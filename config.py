"""Configuration and constants for Athena AI."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def _get_streamlit_secret(key: str, default=""):
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default


settings = Settings(
    GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY", "") or _get_streamlit_secret("GOOGLE_API_KEY", ""),
    GEMINI_MODEL=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    SUPABASE_URL=os.getenv("SUPABASE_URL", "") or _get_streamlit_secret("SUPABASE_URL", ""),
    SUPABASE_KEY=os.getenv("SUPABASE_KEY", "") or _get_streamlit_secret("SUPABASE_KEY", ""),
    STRIPE_PUBLIC_KEY=os.getenv("STRIPE_PUBLIC_KEY", "") or _get_streamlit_secret("STRIPE_PUBLIC_KEY", ""),
    STRIPE_SECRET_KEY=os.getenv("STRIPE_SECRET_KEY", "") or _get_streamlit_secret("STRIPE_SECRET_KEY", ""),
    DEBUG=os.getenv("DEBUG", "").lower() in ("1", "true", "yes"),
    ENVIRONMENT=os.getenv("ENVIRONMENT", "") or _get_streamlit_secret("ENVIRONMENT", "development"),
)

MAX_CHAT_HISTORY = 20
DEFAULT_MAX_TOKENS = 800

FREE_TIER = {
    "daily_quizzes": 5,
    "daily_plans": 2,
    "daily_past_papers": 3,
    "daily_learn_sessions": 10,
}

PREMIUM_TIER = {
    "daily_quizzes": 100,
    "daily_plans": 20,
    "daily_past_papers": 50,
    "daily_learn_sessions": 999,
}

PRICING = {
    "monthly_usd": 9.99,
    "monthly_hkd": 79,
    "annual_usd": 99.99,
    "annual_hkd": 779,
}