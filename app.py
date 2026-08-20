"""High-Protein Meal Planner — Home / Dashboard.

Run locally with:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

import db

st.set_page_config(page_title="Meal Planner", page_icon="🍗", layout="wide")
db.init_db()

st.title("🍗 High-Protein Meal Planner")
st.caption("Plan your week, hit your protein target, and generate a grocery list — all in one place.")

protein_target = float(db.get_setting("protein_target_g", "160"))
calorie_target = float(db.get_setting("calorie_target", "2400"))

plan = db.get_plan()

if not plan:
    st.info(
        "No meals planned yet. Head to **📅 Weekly Plan** in the sidebar to assign recipes "
        "to your days, or add your own recipes first in **🍳 Recipes**."
    )
else:
    df = pd.DataFrame(plan)
    df["total_protein"] = df["protein_g"] * df["plan_servings"]
    df["total_calories"] = df["calories"] * df["plan_servings"]

    daily = df.groupby("day", as_index=False)[["total_protein", "total_calories"]].sum()
    daily["day"] = pd.Categorical(daily["day"], categories=db.DAYS, ordered=True)
    daily = daily.sort_values("day")

    col1, col2, col3 = st.columns(3)
    col1.metric("Weekly avg. protein/day", f"{daily['total_protein'].mean():.0f} g",
                 f"target {protein_target:.0f} g")
    col2.metric("Weekly avg. calories/day", f"{daily['total_calories'].mean():.0f} kcal",
                 f"target {calorie_target:.0f} kcal")
    days_hit = (daily["total_protein"] >= protein_target).sum()
    col3.metric("Days hitting protein target", f"{days_hit} / {len(daily)}")

    st.subheader("Protein per day vs. target")
    chart_df = daily.set_index("day")[["total_protein"]].rename(
        columns={"total_protein": "Protein (g)"}
    )
    chart_df["Target (g)"] = protein_target
    st.bar_chart(chart_df)

    st.subheader("Calories per day vs. target")
    chart_df2 = daily.set_index("day")[["total_calories"]].rename(
        columns={"total_calories": "Calories"}
    )
    chart_df2["Target"] = calorie_target
    st.bar_chart(chart_df2)

    with st.expander("See full weekly plan table"):
        show = df[["day", "slot", "name", "plan_servings", "total_protein", "total_calories"]]
        show = show.rename(columns={
            "day": "Day", "slot": "Slot", "name": "Recipe",
            "plan_servings": "Servings", "total_protein": "Protein (g)",
            "total_calories": "Calories",
        })
        st.dataframe(show, use_container_width=True, hide_index=True)

st.divider()
st.markdown(
    "**Pages:** 🍳 Recipes (build your library) · 📅 Weekly Plan (assign meals) · "
    "🛒 Grocery List (auto-generated) · ⚙️ Settings (targets)"
)
