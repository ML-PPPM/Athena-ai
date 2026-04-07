"""Payment integration using PayMe and Alipay."""
import logging
import streamlit as st
from datetime import datetime

logger = logging.getLogger(__name__)


def render_pricing_table():
    """Render pricing page with PayMe/Alipay QR codes."""

    st.markdown("## 💰 Simple Pricing")
    st.markdown("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🆓 Free")
        st.markdown(
            """
            - 5 quizzes/day
            - 2 study plans/day
            - 3 past papers/day
            - 10 learn sessions/day
            """
        )
        st.button("Current Plan ✅", disabled=True, use_container_width=True)

    with col2:
        st.markdown("### 👑 Premium — $68/月")
        st.markdown(
            """
            - ✅ **Unlimited** quizzes
            - ✅ **Unlimited** study plans
            - ✅ **Unlimited** past papers
            - ✅ **Unlimited** learning
            - ✅ Priority support
            """
        )

    st.divider()
    st.markdown("## 📱 How to Pay")
    st.markdown("")

    tab1, tab2 = st.tabs(["📱 PayMe", "📱 Alipay"])

    with tab1:
        st.markdown("### Scan with PayMe")
        st.markdown("**Amount: $68 HKD**")
        try:
            st.image("payme_qr.png", width=250)
        except:
            st.info(
                "📱 PayMe Number: **[Your PayMe ID here]**\n\n"
                "Open PayMe → Send → Enter amount $68"
            )

    with tab2:
        st.markdown("### Scan with Alipay")
        st.markdown("**Amount: $68 HKD**")
        try:
            st.image("alipay_qr.png", width=250)
        except:
            st.info(
                "📱 Alipay ID: **[Your Alipay ID here]**\n\n"
                "Open Alipay → Transfer → Enter amount $68"
            )

    st.divider()
    st.markdown("## ✅ After Payment")

    with st.form("payment_form"):
        st.markdown("付款後填寫以下資料，我會喺 24 小時內開通你嘅 Premium 👑")

        name = st.text_input("👤 Your Name 你的名字")
        contact = st.text_input(
            "📱 WhatsApp / Phone Number",
            placeholder="e.g. 9123 4567"
        )
        method = st.radio(
            "💳 Payment Method 付款方式",
            ["PayMe", "Alipay HK"],
            horizontal=True
        )
        email = st.text_input(
            "📧 Email (用嚟登入)",
            placeholder="your@email.com"
        )

        submitted = st.form_submit_button(
            "✅ I've Paid — Activate My Premium!",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            if not name or not contact:
                st.error("⚠️ Please fill in your name and contact!")
            else:
                # Log the payment request
                logger.info(
                    f"Premium request: {name}, {contact}, "
                    f"{method}, {email}"
                )

                # Save to session for display
                st.session_state["payment_pending"] = {
                    "name": name,
                    "contact": contact,
                    "method": method,
                    "email": email,
                    "time": datetime.now().isoformat()
                }

                st.success(
                    f"🎉 **Received!**\n\n"
                    f"Name: {name}\n"
                    f"Contact: {contact}\n"
                    f"Method: {method}\n\n"
                    f"我會喺 24 小時內 WhatsApp 你確認 ✅\n"
                    f"Premium will be activated within 24 hours 👑"
                )

                st.balloons()

    st.divider()
    st.markdown(
        "❓ **Questions?** WhatsApp: [Your Number]\n\n"
        "💡 Premium 每月自動提醒續期，取消隨時得。"
    )