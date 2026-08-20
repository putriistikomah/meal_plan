"""SQLite persistence layer for the meal planner."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "meal_planner.db"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SLOTS = ["Breakfast", "Lunch", "Dinner", "Snack"]

DEFAULT_SETTINGS = {
    "protein_target_g": "160",
    "calorie_target": "2400",
}

STARTER_RECIPES = [
    {
        "name": "Greek Yogurt Protein Bowl",
        "meal_type": "Breakfast",
        "protein_g": 35, "calories": 380, "carbs_g": 40, "fat_g": 8,
        "servings": 1, "source_url": "",
        "ingredients": ["300g Greek yogurt (0% or 2%)", "30g whey protein powder",
                        "40g granola", "100g mixed berries", "10g honey"],
    },
    {
        "name": "Grilled Chicken & Rice Bowl",
        "meal_type": "Lunch",
        "protein_g": 48, "calories": 620, "carbs_g": 60, "fat_g": 14,
        "servings": 1, "source_url": "",
        "ingredients": ["200g chicken breast", "150g cooked white rice",
                        "100g broccoli", "1 tbsp olive oil", "soy sauce to taste"],
    },
    {
        "name": "Salmon, Sweet Potato & Greens",
        "meal_type": "Dinner",
        "protein_g": 42, "calories": 580, "carbs_g": 45, "fat_g": 22,
        "servings": 1, "source_url": "",
        "ingredients": ["200g salmon fillet", "200g sweet potato", "100g spinach",
                        "1 tbsp olive oil", "lemon wedge"],
    },
    {
        "name": "Cottage Cheese & Fruit",
        "meal_type": "Snack",
        "protein_g": 24, "calories": 220, "carbs_g": 20, "fat_g": 5,
        "servings": 1, "source_url": "",
        "ingredients": ["200g cottage cheese", "1 banana"],
    },
    {
        "name": "Protein Shake",
        "meal_type": "Snack",
        "protein_g": 30, "calories": 200, "carbs_g": 8, "fat_g": 3,
        "servings": 1, "source_url": "",
        "ingredients": ["1 scoop whey protein powder", "250ml milk or water"],
    },
    {
        "name": "Beef & Egg Scramble",
        "meal_type": "Breakfast",
        "protein_g": 40, "calories": 520, "carbs_g": 10, "fat_g": 30,
        "servings": 1, "source_url": "",
        "ingredients": ["150g lean ground beef", "3 eggs", "50g bell pepper",
                        "30g cheddar cheese"],
    },
]


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                protein_g REAL NOT NULL DEFAULT 0,
                calories REAL NOT NULL DEFAULT 0,
                carbs_g REAL NOT NULL DEFAULT 0,
                fat_g REAL NOT NULL DEFAULT 0,
                servings REAL NOT NULL DEFAULT 1,
                source_url TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                line TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                slot TEXT NOT NULL,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                servings REAL NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS grocery_checked (
                item_key TEXT PRIMARY KEY
            );
            """
        )
        # seed settings
        for k, v in DEFAULT_SETTINGS.items():
            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v)
            )
        # seed starter recipes only if table is empty
        count = conn.execute("SELECT COUNT(*) AS c FROM recipes").fetchone()["c"]
        if count == 0:
            for r in STARTER_RECIPES:
                cur = conn.execute(
                    """INSERT INTO recipes
                       (name, meal_type, protein_g, calories, carbs_g, fat_g, servings, source_url)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (r["name"], r["meal_type"], r["protein_g"], r["calories"],
                     r["carbs_g"], r["fat_g"], r["servings"], r["source_url"]),
                )
                recipe_id = cur.lastrowid
                for line in r["ingredients"]:
                    conn.execute(
                        "INSERT INTO ingredients (recipe_id, line) VALUES (?, ?)",
                        (recipe_id, line),
                    )


# ---------- recipes ----------

def add_recipe(name, meal_type, protein_g, calories, carbs_g, fat_g, servings, source_url, ingredient_lines):
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO recipes
               (name, meal_type, protein_g, calories, carbs_g, fat_g, servings, source_url)
               VALUES (?,?,?,?,?,?,?,?)""",
            (name, meal_type, protein_g, calories, carbs_g, fat_g, servings, source_url),
        )
        recipe_id = cur.lastrowid
        for line in ingredient_lines:
            line = line.strip()
            if line:
                conn.execute(
                    "INSERT INTO ingredients (recipe_id, line) VALUES (?, ?)",
                    (recipe_id, line),
                )
        return recipe_id


