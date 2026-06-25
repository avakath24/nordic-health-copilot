"""
Rule-based natural-language explanation generator.

This plays the role of the "LLM explanation layer" in the project plan, but
without needing an API key. It looks at the summary statistics (same numbers
that drive the chart) and writes a short, plain-language interpretation.

Upgrade path (mentioned in README): swap `explain_trend()` / `explain_comparison()`
internals for a real API call to Claude/GPT, passing the same summary stats in
the prompt instead of hardcoding sentence templates. The function signatures
would not need to change, which is a nice design point to bring up in an
interview ("I separated the analysis from the explanation layer so the LLM
could be swapped in later without touching the rest of the app").
"""

import pandas as pd


def explain_trend(df: pd.DataFrame, value_col: str, label: str, year_col: str = "Year") -> str:
    """Explain a time trend, e.g. EU/EEA cases by year."""
    df = df.sort_values(year_col)
    first_year, last_year = df[year_col].iloc[0], df[year_col].iloc[-1]
    first_val, last_val = df[value_col].iloc[0], df[value_col].iloc[-1]
    change = last_val - first_val
    pct = (change / first_val * 100) if first_val else 0

    direction = "increased" if change > 0 else "decreased" if change < 0 else "stayed roughly flat"

    # Find the year with the biggest single jump, to mention as a notable point
    diffs = df[value_col].diff()
    if diffs.notna().any():
        biggest_jump_idx = diffs.abs().idxmax()
        jump_year = df.loc[biggest_jump_idx, year_col]
        jump_val = diffs.loc[biggest_jump_idx]
        jump_note = (
            f" The most notable shift was around {int(jump_year)}, "
            f"with a change of about {jump_val:+.1f}."
        )
    else:
        jump_note = ""

    return (
        f"Between {int(first_year)} and {int(last_year)}, {label} {direction} "
        f"from {first_val:.1f} to {last_val:.1f} ({pct:+.1f}%)."
        f"{jump_note}"
    )


def explain_comparison(df: pd.DataFrame, group_col: str, value_col: str, label: str) -> str:
    """Explain a comparison across groups, e.g. which country/age group is highest."""
    df_sorted = df.sort_values(value_col, ascending=False)
    top = df_sorted.iloc[0]
    bottom = df_sorted.iloc[-1]
    avg = df[value_col].mean()

    ratio = top[value_col] / bottom[value_col] if bottom[value_col] else None
    ratio_note = f" That is about {ratio:.1f}x the rate of the lowest group, {bottom[group_col]}." if ratio else ""

    return (
        f"{top[group_col]} has the highest {label} at {top[value_col]:.1f}, "
        f"compared to an average of {avg:.1f} across all groups.{ratio_note}"
    )


def explain_age_pattern(age_df: pd.DataFrame) -> str:
    """Specific explanation for age-group breakdowns, since this is a common query type."""
    sorted_df = age_df.sort_values("NotificationRate_per_100k", ascending=False)
    top = sorted_df.iloc[0]
    young_groups = age_df[age_df["AgeGroup"].isin(["0-4", "5-14"])]
    older_groups = age_df[age_df["AgeGroup"].isin(["45-64", "65+"])]

    young_avg = young_groups["NotificationRate_per_100k"].mean()
    older_avg = older_groups["NotificationRate_per_100k"].mean()

    pattern_note = ""
    if older_avg > young_avg * 1.5:
        pattern_note = " Rates are notably higher in older age groups, a pattern consistent with reactivation of latent infection later in life."
    elif young_avg > older_avg * 1.5:
        pattern_note = " Rates skew toward younger groups, which can reflect recent transmission rather than reactivation."

    return (
        f"The {top['AgeGroup']} age group shows the highest notification rate "
        f"at {top['NotificationRate_per_100k']:.1f} per 100,000.{pattern_note}"
    )
