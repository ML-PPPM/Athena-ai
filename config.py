"""Configuration and constants for Athena AI."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Stripe
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""

    # App
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def _get_streamlit_secret(key: str, default=""):
    """Safely retrieve a value from Streamlit secrets at runtime.

    Falls back to ``default`` if Streamlit is not running or the key is absent.
    This must never be called at import/build time.
    """
    try:
        import streamlit as st

        return st.secrets.get(key, default)
    except Exception:
        return default


# Load settings — prefer environment variables (available during build and at
# runtime on Railway) and only fall back to Streamlit secrets at runtime.
settings = Settings(
    ANTHROPIC_API_KEY=os.getenv("ANTHROPIC_API_KEY", "") or _get_streamlit_secret("ANTHROPIC_API_KEY", ""),
    ANTHROPIC_MODEL=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
    SUPABASE_URL=os.getenv("SUPABASE_URL", "") or _get_streamlit_secret("SUPABASE_URL", ""),
    SUPABASE_KEY=os.getenv("SUPABASE_KEY", "") or _get_streamlit_secret("SUPABASE_KEY", ""),
    STRIPE_PUBLIC_KEY=os.getenv("STRIPE_PUBLISHABLE_KEY", "") or os.getenv("STRIPE_PUBLIC_KEY", "") or _get_streamlit_secret("STRIPE_PUBLIC_KEY", ""),
    STRIPE_SECRET_KEY=os.getenv("STRIPE_SECRET_KEY", "") or _get_streamlit_secret("STRIPE_SECRET_KEY", ""),
    DEBUG=os.getenv("DEBUG", "").lower() in ("1", "true", "yes"),
    ENVIRONMENT=os.getenv("ENVIRONMENT", "") or _get_streamlit_secret("ENVIRONMENT", "development"),
)


# App Constants
MAX_CHAT_HISTORY = 20
DEFAULT_MAX_TOKENS = 800

# Free Tier Limits
FREE_TIER = {
    "daily_quizzes": 5,
    "daily_plans": 2,
    "daily_past_papers": 3,
    "daily_learn_sessions": 10,
}

# Premium Tier Features
PREMIUM_TIER = {
    "daily_quizzes": 100,
    "daily_plans": 20,
    "daily_past_papers": 50,
    "daily_learn_sessions": 999,
}

# Pricing
PRICING = {
    "monthly_usd": 9.99,
    "monthly_hkd": 79,
    "annual_usd": 99.99,
    "annual_hkd": 779,
}
