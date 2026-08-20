"""Assign recipes to days/slots and track protein against target."""
import streamlit as st

import db

st.set_page_config(page_title="Weekly Plan", page_icon="📅", layout="wide")
db.init_db()

st.title("📅 Weekly Plan")

recipes = db.get_recipes()
protein_target = float(db.get_setting("protein_target_g", "120"))
calorie_target = float(db.get_setting("calorie_target", "2400"))

if not recipes:
    st.warning("Add some recipes first on the **🍳 Recipes** page.")
    st.stop()

recipe_by_id = {r["id"]: r for r in recipes}

top1, top2 = st.columns([3, 1])
top1.caption(f"Target: {protein_target:.0f}g protein / {calorie_target:.0f} kcal per day.")
if top2.button("🗑️ Clear entire week"):
    db.clear_plan()
    st.rerun()

plan = db.get_plan()
plan_by_day = {d: [] for d in db.DAYS}
for entry in plan:
    plan_by_day[entry["day"]].append(entry)

for day in db.DAYS:
    entries = plan_by_day[day]
    day_protein = sum(e["protein_g"] * e["plan_servings"] for e in entries)
    day_calories = sum(e["calories"] * e["plan_servings"] for e in entries)
    pct = min(day_protein / protein_target, 1.0) if protein_target else 0

    status = "✅" if day_protein >= protein_target else "⏳"
    with st.expander(
        f"{status} **{day}** — {day_protein:.0f}g protein / {day_calories:.0f} kcal",
        expanded=False,
    ):
        st.progress(pct, text=f"{day_protein:.0f} / {protein_target:.0f} g protein")

        if entries:
            for e in entries:
                c1, c2, c3, c4 = st.columns([2, 3, 2, 1])
                c1.write(f"**{e['slot']}**")
                c2.write(f"{e['name']}")
                c3.write(f"{e['protein_g'] * e['plan_servings']:.0f}g protein "
                          f"· {e['calories'] * e['plan_servings']:.0f} kcal "
                          f"({e['plan_servings']:g}x)")
                if c4.button("✕", key=f"rm_{e['plan_id']}"):
                    db.remove_plan_entry(e["plan_id"])
                    st.rerun()
        else:
            st.caption("Nothing planned yet.")

        st.markdown("**Add a meal:**")
        with st.form(f"add_form_{day}", clear_on_submit=True):
            fc1, fc2, fc3, fc4 = st.columns([1.5, 3, 1, 1])
            slot = fc1.selectbox("Slot", db.SLOTS, key=f"slot_{day}")
            options = [r["id"] for r in recipes]
            labels = {r["id"]: f"{r['name']} ({r['protein_g']:.0f}g protein)" for r in recipes}
            recipe_id = fc2.selectbox(
                "Recipe", options, format_func=lambda rid: labels[rid], key=f"recipe_{day}"
            )
            servings = fc3.number_input("Servings", min_value=0.25, value=1.0,
                                         step=0.25, key=f"servings_{day}")
            add = fc4.form_submit_button("Add")
            if add:
                db.add_plan_entry(day, slot, recipe_id, servings)
                st.rerun()
