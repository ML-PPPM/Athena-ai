"""Configuration and constants for Athena AI."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Anthropic
    ANTHROPIC_API_KEY: str
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


# Load settings
try:
    settings = Settings()
except Exception as e:
    # If .env doesn't exist, try to load from Streamlit secrets
    import streamlit as st

    settings = Settings(
        ANTHROPIC_API_KEY=st.secrets.get("ANTHROPIC_API_KEY", ""),
        SUPABASE_URL=st.secrets.get("SUPABASE_URL", ""),
        SUPABASE_KEY=st.secrets.get("SUPABASE_KEY", ""),
        STRIPE_PUBLIC_KEY=st.secrets.get("STRIPE_PUBLIC_KEY", ""),
        STRIPE_SECRET_KEY=st.secrets.get("STRIPE_SECRET_KEY", ""),
        DEBUG=st.secrets.get("DEBUG", False),
        ENVIRONMENT=st.secrets.get("ENVIRONMENT", "development"),
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
