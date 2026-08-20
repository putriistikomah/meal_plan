"""Auto-generated, checkable grocery list from the current weekly plan."""
import streamlit as st

import db
from utils import aggregate_ingredients

st.set_page_config(page_title="Grocery List", page_icon="🛒", layout="wide")
db.init_db()

st.title("🛒 Grocery List")
st.caption("Aggregated automatically from everything in your Weekly Plan.")

plan = db.get_plan()

if not plan:
    st.info("Nothing planned yet — go add meals on the **📅 Weekly Plan** page.")
    st.stop()

entries = []
for e in plan:
    lines = db.get_ingredients_for_recipe(e["recipe_id"])
    for line in lines:
        entries.append((line, e["plan_servings"]))

grouped = aggregate_ingredients(entries)
checked = db.get_checked_items()

c1, c2 = st.columns([1, 1])
if c1.button("↺ Reset checklist"):
    db.clear_checked_items()
    st.rerun()

total_items = sum(len(v) for v in grouped.values())
checked_count = sum(1 for cat in grouped.values() for item in cat if item["key"] in checked)
c2.progress(checked_count / total_items if total_items else 0,
            text=f"{checked_count} / {total_items} items checked")

st.divider()

CATEGORY_ORDER = ["Protein", "Produce", "Dairy", "Grains & Starch", "Pantry", "Other"]
for category in CATEGORY_ORDER:
    if category not in grouped:
        continue
    st.subheader(category)
    for item in grouped[category]:
        is_checked = item["key"] in checked
        new_val = st.checkbox(item["display"], value=is_checked, key=f"chk_{item['key']}")
        if new_val != is_checked:
            db.set_item_checked(item["key"], new_val)
            st.rerun()
