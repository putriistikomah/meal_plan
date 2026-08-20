# 🍗 High-Protein Meal Planner

A Streamlit dashboard for planning a week of high-protein meals: build a recipe
library, assign recipes to days, track protein/calories against your targets,
and get an auto-generated grocery list.

## Pages

- **Dashboard** (`app.py`) — weekly protein/calorie totals vs. targets, charts
- **🍳 Recipes** — add/edit/delete recipes (protein, calories, ingredients)
- **📅 Weekly Plan** — assign recipes to day + meal slot, see daily totals
- **🛒 Grocery List** — ingredients from the whole week, aggregated, grouped
  by category, with a checklist
- **⚙️ Settings** — daily protein/calorie targets

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501.

## Deploy to Streamlit Community Cloud (free public URL)

1. Push this folder to a **GitHub repo** (see commands below).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, pick this repo/branch, set the main file to `app.py`.
4. Deploy. You'll get a URL like `https://<something>.streamlit.app` you can
   open from your phone, gym, anywhere.

```bash
git init
git add .
git commit -m "Initial meal planner"
git branch -M main
git remote add origin <your-empty-github-repo-url>
git push -u origin main
```

## ⚠️ Data persistence note

Data (recipes, plan, targets) is stored in a local SQLite file
(`meal_planner.db`), which is **not** committed to git. That's fine for local
use, but on Streamlit Community Cloud the filesystem is not guaranteed to
persist — a redeploy or a restart after the app sleeps from inactivity can
reset it back to the starter recipes.

For a hosted app you rely on daily, consider swapping the storage in `db.py`
for a free hosted database later (e.g. Supabase/Postgres, or Turso for
SQLite) — the rest of the app (pages, logic) won't need to change, only the
connection in `db.py`. Ask if you want this wired up.
