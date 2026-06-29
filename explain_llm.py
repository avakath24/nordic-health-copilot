"""
LLM-powered explanation layer (v2 upgrade).

Replaces the purely rule-based explanations with a real call to the
Anthropic API, falling back automatically to the rule-based version in
explain.py if no API key is configured -- the app keeps working even if a
key is missing or a network call fails.

Setup:
1. Get a free API key at https://console.anthropic.com/ (sign up, then
   Settings -> API Keys -> Create Key). New accounts get a small amount of
   free credit, more than enough for this project.
2. Create a file called `.env` in the project root (same folder as app.py)
   containing one line:
       ANTHROPIC_API_KEY=your-key-here
3. That's it -- the app will automatically detect it and use real AI
   explanations instead of the rule-based ones.
"""

import os
import streamlit as st

import explain as rule_based

_client = None
_client_checked = False


def _get_client():
    """Lazily create an Anthropic client only if a key is available."""
    global _client, _client_checked
    if _client_checked:
        return _client
    _client_checked = True

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    # Streamlit Cloud users set secrets via st.secrets instead of .env
    if not api_key:
        try:
            api_key = st.secrets.get("ANTHROPIC_API_KEY")
        except Exception:
            api_key = None

    if not api_key:
        return None

    try:
        import anthropic
        _client = anthropic.Anthropic(api_key=api_key)
    except Exception:
        _client = None
    return _client


def _call_llm(prompt: str) -> str | None:
    client = _get_client()
    if client is None:
        return None
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        st.caption(f"⚠️ Live AI call failed, showing rule-based explanation instead. ({e})")
        return None


def explain_trend(df, value_col, label, year_col="Year") -> str:
    summary = df[[year_col, value_col]].to_string(index=False)
    prompt = (
        f"You are a health-data analyst. Here is a small table showing {label} over time:\n\n"
        f"{summary}\n\n"
        "Write 2 short sentences in plain language explaining the trend, suitable for a "
        "non-technical reader. Do not repeat the raw numbers in a list, just describe the pattern."
    )
    result = _call_llm(prompt)
    if result:
        return result
    return rule_based.explain_trend(df, value_col, label, year_col)


def explain_comparison(df, group_col, value_col, label) -> str:
    summary = df[[group_col, value_col]].sort_values(value_col, ascending=False).to_string(index=False)
    prompt = (
        f"You are a health-data analyst. Here is a table comparing {label} across groups:\n\n"
        f"{summary}\n\n"
        "Write 2 short sentences in plain language explaining what stands out, suitable for a "
        "non-technical reader."
    )
    result = _call_llm(prompt)
    if result:
        return result
    return rule_based.explain_comparison(df, group_col, value_col, label)


def explain_age_pattern(age_df) -> str:
    summary = age_df.to_string(index=False)
    prompt = (
        "You are a health-data analyst. Here is a table of disease notification rates by age group:\n\n"
        f"{summary}\n\n"
        "Write 2 short sentences in plain language explaining which age group is most affected and "
        "what that might suggest (e.g. recent transmission vs. reactivation of latent infection, or "
        "vaccination gaps), suitable for a non-technical reader."
    )
    result = _call_llm(prompt)
    if result:
        return result
    return rule_based.explain_age_pattern(age_df)


def using_live_ai() -> bool:
    """Lets the UI show a badge indicating whether real AI or rule-based is active."""
    return _get_client() is not None
