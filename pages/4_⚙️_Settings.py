"""Set daily targets."""
import streamlit as st

import db

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="centered")
db.init_db()

st.title("⚙️ Settings")

protein_target = float(db.get_setting("protein_target_g", "160"))
calorie_target = float(db.get_setting("calorie_target", "2400"))

with st.form("settings_form"):
    new_protein = st.number_input(
        "Daily protein target (g)", min_value=0.0, value=protein_target, step=5.0,
        help="Common lifting guidance is roughly 1.6–2.2g per kg of bodyweight.",
    )
    new_calories = st.number_input(
        "Daily calorie target (kcal)", min_value=0.0, value=calorie_target, step=50.0,
    )
    if st.form_submit_button("Save", type="primary"):
        db.set_setting("protein_target_g", new_protein)
        db.set_setting("calorie_target", new_calories)
        st.success("Saved.")
        st.rerun()

st.divider()
st.caption(
    "These targets drive the progress bars on the Dashboard and Weekly Plan pages."
)
