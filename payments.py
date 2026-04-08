"""Payment integration using Stripe for automatic subscriptions."""
import logging
import stripe
import streamlit as st
from datetime import datetime
from config import settings
from database import db

logger = logging.getLogger(__name__)

# Initialize Stripe
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY
else:
    logger.warning("Stripe secret key not configured")


def create_subscription(user_email: str, price_id: str) -> dict:
    """Create a Stripe subscription for the user."""
    if not settings.STRIPE_SECRET_KEY:
        return {"error": "Stripe not configured"}

    try:
        # Create or retrieve customer
        customers = stripe.Customer.list(email=user_email, limit=1)
        if customers.data:
            customer = customers.data[0]
        else:
            customer = stripe.Customer.create(email=user_email)

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
        )

        return {
            "subscription_id": subscription.id,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret,
            "customer_id": customer.id,
        }
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        return {"error": str(e)}


def handle_payment_success(subscription_id: str, user_id: str):
    """Handle successful payment and upgrade user to premium."""
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        price_id = subscription.items.data[0].price.id

        # Determine plan type from price ID
        plan_type = "monthly"  # Default
        if "semester" in price_id.lower():
            plan_type = "semester"
        elif "dse" in price_id.lower() or "bundle" in price_id.lower():
            plan_type = "dse_bundle"

        # Create subscription record and upgrade user
        db.create_subscription(user_id, subscription_id, plan_type)

        logger.info(f"Successfully upgraded user {user_id} to premium with {plan_type} plan")
        return True
    except Exception as e:
        logger.error(f"Error handling payment success: {e}")
        return False


def render_pricing_table():
    """Render pricing page with Stripe subscription options."""

    st.markdown("## 💰 Choose Your Plan")
    st.markdown("")

    if not settings.STRIPE_PUBLIC_KEY:
        st.error("Payment system is not configured. Please contact support.")
        return

    # ── Free vs Premium comparison ──
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            ### 🆓 Free

            - 5 quizzes/day
            - 2 study plans/day
            - 3 past papers/day
            - 10 learn sessions/day
            """
        )
        if st.session_state.get("is_premium"):
            st.button("Downgrade to Free", use_container_width=True, type="secondary")
        else:
            st.button("Current Plan ✅", disabled=True, use_container_width=True)

    with col2:
        st.markdown(
            f"""
            ### 👑 Monthly — ${settings.PRICING['monthly_usd']}/mo

            - ✅ **Unlimited** quizzes
            - ✅ **Unlimited** study plans
            - ✅ **Unlimited** past papers
            - ✅ **Unlimited** learning
            - ✅ Priority support
            - ✅ Cancel anytime
            """
        )
        if st.button("Subscribe Monthly", use_container_width=True, type="primary"):
            st.session_state.show_checkout = "monthly"

    with col3:
        st.markdown(
            f"""
            ### 🎓 Semester — ${settings.PRICING['semester_usd']}/5mo

            - ✅ **Unlimited** everything
            - ✅ **Save 20%** vs monthly
            - ✅ 5 months coverage
            - ✅ Perfect for exam prep
            - ✅ Priority support
            """
        )
        if st.button("Subscribe Semester", use_container_width=True, type="primary"):
            st.session_state.show_checkout = "semester"

    # ── Checkout Modal ──
    if st.session_state.get("show_checkout"):
        plan = st.session_state.show_checkout

        st.markdown("---")
        st.markdown(f"## 🛒 Checkout — {plan.title()} Plan")

        # Price IDs (you'll need to create these in Stripe dashboard)
        price_ids = {
            "monthly": "price_monthly_premium",  # Replace with actual Stripe price ID
            "semester": "price_semester_premium",  # Replace with actual Stripe price ID
        }

        if plan in price_ids:
            user_email = st.session_state.get("user_email", "")
            if user_email:
                result = create_subscription(user_email, price_ids[plan])

                if "error" in result:
                    st.error(f"Failed to create subscription: {result['error']}")
                else:
                    st.success("Subscription created! Complete payment below.")

                    # Stripe Elements checkout
                    st.markdown(
                        f"""
                        <script src="https://js.stripe.com/v3/"></script>
                        <div id="payment-element"></div>
                        <button id="submit">Complete Payment</button>

                        <script>
                        const stripe = Stripe('{settings.STRIPE_PUBLIC_KEY}');
                        const elements = stripe.elements();
                        const paymentElement = elements.create('payment');
                        paymentElement.mount('#payment-element');

                        const submitButton = document.getElementById('submit');
                        submitButton.addEventListener('click', async (event) => {{
                            event.preventDefault();
                            const {{error}} = await stripe.confirmPayment({{
                                elements,
                                confirmParams: {{
                                    return_url: window.location.href,
                                }},
                            }});
                            if (error) {{
                                alert(error.message);
                            }}
                        }});
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.error("Please sign in to subscribe.")
        else:
            st.error("Invalid plan selected.")

        if st.button("Cancel", use_container_width=True):
            del st.session_state.show_checkout
            st.rerun()

    with st.expander("我有其他問題"):
        st.markdown("WhatsApp 我: [YOUR NUMBER]，我會盡快回覆！")

    st.divider()
    st.caption(
        "🔒 Your payment information is secure. "
        "We use PayMe/Alipay's official payment systems."
    )