def update_recipe(recipe_id, name, meal_type, protein_g, calories, carbs_g, fat_g, servings, source_url, ingredient_lines):
    with get_conn() as conn:
        conn.execute(
            """UPDATE recipes SET name=?, meal_type=?, protein_g=?, calories=?,
               carbs_g=?, fat_g=?, servings=?, source_url=? WHERE id=?""",
            (name, meal_type, protein_g, calories, carbs_g, fat_g, servings, source_url, recipe_id),
        )
        conn.execute("DELETE FROM ingredients WHERE recipe_id=?", (recipe_id,))
        for line in ingredient_lines:
            line = line.strip()
            if line:
                conn.execute(
                    "INSERT INTO ingredients (recipe_id, line) VALUES (?, ?)",
                    (recipe_id, line),
                )


def delete_recipe(recipe_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
        conn.execute("DELETE FROM plan WHERE recipe_id=?", (recipe_id,))


def get_recipes():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM recipes ORDER BY meal_type, name").fetchall()
        return [dict(r) for r in rows]


def get_recipe(recipe_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,)).fetchone()
        if not row:
            return None
        recipe = dict(row)
        ing = conn.execute(
            "SELECT line FROM ingredients WHERE recipe_id=? ORDER BY id", (recipe_id,)
        ).fetchall()
        recipe["ingredients"] = [i["line"] for i in ing]
        return recipe


# ---------- plan ----------

def add_plan_entry(day, slot, recipe_id, servings=1):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO plan (day, slot, recipe_id, servings) VALUES (?,?,?,?)",
            (day, slot, recipe_id, servings),
        )


def remove_plan_entry(entry_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM plan WHERE id=?", (entry_id,))


def get_plan():
    """Returns list of plan rows joined with recipe info."""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT p.id AS plan_id, p.day, p.slot, p.servings AS plan_servings,
                      r.id AS recipe_id, r.name, r.meal_type, r.protein_g, r.calories,
                      r.carbs_g, r.fat_g, r.servings AS recipe_servings
               FROM plan p JOIN recipes r ON p.recipe_id = r.id
               ORDER BY CASE p.day
                   WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
                   WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6
                   WHEN 'Sunday' THEN 7 END,
               CASE p.slot
                   WHEN 'Breakfast' THEN 1 WHEN 'Lunch' THEN 2 WHEN 'Dinner' THEN 3
                   WHEN 'Snack' THEN 4 END"""
        ).fetchall()
        return [dict(r) for r in rows]


def clear_plan():
    with get_conn() as conn:
        conn.execute("DELETE FROM plan")


def get_ingredients_for_recipe(recipe_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT line FROM ingredients WHERE recipe_id=?", (recipe_id,)
        ).fetchall()
        return [r["line"] for r in rows]


# ---------- settings ----------

def get_setting(key, default=None):
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key, value):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )


# ---------- grocery checklist state ----------

def get_checked_items():
    with get_conn() as conn:
        rows = conn.execute("SELECT item_key FROM grocery_checked").fetchall()
        return {r["item_key"] for r in rows}


def set_item_checked(item_key, checked):
    with get_conn() as conn:
        if checked:
            conn.execute(
                "INSERT OR IGNORE INTO grocery_checked (item_key) VALUES (?)", (item_key,)
            )
        else:
            conn.execute("DELETE FROM grocery_checked WHERE item_key=?", (item_key,))


def clear_checked_items():
    with get_conn() as conn:
        conn.execute("DELETE FROM grocery_checked")
