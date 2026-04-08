"""Authentication and user session management."""

import logging
import streamlit as st
from typing import Optional, Tuple, Dict
from datetime import datetime

from database import db
from supabase import create_client

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

    # Check if Supabase is configured
    supabase_configured = db.is_connected()

    if not supabase_configured:
        st.warning("⚠️ **Supabase not configured** - Authentication will not work. Use Development Mode below.")
        st.info("""
        **To enable authentication:**
        1. Set up Supabase at [supabase.com](https://supabase.com)
        2. Configure `SUPABASE_URL` and `SUPABASE_KEY` in your `.env` file
        3. Restart the app
        """)

    tab1, tab2, tab3 = st.tabs(["🚀 Sign Up", "📝 Sign In", "🚧 Development Mode"])

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

        if st.button("🚀 Create Account", use_container_width=True, type="primary", disabled=not supabase_configured):
            if not supabase_configured:
                st.error("Supabase not configured. Use Development Mode instead.")
            elif not email or not password:
                st.error("Email and password are required")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters")
            elif password != password_confirm:
                st.error("Passwords don't match")
            else:
                try:
                    # Attempt to sign up with Supabase
                    response = db.client.auth.sign_up({
                        "email": email,
                        "password": password,
                        "options": {
                            "data": {
                                "full_name": full_name
                            }
                        }
                    })
                    if response.user:
                        # Create user in database
                        db.create_user(response.user.id, email, full_name, False)
                        st.success("Account created successfully! Please check your email to verify your account.")
                        logger.info(f"Signup successful: {email}")
                    else:
                        st.error("Failed to create account. Please try again.")
                except Exception as e:
                    st.error(f"Signup failed: {str(e)}")
                    logger.error(f"Signup error: {e}")

    # ─────────────────────────────────────────────────────────────
    # SIGN IN TAB
    # ─────────────────────────────────────────────────────────────
    with tab2:
        st.markdown("### Sign In")
        email = st.text_input("📧 Email", key="signin_email")
        password = st.text_input("🔐 Password", type="password", key="signin_password")

        if st.button("📝 Sign In", use_container_width=True, type="primary", disabled=not supabase_configured):
            if not supabase_configured:
                st.error("Supabase not configured. Use Development Mode instead.")
            elif not email or not password:
                st.error("Email and password are required")
            else:
                try:
                    # Attempt to sign in with Supabase
                    response = db.client.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    if response.user:
                        # Get user data
                        user_data = db.get_user(response.user.id)
                        if user_data:
                            # Check subscription status and update if needed
                            check_and_update_premium_status(response.user.id, user_data)

                            st.session_state.user_id = response.user.id
                            st.session_state.user_email = response.user.email
                            st.session_state.is_authenticated = True
                            st.session_state.is_premium = user_data.get("is_premium", False)
                            st.session_state.auth_method = "supabase"
                            logger.info(f"Signin successful: {email}")
                            st.success(f"Welcome back, {user_data.get('full_name', 'User')}!")
                            st.rerun()
                        else:
                            st.error("User data not found. Please contact support.")
                    else:
                        st.error("Invalid email or password")
                except Exception as e:
                    st.error(f"Sign in failed: {str(e)}")
                    logger.error(f"Signin error: {e}")

    # ─────────────────────────────────────────────────────────────
    # DEVELOPMENT MODE TAB
    # ─────────────────────────────────────────────────────────────
    with tab3:
        st.markdown("### Development Mode")
        st.info(
            "✨ **No setup required!**\n\n"
            "Explore all features with premium access:\n"
            "- ✅ Unlimited quizzes\n"
            "- ✅ Unlimited study plans\n"
            "- ✅ Unlimited past papers\n"
            "- ✅ All learning features\n\n"
            "Perfect for testing and development!"
        )

        demo_name = st.text_input(
            "👤 Your name (optional)",
            value="Developer",
            key="dev_name",
        )

        if st.button("🚧 Enter Development Mode", use_container_width=True, type="primary"):
            st.session_state.user_id = f"dev_{demo_name.lower().replace(' ', '_')}"
            st.session_state.user_email = f"{demo_name.lower().replace(' ', '.')}@dev.local"
            st.session_state.is_authenticated = True
            st.session_state.is_premium = True
            st.session_state.auth_method = "development"
            logger.info(f"Development login: {demo_name}")
            st.success(f"🚧 Welcome to Development Mode, {demo_name}!")
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
        if st.session_state.get("auth_method") == "development":
            st.markdown("### 🚧 Development Mode")
            st.info("Full access for testing")
        elif st.session_state.get("is_premium"):
            st.markdown("### 👑 Premium User")
            st.success("Unlimited features!")
        else:
            st.markdown("### 📋 Athena AI")
            st.info("Free tier - upgrade for unlimited access")
            if st.button("⬆️ Upgrade to Premium", use_container_width=True):
                st.session_state.show_pricing = True
                st.rerun()


def check_and_update_premium_status(user_id: str, user_data: Dict):
    """Check subscription status and update premium status if needed."""
    if not db.is_connected():
        return

    try:
        # Check if user has active subscription (don't use .single() as it expects exactly 1 row)
        subscriptions = db.client.table('subscriptions').select('*').eq('user_id', user_id).eq('status', 'active').execute()

        if subscriptions.data and len(subscriptions.data) > 0:
            subscription = subscriptions.data[0]  # Get the first active subscription
            # Check if subscription is still valid
            from datetime import datetime
            renews_at = datetime.fromisoformat(subscription['renews_at'])
            if datetime.now() < renews_at:
                # Ensure user is marked as premium
                if not user_data.get('is_premium'):
                    db.update_user(user_id, {'is_premium': True})
                    logger.info(f"Updated user {user_id} to premium based on active subscription")
            else:
                # Subscription expired, downgrade user
                db.update_user(user_id, {'is_premium': False, 'premium_until': None})
                db.client.table('subscriptions').update({'status': 'expired'}).eq('user_id', user_id).execute()
                logger.info(f"Downgraded expired subscription for user {user_id}")
        else:
            # No active subscription, ensure user is not premium
            if user_data.get('is_premium'):
                db.update_user(user_id, {'is_premium': False, 'premium_until': None})
                logger.info(f"Removed premium status for user {user_id} - no active subscription")

    except Exception as e:
        logger.error(f"Error checking subscription status for {user_id}: {e}")


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