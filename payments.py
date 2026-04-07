"""Payment integration using PayMe and Alipay with push notifications."""
import logging
import urllib.request
import streamlit as st
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Change this to your own secret topic name ──
NTFY_TOPIC = "athena-ai-payments-ml-pppm"


def notify_me(name, contact, method, email):
    """Send free push notification when someone pays."""
    try:
        data = (
            f"💰 NEW PAYMENT!\n"
            f"Name: {name}\n"
            f"Contact: {contact}\n"
            f"Method: {method}\n"
            f"Email: {email}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        req = urllib.request.Request(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=data.encode(),
            headers={
                "Title": "Athena AI — New Payment!",
                "Priority": "high",
                "Tags": "money_with_wings",
            },
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
        logger.info(f"Payment notification sent for {name}")
    except Exception as e:
        logger.warning(f"Failed to send notification: {e}")


def render_pricing_table():
    """Render pricing page with PayMe/Alipay QR codes."""

    st.markdown("## 💰 Simple Pricing")
    st.markdown("")

    # ── Free vs Premium comparison ──
    col1, col2 = st.columns(2)

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
        st.button("Current Plan ✅", disabled=True, use_container_width=True)

    with col2:
        st.markdown(
            """
            ### 👑 Premium — $68/月
            
            - ✅ **Unlimited** quizzes
            - ✅ **Unlimited** study plans
            - ✅ **Unlimited** past papers
            - ✅ **Unlimited** learning
            - ✅ Priority support
            - ✅ Early access to new features
            """
        )

    st.divider()

    # ── Price comparison ──
    st.markdown("### 💡 Compare")
    st.markdown(
        """
        | | Price | Available |
        |---|---|---|
        | Private Tutor 補習 | $200-500/hr | Few hours/week |
        | Tutorial Center 補習社 | $800-2000/mo | Limited subjects |
        | **Athena AI Premium** | **$68/mo** | **24/7, all 14 subjects** |
        """
    )

    st.divider()

    # ── Payment methods ──
    st.markdown("## 📱 How to Pay 付款方法")
    st.markdown("")

    tab1, tab2, tab3 = st.tabs(["📱 PayMe", "📱 Alipay", "💵 Other"])

    with tab1:
        st.markdown("### Scan with PayMe")
        st.markdown("**Amount 金額: HK$68**")
        st.markdown("")
        try:
            st.image("payme_qr.png", width=250, caption="Scan to pay $68 via PayMe")
        except Exception:
            st.markdown(
                """
                📱 **PayMe Steps:**
                1. Open PayMe app
                2. Click "Send 付款"
                3. Search phone number: **[YOUR PHONE NUMBER]**
                4. Enter amount: **$68**
                5. Send ✅
                """
            )

    with tab2:
        st.markdown("### Scan with Alipay HK")
        st.markdown("**Amount 金額: HK$68**")
        st.markdown("")
        try:
            st.image("alipay_qr.png", width=250, caption="Scan to pay $68 via Alipay")
        except Exception:
            st.markdown(
                """
                📱 **Alipay Steps:**
                1. Open Alipay HK app
                2. Click "Transfer 轉賬"
                3. Search phone number: **[YOUR PHONE NUMBER]**
                4. Enter amount: **$68**
                5. Confirm ✅
                """
            )

    with tab3:
        st.markdown("### Other Payment Methods")
        st.markdown(
            """
            📱 **FPS 轉數快:** [YOUR PHONE NUMBER]
            🏧 **Bank Transfer:** [YOUR BANK DETAILS — optional]
            💵 **Cash:** Contact me on WhatsApp
            
            📞 **WhatsApp:** [YOUR WHATSAPP NUMBER]
            """
        )

    st.divider()

    # ── Payment confirmation form ──
    st.markdown("## ✅ After Payment 付款後")
    st.markdown("填寫以下資料，我會喺 **24 小時內** 開通你嘅 Premium 👑")
    st.markdown("")

    with st.form("payment_form"):
        col_a, col_b = st.columns(2)

        with col_a:
            name = st.text_input(
                "👤 Your Name 你的名字",
                placeholder="e.g. Chan Siu Ming"
            )
        with col_b:
            contact = st.text_input(
                "📱 WhatsApp Number",
                placeholder="e.g. 9123 4567"
            )

        col_c, col_d = st.columns(2)

        with col_c:
            method = st.selectbox(
                "💳 Payment Method 付款方式",
                ["PayMe", "Alipay HK", "FPS 轉數快", "Bank Transfer", "Cash 現金"]
            )
        with col_d:
            email = st.text_input(
                "📧 Email (登入用)",
                placeholder="your@email.com"
            )

        amount = st.selectbox(
            "💰 Plan 計劃",
            [
                "Monthly 月費 — HK$68/month",
                "Semester 學期 — HK$298/5 months (Save $42!)",
                "DSE Bundle 考試套餐 — HK$488 (until DSE exam)",
            ]
        )

        notes = st.text_area(
            "📝 Notes 備註 (optional)",
            placeholder="e.g. transaction ID, payment time, anything else...",
            height=80,
        )

        st.markdown("")
        submitted = st.form_submit_button(
            "✅ I've Paid — Activate My Premium!",
            use_container_width=True,
            type="primary",
        )

        if submitted:
            if not name.strip():
                st.error("⚠️ Please enter your name 請輸入你的名字")
            elif not contact.strip():
                st.error("⚠️ Please enter your WhatsApp number 請輸入你的WhatsApp號碼")
            elif not email.strip():
                st.error("⚠️ Please enter your email 請輸入你的電郵")
            else:
                # Send push notification to you
                notify_me(
                    name.strip(),
                    contact.strip(),
                    f"{method} — {amount}",
                    email.strip(),
                )

                # Log it
                logger.info(
                    f"Premium request: {name}, {contact}, "
                    f"{method}, {email}, {amount}"
                )

                st.success(
                    f"🎉 **Payment Received!**\n\n"
                    f"**Name:** {name}\n"
                    f"**Contact:** {contact}\n"
                    f"**Method:** {method}\n"
                    f"**Plan:** {amount}\n\n"
                    f"---\n"
                    f"📱 我會喺 24 小時內 WhatsApp 你確認\n"
                    f"Premium will be activated within 24 hours 👑\n\n"
                    f"如有問題，WhatsApp 我: [YOUR NUMBER]"
                )

                st.balloons()

    st.divider()

    # ── FAQ ──
    st.markdown("## ❓ FAQ")

    with st.expander("點樣知道我已經升級？"):
        st.markdown("我會 WhatsApp 你確認，之後你 refresh 個 app 就會見到 👑 Premium badge。")

    with st.expander("可唔可以退款？"):
        st.markdown("首 7 日內可以全額退款。之後唔設退款，但可以隨時取消下個月。")

    with st.expander("點樣取消？"):
        st.markdown("WhatsApp 我話想取消就得，下個月唔會再收費。")

    with st.expander("我有其他問題"):
        st.markdown("WhatsApp 我: [YOUR NUMBER]，我會盡快回覆！")

    st.divider()
    st.caption(
        "🔒 Your payment information is secure. "
        "We use PayMe/Alipay's official payment systems."
    )