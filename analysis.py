"""
Core analysis functions for the Nordic Health Data Copilot.

R -> pandas cheat sheet (for reference while reading this file):
  filter(df, x == y)          ->  df[df.x == y]
  group_by(df, x) %>% summarize(s = sum(y))  ->  df.groupby('x')['y'].sum()
  arrange(df, x)               ->  df.sort_values('x')
  mutate(df, z = x + y)        ->  df['z'] = df['x'] + df['y']
  df %>% select(x, y)          ->  df[['x', 'y']]
"""

import pandas as pd

DATA_DIR = "data"


def load_data():
    """Load all three CSVs into a dict of DataFrames (like reading 3 .Rds/.csv into a list)."""
    country_year = pd.read_csv(f"{DATA_DIR}/tb_country_year.csv")
    age_group = pd.read_csv(f"{DATA_DIR}/tb_age_group.csv")
    eu_totals = pd.read_csv(f"{DATA_DIR}/tb_eu_totals.csv")
    return country_year, age_group, eu_totals


def cases_by_year(eu_totals: pd.DataFrame) -> pd.DataFrame:
    """EU/EEA total cases and rate per year. Already aggregated at source."""
    return eu_totals.sort_values("Year")


def cases_by_country(country_year: pd.DataFrame, year: int | None = None) -> pd.DataFrame:
    """
    Total cases and average notification rate by country.
    Equivalent R: df %>% filter(Year == year) %>% group_by(Country) %>%
                  summarize(Cases = sum(Cases), Rate = mean(NotificationRate_per_100k))
    """
    df = country_year.copy()
    if year is not None:
        df = df[df["Year"] == year]
    result = (
        df.groupby("Country", as_index=False)
        .agg(Cases=("Cases", "sum"), NotificationRate_per_100k=("NotificationRate_per_100k", "mean"))
        .sort_values("NotificationRate_per_100k", ascending=False)
    )
    return result


def cases_by_age_group(age_group: pd.DataFrame, year: int | None = None, country: str | None = None) -> pd.DataFrame:
    """
    Total cases and average rate by age group, optionally filtered by year/country.
    """
    df = age_group.copy()
    if year is not None:
        df = df[df["Year"] == year]
    if country is not None:
        df = df[df["Country"] == country]
    result = (
        df.groupby("AgeGroup", as_index=False)
        .agg(Cases=("Cases", "sum"), NotificationRate_per_100k=("NotificationRate_per_100k", "mean"))
    )
    # Keep age groups in natural order rather than alphabetical
    order = ["0-4", "5-14", "15-24", "25-44", "45-64", "65+"]
    result["AgeGroup"] = pd.Categorical(result["AgeGroup"], categories=order, ordered=True)
    return result.sort_values("AgeGroup")


def trend_over_time(country_year: pd.DataFrame, country: str | None = None) -> pd.DataFrame:
    """Cases/rate over time, optionally for one country, otherwise EU/EEA-wide sum."""
    df = country_year.copy()
    if country is not None:
        df = df[df["Country"] == country]
        return df.sort_values("Year")[["Year", "Cases", "NotificationRate_per_100k"]]
    result = df.groupby("Year", as_index=False).agg(
        Cases=("Cases", "sum"), NotificationRate_per_100k=("NotificationRate_per_100k", "mean")
    )
    return result.sort_values("Year")


def highest_group(df: pd.DataFrame, group_col: str, value_col: str = "NotificationRate_per_100k"):
    """Return the row with the max value in value_col -- e.g. 'which age group has highest incidence'."""
    return df.loc[df[value_col].idxmax()]


def pct_change(df: pd.DataFrame, value_col: str, year_col: str = "Year"):
    """Percent change between first and last year in a time-ordered dataframe."""
    df = df.sort_values(year_col)
    first, last = df[value_col].iloc[0], df[value_col].iloc[-1]
    if first == 0:
        return None
    return round((last - first) / first * 100, 1)
