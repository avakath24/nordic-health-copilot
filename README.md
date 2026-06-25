# 🩺 Nordic Health Data Copilot (MVP)

An AI-assisted analytics tool for exploring EU/EEA disease surveillance data (Tuberculosis and Measles). Ask a question about disease trends, get an interactive chart and a plain-language explanation — generated live by Claude when an API key is set, or by a rule-based fallback engine otherwise. Built as a portfolio project demonstrating healthcare analytics, Python data work, and practical AI integration.

**Live demo:** *(add your Streamlit Cloud link here after deploying)*
**Screenshot:**

*(add a screenshot here — run the app locally, take a screenshot, save it as `screenshot.png` in this folder, then add: `![App screenshot](screenshot.png)`)*

---

## What it does

- 📈 **Trend analysis** — How has TB/measles notification rate changed across the EU/EEA over time?
- 🌍 **Country comparison** — Which country has the highest TB notification rate, and how do they compare? *(TB only — see data note below)*
- 👥 **Age-group breakdown** — Which age group is most affected, and does the pattern suggest recent transmission, reactivation of latent infection, or vaccination gaps?
- 🇸🇪 **Single-country deep dive** — How is a specific country (e.g. Sweden) trending against the wider region? *(TB only)*
- 🦠 **Multi-disease** — Switch between Tuberculosis and Measles datasets from the sidebar.
- 🤖 **AI explanation, with graceful fallback** — Every chart comes with a short natural-language summary. If an Anthropic API key is configured, this is generated live by Claude; if not, it automatically falls back to a rule-based explanation engine, so the app never breaks.

## Tech stack

- **Python** + **pandas** for data wrangling and aggregation
- **Streamlit** for the interactive web interface
- **Plotly** for charts
- **Anthropic API** (Claude) for live natural-language explanations, with a **rule-based fallback engine** (`explain.py`) used automatically when no API key is set — this separation means the explanation layer can be swapped or upgraded without touching the analysis/chart code

## Setting up live AI explanations (optional)

The app works perfectly well with zero setup (rule-based explanations). To enable real Claude-generated explanations:

1. Go to [console.anthropic.com](https://console.anthropic.com/), sign up, then **Settings → API Keys → Create Key**. New accounts get a small amount of free credit.
2. In the project root, create a file named `.env` containing:
   ```
   ANTHROPIC_API_KEY=your-key-here
   ```
3. Run the app as normal — the sidebar will show "🤖 Live AI explanations active" once it detects the key.

If deploying on Streamlit Cloud, set the key via the app's **Secrets** manager instead of a `.env` file (Settings → Secrets, same `ANTHROPIC_API_KEY = "..."` format).

## Data source and an honest note on provenance

This project uses **real published figures** from ECDC's official Annual Epidemiological Reports for **Tuberculosis (2018–2022)** and **Measles (2018–2022)** — EU/EEA-wide case counts and notification rates are taken directly from those reports.

One nuance worth being upfront about (and a good thing to mention if asked in an interview): ECDC's [Surveillance Atlas](https://atlas.ecdc.europa.eu/public/) is an interactive tool without a public bulk-CSV export, and raw case-level TESSy data requires a formal data access request to ECDC. So rather than scraping an interactive dashboard, this project compiles the **published aggregate statistics** from ECDC's official reports into clean, analysis-ready datasets:

- **Tuberculosis**: full 2018–2022 country-level rates and an EU/EEA-wide age-distribution pattern, both from real published figures; country-level age-group splits are modeled proportionally from the EU/EEA-wide pattern since per-country age breakdowns aren't published at that resolution (documented in `data/build_dataset.py`).
- **Measles**: EU/EEA yearly rates are real for all 5 years; case counts are real for 2019 and 2022 and estimated from rate × population for 2018/2020/2021 (flagged in a `Cases_estimated` column); country-level figures are a real but single-year (2022) snapshot, since most countries reported zero cases in other years; the age pattern uses real 2019 figures for `<1` and `1-4` age groups, with older groups modeled on the documented decreasing trend (documented in `data/build_measles_dataset.py`).

> Data provided by ECDC based on data reported by EU/EEA Member States. Source: ECDC Tuberculosis and Measles Annual Epidemiological Reports, 2018–2022.

## Project structure

```
nordic-health-copilot/
├── app.py                  # Streamlit application (main entry point)
├── analysis.py              # Data loading + pandas analysis functions (TB)
├── explain.py                # Rule-based natural-language explanation generator (fallback)
├── explain_llm.py            # Live Claude API explanation layer, falls back to explain.py
├── requirements.txt
├── data/
│   ├── build_dataset.py          # Builds the TB CSVs from published ECDC figures
│   ├── build_measles_dataset.py  # Builds the measles CSVs from published ECDC figures
│   ├── tb_country_year.csv
│   ├── tb_age_group.csv
│   ├── tb_eu_totals.csv
│   ├── measles_country_year.csv
│   ├── measles_age_group.csv
│   └── measles_eu_totals.csv
└── README.md
```

## Running it locally

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/nordic-health-copilot.git
cd nordic-health-copilot

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate       # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) rebuild the datasets from scratch
python3 data/build_dataset.py
python3 data/build_measles_dataset.py

# 5. (Optional) enable live AI explanations — see "Setting up live AI explanations" above

# 6. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Possible extensions (v3 ideas)

- Add more diseases (COVID-19, mumps) using the same dataset-building pattern.
- Add a map view (Plotly choropleth) for geographic comparison.
- Cache LLM responses (e.g. with `@st.cache_data`) to avoid repeat API calls for the same chart.
- Stream the LLM response token-by-token for a more "live" feel in the UI.

## Why this project

Built as a focused demonstration of:
- End-to-end data pipeline thinking (sourcing → cleaning → analysis → visualization → communication)
- Healthcare/epidemiological analytics literacy
- Practical AI-assisted insight generation
- Product framing — not just a model, but a usable interactive tool

---
*This is an educational/portfolio project and is not intended for clinical or policy decision-making.*
