"""
Nordic Health Data Copilot — Streamlit app.

Run with:
    streamlit run app.py
"""

import pandas as pd
import streamlit as st
import plotly.express as px

from analysis import (
    load_data,
    cases_by_year,
    cases_by_country,
    cases_by_age_group,
    trend_over_time,
)
from explain_llm import explain_trend, explain_comparison, explain_age_pattern, using_live_ai

st.set_page_config(page_title="Nordic Health Data Copilot", page_icon="🩺", layout="wide")


@st.cache_data
def load_measles_data():
    eu_totals = pd.read_csv("data/measles_eu_totals.csv")
    country_year = pd.read_csv("data/measles_country_year.csv")
    age_group = pd.read_csv("data/measles_age_group.csv")
    return country_year, age_group, eu_totals


# ---------- Sidebar ----------
st.sidebar.title("🩺 Health Data Copilot")

disease = st.sidebar.selectbox("Disease", ["Tuberculosis", "Measles"])

if using_live_ai():
    st.sidebar.success("🤖 Live AI explanations (Claude API) active")
else:
    st.sidebar.info("🤖 Using rule-based explanations (no API key set)")

st.sidebar.markdown("Explore EU/EEA disease surveillance data.")

if disease == "Tuberculosis":
    country_year, age_group, eu_totals = load_data()
    query_options = [
        "Trend over time (EU/EEA)",
        "Compare countries",
        "Which age group is most affected?",
        "Single country trend",
    ]
else:
    country_year, age_group, eu_totals = load_measles_data()
    query_options = [
        "Trend over time (EU/EEA)",
        "Which age group is most affected?",
    ]
    st.sidebar.caption(
        "Note: measles case counts dropped sharply after 2020 vaccination/COVID effects, "
        "so country-level and multi-year age data is sparser than for TB — only 2022 country "
        "figures and 2019 age figures are available from published reports."
    )

all_countries = sorted(country_year["Country"].unique()) if "Country" in country_year.columns else []
all_years = sorted(country_year["Year"].unique()) if "Year" in country_year.columns else sorted(eu_totals["Year"].unique())

query_type = st.sidebar.selectbox("What do you want to explore?", query_options)

st.sidebar.markdown("---")
st.sidebar.markdown("**Example questions this answers:**")
st.sidebar.markdown(
    "- How has TB incidence changed over time?\n"
    "- Which country has the highest TB notification rate?\n"
    "- Which age group has the highest TB incidence?\n"
    "- How is Sweden trending compared to the EU/EEA average?"
)

st.title("Nordic Health Data Copilot")
st.caption(f"AI-assisted exploration of EU/EEA {disease.lower()} surveillance data, sourced from ECDC Annual Epidemiological Reports.")

# ---------- Main content per query type ----------
if query_type == "Trend over time (EU/EEA)":
    st.subheader(f"{disease} notification rate across the EU/EEA")
    df = cases_by_year(eu_totals)

    fig = px.line(
        df, x="Year", y="EU_EEA_Rate_per_100k", markers=True,
        labels={"EU_EEA_Rate_per_100k": "Rate per 100,000"},
        title=f"EU/EEA {disease.lower()} notification rate by year",
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"Latest rate ({int(df['Year'].iloc[-1])})", f"{df['EU_EEA_Rate_per_100k'].iloc[-1]:.2f} / 100k")
    with col2:
        st.metric(f"Latest total cases ({int(df['Year'].iloc[-1])})", f"{df['EU_EEA_Cases'].iloc[-1]:,}")

    st.markdown("#### 🤖 AI Explanation")
    st.info(explain_trend(df, "EU_EEA_Rate_per_100k", f"the EU/EEA {disease.lower()} notification rate"))

elif query_type == "Compare countries":
    st.subheader(f"{disease} notification rate by country")
    year = st.selectbox("Year", all_years, index=len(all_years) - 1)
    df = cases_by_country(country_year, year=year)

    fig = px.bar(
        df, x="Country", y="NotificationRate_per_100k", color="NotificationRate_per_100k",
        labels={"NotificationRate_per_100k": "Rate per 100,000"},
        title=f"{disease} notification rate by country, {year}",
        color_continuous_scale="Reds",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### 🤖 AI Explanation")
    st.info(explain_comparison(df, "Country", "NotificationRate_per_100k", f"{disease.lower()} notification rate"))

elif query_type == "Which age group is most affected?":
    st.subheader(f"{disease} notification rate by age group")

    if disease == "Tuberculosis":
        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox("Year", all_years, index=len(all_years) - 1)
        with col2:
            country = st.selectbox("Country (or all)", ["All countries"] + all_countries)
        country_filter = None if country == "All countries" else country
        df = cases_by_age_group(age_group, year=year, country=country_filter)
        title_suffix = f", {year}" + (f" — {country}" if country_filter else " — EU/EEA")
    else:
        # Measles age data is a single EU/EEA-wide snapshot (2019), no country breakdown available
        df = age_group.copy()
        st.caption("Showing the most recent published EU/EEA-wide age breakdown (2019).")
        title_suffix = ", 2019 — EU/EEA"

    fig = px.bar(
        df, x="AgeGroup", y="NotificationRate_per_100k",
        labels={"NotificationRate_per_100k": "Rate per 100,000", "AgeGroup": "Age group"},
        title=f"{disease} notification rate by age group{title_suffix}",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### 🤖 AI Explanation")
    st.info(explain_age_pattern(df))

elif query_type == "Single country trend":
    st.subheader("Country-level trend over time")
    country = st.selectbox("Country", all_countries, index=all_countries.index("Sweden") if "Sweden" in all_countries else 0)
    df = trend_over_time(country_year, country=country)

    fig = px.line(
        df, x="Year", y="NotificationRate_per_100k", markers=True,
        labels={"NotificationRate_per_100k": "Rate per 100,000"},
        title=f"{disease} notification rate in {country}",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### 🤖 AI Explanation")
    st.info(explain_trend(df, "NotificationRate_per_100k", f"the {disease.lower()} notification rate in {country}"))

st.markdown("---")
st.caption(
    "Data provided by ECDC based on data reported by EU/EEA Member States, "
    "compiled from ECDC Annual Epidemiological Reports. "
    "See README for full data provenance notes, including which figures are modeled/estimated."
)
