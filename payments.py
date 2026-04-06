"""Stripe payment integration."""

import logging
import stripe
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from config import settings, PRICING

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(
    user_id: str, email: str, plan_type: str = "monthly"
) -> Optional[str]:
    """Create Stripe checkout session.
    
    Args:
        user_id: User ID
        email: User email
        plan_type: "monthly" or "annual"
        
    Returns:
        Checkout URL or None
    """
    if not settings.STRIPE_SECRET_KEY:
        logger.warning("Stripe not configured")
        return None

    try:
        price_usd = PRICING[f"{plan_type}_usd"]

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(price_usd * 100),  # Convert to cents
                        "recurring": {"interval": plan_type[:1], "interval_count": 1}
                        if plan_type == "monthly"
                        else {"interval": "year", "interval_count": 1},
                        "product_data": {
                            "name": f"Athena AI Premium ({plan_type.title()})",
                            "description": "Unlimited access to all features",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url="https://athena-ai.streamlit.app?payment=success",
            cancel_url="https://athena-ai.streamlit.app?payment=cancelled",
            customer_email=email,
            metadata={"user_id": user_id, "plan_type": plan_type},
        )

        logger.info(f"Created checkout session for {user_id}: {session.id}")
        return session.url

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        return None


def handle_webhook(event: Dict[str, Any]) -> bool:
    """Handle Stripe webhook events.
    
    Args:
        event: Stripe event object
        
    Returns:
        True if handled successfully
    """
    from database import db

    try:
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = session["metadata"]["user_id"]
            plan_type = session["metadata"]["plan_type"]
            subscription_id = session["subscription"]

            # Create subscription in database
            if db.is_connected():
                db.create_subscription(user_id, subscription_id, plan_type)
                logger.info(f"Subscription activated for {user_id}")

        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            user_id = subscription["metadata"]["user_id"]

            # Cancel subscription in database
            if db.is_connected():
                db.cancel_subscription(user_id)
                logger.info(f"Subscription cancelled for {user_id}")

        return True

    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return False


def verify_webhook_signature(payload: bytes, sig_header: str) -> Optional[Dict[str, Any]]:
    """Verify and parse Stripe webhook signature.
    
    Args:
        payload: Request body
        sig_header: Stripe signature header
        
    Returns:
        Event object or None if signature invalid
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_SECRET_KEY
        )
        return event
    except ValueError:
        logger.error("Invalid webhook payload")
        return None
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid webhook signature")
        return None


def format_price(amount_usd: float, currency: str = "USD") -> str:
    """Format price for display.
    
    Args:
        amount_usd: Amount in USD
        currency: Display currency (USD or HKD)
        
    Returns:
        Formatted price string
    """
    if currency == "HKD":
        hkd_amount = amount_usd * 7.8  # Approximate conversion
        return f"HK${hkd_amount:.0f}/month"
    return f"${amount_usd:.2f}/month"


def render_pricing_table():
    """Render pricing comparison table in Streamlit."""
    import streamlit as st

    st.markdown("## 💰 Simple Pricing")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🆓 Free Tier")
        st.write(
            """
        - 5 quizzes/day
        - 2 study plans/day
        - 3 past papers/day
        - 10 learn sessions/day
        """
        )
        st.button("Start Free →", use_container_width=True, disabled=True)

    with col2:
        st.markdown("### 👑 Premium")
        st.write(
            """
        - ✅ Unlimited quizzes
        - ✅ Unlimited study plans
        - ✅ Unlimited past papers
        - ✅ Unlimited learning
        - ✅ Ad-free
        """
        )

        subscription_type = st.radio("Choose plan:", ["Monthly ($9.99)", "Annual ($99.99)"], horizontal=True)
        plan = "monthly" if "Monthly" in subscription_type else "annual"

        if st.button("🚀 Upgrade Now", use_container_width=True, type="primary"):
            user_id = st.session_state.get("user_id", "demo_user")
            email = st.session_state.get("user_email", "demo@athena.ai")

            checkout_url = create_checkout_session(user_id, email, plan)
            if checkout_url:
                st.markdown(f"[👉 Go to Checkout]({checkout_url})")
            else:
                st.error("Payment processing temporarily unavailable")
