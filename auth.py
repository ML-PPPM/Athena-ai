"""Authentication and user session management."""

import logging
import streamlit as st
from typing import Optional, Tuple, Dict
from datetime import datetime

from database import db

logger = logging.getLogger(__name__)


def init_auth_session():
    """Initialize authentication session state."""
    auth_defaults = {
        "user_id": None,
        "user_email": None,
        "is_authenticated": False,
        "is_premium": False,
        "auth_method": None,  # "demo" or "supabase"
    }
    for key, value in auth_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_auth_page():
    """Render authentication page (login/signup)."""
    st.markdown("# 🔐 Welcome to Athena AI")
    st.caption("Sign in to unlock personalized learning, streak tracking, and more!")

    tab1, tab2, tab3 = st.tabs(["🚀 Sign Up", "📝 Sign In", "👤 Demo Mode"])

    # ─────────────────────────────────────────────────────────────
    # SIGN UP TAB
    # ─────────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Create Account")
        email = st.text_input("📧 Email", key="signup_email")
        password = st.text_input("🔐 Password (min 8 chars)", type="password", key="signup_password")
        password_confirm = st.text_input(
            "Confirm Password", type="password", key="signup_confirm"
        )
        full_name = st.text_input("👤 Full Name (optional)", key="signup_name")

        if st.button("🚀 Create Account", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Email and password are required")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters")
            elif password != password_confirm:
                st.error("Passwords don't match")
            else:
                st.info("✅ Feature coming soon! For now, use Demo Mode to explore.")
                logger.info(f"Signup attempt: {email}")

    # ─────────────────────────────────────────────────────────────
    # SIGN IN TAB
    # ─────────────────────────────────────────────────────────────
    with tab2:
        st.markdown("### Sign In")
        email = st.text_input("📧 Email", key="signin_email")
        password = st.text_input("🔐 Password", type="password", key="signin_password")

        if st.button("📝 Sign In", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Email and password are required")
            else:
                st.info("✅ Feature coming soon! For now, use Demo Mode to explore.")
                logger.info(f"Signin attempt: {email}")

    # ─────────────────────────────────────────────────────────────
    # DEMO MODE TAB
    # ─────────────────────────────────────────────────────────────
    with tab3:
        st.markdown("### Try Demo Mode")
        st.info(
            "✨ **No signup required!**\n\n"
            "Explore all features with limited daily usage:\n"
            "- 5 quizzes/day\n"
            "- 2 study plans/day\n"
            "- 3 past papers/day\n\n"
            "Sign up to unlock unlimited access!"
        )

        demo_name = st.text_input(
            "👤 Your name (optional)",
            value="Demo User",
            key="demo_name",
        )

        if st.button("👤 Enter as Guest", use_container_width=True, type="primary"):
            st.session_state.user_id = f"demo_{datetime.now().timestamp()}"
            st.session_state.user_email = "demo@athena.ai"
            st.session_state.is_authenticated = True
            st.session_state.is_premium = False
            st.session_state.auth_method = "demo"
            logger.info(f"Demo login: {demo_name}")
            st.success(f"👋 Welcome, {demo_name}!")
            st.rerun()


def check_usage_limit(user_id: str, feature: str) -> Tuple[bool, str, Dict]:
    """Check if user has exceeded usage limit for feature.
    
    Returns:
        (is_allowed, message, remaining_usage)
    """
    from config import FREE_TIER, PREMIUM_TIER

    user = db.get_user(user_id) if db.is_connected() else None
    is_premium = user.get("is_premium", False) if user else False

    # Get limits for this user
    limits = PREMIUM_TIER if is_premium else FREE_TIER

    # Get today's usage
    today_usage = db.get_today_usage(user_id) if db.is_connected() else {}

    # Map features to limit keys
    feature_map = {
        "quiz": ("daily_quizzes", "quizzes"),
        "past_paper": ("daily_past_papers", "past_papers"),
        "plan": ("daily_plans", "plans"),
        "learn": ("daily_learn_sessions", "learn_sessions"),
    }

    if feature not in feature_map:
        return True, "", {"limit": 0, "used": 0, "remaining": 0}

    limit_key, usage_key = feature_map[feature]
    limit = limits[limit_key]
    used = today_usage.get(usage_key, 0)
    remaining = limit - used

    data = {"limit": limit, "used": used, "remaining": remaining}

    if used >= limit:
        msg = (
            f"❌ Daily limit reached ({used}/{limit})\n\n"
            "Upgrade to premium for unlimited access!"
        )
        return False, msg, data

    if remaining <= 3:
        msg = f"⚠️ {remaining} uses remaining today"
        return True, msg, data

    return True, "", data


def render_premium_badge():
    """Render user badge in sidebar."""
    if st.session_state.get("is_authenticated"):
        if st.session_state.get("is_premium"):
            st.markdown("### 👑 Premium User")
            st.success("Unlimited features!")
        elif st.session_state.get("auth_method") == "demo":
            st.markdown("### 👤 Guest User")
            st.warning("Limited free tier")
            if st.button("⬆️ Upgrade to Premium", use_container_width=True):
                st.session_state.show_pricing = True
                st.rerun()
        else:
            st.markdown("### 📋 Athena AI")


def logout():
    """Logout current user."""
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.is_authenticated = False
    st.session_state.is_premium = False
    st.session_state.auth_method = None
    logger.info("User logged out")
    st.success("Logged out successfully!")
    st.rerun()