"""Manage the recipe library."""
import streamlit as st

import db

st.set_page_config(page_title="Recipes", page_icon="🍳", layout="wide")
db.init_db()

st.title("🍳 Recipe Library")
st.caption("Add every recipe idea you've saved from the internet. One entry, reused every week.")

with st.expander("➕ Add a new recipe", expanded=len(db.get_recipes()) == 0):
    with st.form("add_recipe_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Recipe name*")
        meal_type = c2.selectbox("Meal type*", db.SLOTS)

        c3, c4, c5, c6 = st.columns(4)
        protein_g = c3.number_input("Protein (g)*", min_value=0.0, step=1.0)
        calories = c4.number_input("Calories*", min_value=0.0, step=10.0)
        carbs_g = c5.number_input("Carbs (g)", min_value=0.0, step=1.0)
        fat_g = c6.number_input("Fat (g)", min_value=0.0, step=1.0)

        servings = st.number_input("Servings this recipe makes", min_value=0.25, value=1.0, step=0.25)
        source_url = st.text_input("Source link (optional)")
        ingredients_text = st.text_area(
            "Ingredients (one per line, e.g. `200g chicken breast`)",
            height=140,
            placeholder="200g chicken breast\n150g cooked white rice\n100g broccoli\n1 tbsp olive oil",
        )

        submitted = st.form_submit_button("Add recipe", type="primary")
        if submitted:
            if not name.strip():
                st.error("Recipe name is required.")
            else:
                lines = [l for l in ingredients_text.splitlines() if l.strip()]
                db.add_recipe(name.strip(), meal_type, protein_g, calories, carbs_g,
                               fat_g, servings, source_url.strip(), lines)
                st.success(f"Added '{name}'.")
                st.rerun()

st.divider()
st.subheader("Your recipes")

recipes = db.get_recipes()
if not recipes:
    st.info("No recipes yet — add one above.")
else:
    filter_type = st.selectbox("Filter by meal type", ["All"] + db.SLOTS)
    for r in recipes:
        if filter_type != "All" and r["meal_type"] != filter_type:
            continue
        with st.expander(f"{r['name']}  ·  {r['meal_type']}  ·  {r['protein_g']:.0f}g protein"):
            full = db.get_recipe(r["id"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Protein", f"{r['protein_g']:.0f} g")
            c2.metric("Calories", f"{r['calories']:.0f}")
            c3.metric("Servings", f"{r['servings']:g}")
            st.write(f"Carbs: {r['carbs_g']:.0f} g · Fat: {r['fat_g']:.0f} g")
            if r["source_url"]:
                st.markdown(f"[Source]({r['source_url']})")
            st.markdown("**Ingredients:**")
            for line in full["ingredients"]:
                st.write(f"- {line}")

            colA, colB = st.columns([1, 1])
            edit_key = f"editing_{r['id']}"
            if colA.button("✏️ Edit", key=f"edit_btn_{r['id']}"):
                st.session_state[edit_key] = not st.session_state.get(edit_key, False)
            if colB.button("🗑️ Delete", key=f"del_{r['id']}"):
                db.delete_recipe(r["id"])
                st.rerun()

            if st.session_state.get(edit_key):
                with st.form(f"edit_form_{r['id']}"):
                    e1, e2 = st.columns(2)
                    ename = e1.text_input("Recipe name*", value=full["name"])
                    emeal = e2.selectbox("Meal type*", db.SLOTS,
                                          index=db.SLOTS.index(full["meal_type"]))
                    e3, e4, e5, e6 = st.columns(4)
                    eprotein = e3.number_input("Protein (g)*", min_value=0.0,
                                                value=float(full["protein_g"]), step=1.0)
                    ecal = e4.number_input("Calories*", min_value=0.0,
                                            value=float(full["calories"]), step=10.0)
                    ecarb = e5.number_input("Carbs (g)", min_value=0.0,
                                             value=float(full["carbs_g"]), step=1.0)
                    efat = e6.number_input("Fat (g)", min_value=0.0,
                                            value=float(full["fat_g"]), step=1.0)
                    eservings = st.number_input("Servings", min_value=0.25,
                                                 value=float(full["servings"]), step=0.25)
                    esource = st.text_input("Source link", value=full["source_url"] or "")
                    eing = st.text_area("Ingredients (one per line)",
                                         value="\n".join(full["ingredients"]), height=140)
                    if st.form_submit_button("Save changes", type="primary"):
                        lines = [l for l in eing.splitlines() if l.strip()]
                        db.update_recipe(r["id"], ename.strip(), emeal, eprotein, ecal,
                                          ecarb, efat, eservings, esource.strip(), lines)
                        st.session_state[edit_key] = False
                        st.success("Saved.")
                        st.rerun()
