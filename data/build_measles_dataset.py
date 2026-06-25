"""
Builds the measles dataset, structured to match the TB dataset, so the app
can support multiple diseases through the same pipeline.

Source: ECDC Measles Annual Epidemiological Reports (2019, 2022, 2023).
https://www.ecdc.europa.eu/en/measles/surveillance-and-disease-data

DATA PROVENANCE NOTE:
- EU/EEA-wide rates per year (2018-2022) are real published figures.
- 2019 and 2022 case counts are real published figures (13,200 and 127).
- 2018, 2020, 2021 case counts are ESTIMATED by applying the published rate
  to the approximate EU/EEA population (~447 million), since exact case
  counts for those years weren't in the report excerpts used here. This is
  clearly flagged in the Cases_estimated column.
- Country-level 2022 rates for Belgium, Poland, Romania, Sweden are real
  published figures (the only ones explicitly broken out in the 2022 report,
  since only 15 of 30 countries reported any cases that year).
- The age-group pattern (highest in <1yr, decreasing with age) reflects the
  real reported pattern; exact rates for groups beyond <1yr and 1-4yr are
  modeled to follow a realistic decreasing curve since the source report
  excerpt only gave those two groups precisely.
"""

import pandas as pd

EU_POPULATION_MILLIONS = 447  # approx EU/EEA population

# Real published EU/EEA notification rate per 1,000,000 population
yearly_rate_per_million = {
    2018: 34.4,
    2019: 25.4,
    2020: 4.3,
    2021: 0.1,
    2022: 0.3,
}

# Real published case counts (where available)
known_cases = {
    2019: 13200,
    2022: 127,
}

# Real published 2022 country rates (per 1,000,000) -- only a handful of
# countries reported notable case numbers that year
country_rates_2022 = {
    "Belgium": 1.6,
    "Poland": 0.7,
    "Romania": 0.5,
    "Sweden": 0.5,
}

# Real reported age pattern (rate per 1,000,000), from the 2019 report,
# the most recent year with a clear age breakdown in the excerpts used here
age_group_rate_per_million_2019 = {
    "<1": 273.2,
    "1-4": 100.6,
    "5-14": 35.0,   # modeled: decreasing trend continues
    "15-19": 18.0,  # modeled
    "20+": 14.0,    # modeled, consistent with "adults 20+ accounted for 49% of cases" in 2019
}


def build_eu_totals_table() -> pd.DataFrame:
    rows = []
    for year, rate in yearly_rate_per_million.items():
        rate_per_100k = rate / 10
        if year in known_cases:
            cases = known_cases[year]
            estimated = False
        else:
            cases = round(rate * EU_POPULATION_MILLIONS)
            estimated = True
        rows.append({
            "Year": year,
            "EU_EEA_Cases": cases,
            "EU_EEA_Rate_per_100k": round(rate_per_100k, 2),
            "Cases_estimated": estimated,
        })
    return pd.DataFrame(rows)


def build_country_year_table() -> pd.DataFrame:
    # Only 2022 has explicit country-level figures in our sources; presented
    # honestly as a single-year snapshot rather than inventing other years.
    rows = []
    for country, rate in country_rates_2022.items():
        rows.append({
            "Country": country,
            "Year": 2022,
            "NotificationRate_per_100k": round(rate / 10, 3),
            "Cases": None,  # not precisely published at country level
        })
    return pd.DataFrame(rows)


def build_age_group_table() -> pd.DataFrame:
    rows = []
    for age_group, rate in age_group_rate_per_million_2019.items():
        rows.append({
            "Year": 2019,
            "AgeGroup": age_group,
            "NotificationRate_per_100k": round(rate / 10, 2),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    eu_totals = build_eu_totals_table()
    country_year = build_country_year_table()
    age_group = build_age_group_table()

    eu_totals.to_csv("/home/claude/nordic-health-copilot/data/measles_eu_totals.csv", index=False)
    country_year.to_csv("/home/claude/nordic-health-copilot/data/measles_country_year.csv", index=False)
    age_group.to_csv("/home/claude/nordic-health-copilot/data/measles_age_group.csv", index=False)

    print("EU totals:\n", eu_totals)
    print("\nCountry 2022:\n", country_year)
    print("\nAge group 2019:\n", age_group)
