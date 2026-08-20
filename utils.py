"""Ingredient parsing and grocery-list aggregation helpers."""
import re
from collections import defaultdict

CATEGORY_KEYWORDS = {
    "Protein": ["chicken", "beef", "salmon", "fish", "shrimp", "tuna", "turkey",
                "egg", "tofu", "whey", "protein powder", "pork", "steak",
                "cottage cheese", "greek yogurt", "yogurt", "tempeh", "sausage"],
    "Dairy": ["milk", "cheese", "cheddar", "butter", "cream"],
    "Produce": ["broccoli", "spinach", "pepper", "banana", "berries", "berry",
                "apple", "onion", "garlic", "tomato", "sweet potato", "potato",
                "lettuce", "avocado", "lemon", "lime", "carrot", "cucumber",
                "kale", "mushroom"],
    "Grains & Starch": ["rice", "oats", "oatmeal", "bread", "pasta", "granola",
                         "quinoa", "tortilla", "cereal"],
    "Pantry": ["olive oil", "oil", "soy sauce", "honey", "salt", "spice",
               "vinegar", "sauce", "stock", "broth", "flour", "sugar", "nut butter",
               "peanut butter"],
}

# roughly: "200g chicken breast" / "1 tbsp olive oil" / "3 eggs" / "1 banana"
QTY_RE = re.compile(
    r"^\s*(?P<qty>\d+(?:\.\d+)?(?:/\d+)?)\s*(?P<unit>g|kg|ml|l|oz|lb|lbs|tbsp|tsp|cup|cups|scoop|scoops)?\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)


def categorize(ingredient_name: str) -> str:
    lname = ingredient_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in lname for kw in keywords):
            return category
    return "Other"


def parse_ingredient_line(line: str):
    """Returns (qty: float|None, unit: str, name: str)."""
    m = QTY_RE.match(line)
    if not m:
        return None, "", line.strip()
    qty_str = m.group("qty")
    unit = (m.group("unit") or "").lower()
    name = m.group("name").strip()
    try:
        if "/" in qty_str:
            num, den = qty_str.split("/")
            qty = float(num) / float(den)
        else:
            qty = float(qty_str)
    except (ValueError, ZeroDivisionError):
        qty = None
    return qty, unit, name


def aggregate_ingredients(entries):
    """entries: list of (line, servings_multiplier).

    Returns dict: category -> list of dicts {key, display, checked_key}
    Same (name, unit) pairs are summed; otherwise items are listed separately.
    """
    grouped = defaultdict(lambda: defaultdict(float))  # (name, unit) -> qty
    unparsed = defaultdict(list)  # name -> list of raw lines (for items w/o clean qty)

    for line, multiplier in entries:
        qty, unit, name = parse_ingredient_line(line)
        if qty is None:
            unparsed[name.lower()].append(line)
        else:
            grouped[(name.lower(), unit)][name] += qty * multiplier

    by_category = defaultdict(list)

    for (name_key, unit), variants in grouped.items():
        # pick a display name (first seen casing)
        display_name = next(iter(variants))
        total = sum(variants.values())
        qty_str = f"{total:g}{unit}" if unit else f"{total:g}x"
        display = f"{qty_str} {display_name}"
        category = categorize(display_name)
        item_key = f"{name_key}|{unit}"
        by_category[category].append({"key": item_key, "display": display})

    for name_key, lines in unparsed.items():
        display_name = lines[0]
        category = categorize(display_name)
        if len(lines) > 1:
            display = f"{display_name} (x{len(lines)})"
        else:
            display = display_name
        item_key = f"raw|{name_key}|{len(lines)}"
        by_category[category].append({"key": item_key, "display": display})

    # sort items within each category alphabetically
    for cat in by_category:
        by_category[cat].sort(key=lambda x: x["display"].lower())

    return dict(by_category)
