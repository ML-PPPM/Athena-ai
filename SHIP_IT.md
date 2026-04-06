# 🚢 SHIP IT — Complete Deployment Guide

Follow this exact sequence to go live in ~1 hour.

## PHASE 1: Setup External Services (20 min)

### 1A. Create Supabase Project

```bash
# Go to https://supabase.com
# Click "Start your project" → "Create new project"
# Fill in:
#   - Organization: your name
#   - Project name: "athena-ai"
#   - Database password: strong password (save it!)
#   - Region: Singapore (closest to HK)
# Click "Create new project"

# After created, go to: Settings → API
# Copy and save:
#   - Project URL (starts with https://)
#   - Anon public key (eyJhbGci...)
```

### 1B. Run SQL to Create Tables

```bash
# In Supabase dashboard:
# 1. Click "SQL Editor" (left sidebar)
# 2. Click "New query"
# 3. Copy-paste the SQL from DEPLOYMENT.md (the big SQL block)
# 4. Click "Run"
# Wait for "Success" message ✅
```

### 1C. Create Stripe Account

```bash
# Go to https://stripe.com
# Click "Sign up"
# Fill business info
# Verify email
# Go to: Dashboard → API keys
# Copy and save:
#   - Publishable key (pk_live_...)
#   - Secret key (sk_live_...)

# IMPORTANT: Use pk_test_ and sk_test_ until ready for real money!
```

### 1D. You Already Have Anthropic ✅

Your `ANTHROPIC_API_KEY` is ready from earlier.

---

## PHASE 2: Configure Locally (10 min)

### 2A. Create .env file

```bash
cd /workspaces/Athena-ai

# Copy template
cp .env.example .env

# Open and fill in (use YOUR keys from Phase 1):
# nano .env (or use VS Code)

# Fill these:
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGci...YOUR_ANON_KEY
STRIPE_PUBLIC_KEY=pk_test_YOUR_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
ENVIRONMENT=development
DEBUG=False
```

### 2B. Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py

# Should open at http://localhost:8501
# Click "Guest Mode" → Try it out!
# Take 5 quizzes → Should hit limit
# Click "Upgrade" → Should see Stripe checkout
```

If page is blank or errors:
```bash
# Check logs
streamlit run streamlit_app.py --logger.level=debug

# Or check syntax
python -m py_compile streamlit_app.py config.py auth.py database.py payments.py
```

---

## PHASE 3: Deploy to Streamlit Cloud (15 min)

### 3A. Commit & Push to GitHub

```bash
# Stage all changes
git add .
git commit -m "Production: Add auth, DB, payments"
git push origin main

# Verify on GitHub: https://github.com/ML-PPPM/Athena-ai
```

### 3B. Deploy to Streamlit Cloud

```bash
# Option 1: Using CLI
streamlit login
# (follow prompts to connect GitHub account)

streamlit deploy
# Choose: ML-PPPM/Athena-ai, main branch, streamlit_app.py
```

**Option 2: Using Web Interface**
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select GitHub repo: ML-PPPM/Athena-ai
4. Branch: main
5. File: streamlit_app.py
6. Click "Deploy"

After deployment:
```
✅ Your app is live at: https://athena-ai-RANDOM.streamlit.app
```

### 3C. Add Secrets to Streamlit Cloud

In Streamlit Cloud dashboard:
1. Click "Advanced settings"
2. Paste this in "Secrets":

```toml
ANTHROPIC_API_KEY = "sk-ant-YOUR_LIVE_KEY"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "eyJhbGci..."
STRIPE_PUBLIC_KEY = "pk_test_YOUR_KEY"
STRIPE_SECRET_KEY = "sk_test_YOUR_KEY"
ENVIRONMENT = "production"
DEBUG = False
```

3. Click "Save"
4. Streamlit automatically redeploys ✅

---

## PHASE 4: Test Payment Flow (10 min)

### 4A. Visit Your Live App

```
https://athena-ai-RANDOM.streamlit.app
```

### 4B. Full Test Flow

```
1. Click "Guest Mode"
   └─ Should see "👤 Guest User" in sidebar

2. Take 5 quizzes
   └─ On 6th quiz, should say "Daily limit reached"

3. Click "⬆️ Upgrade to Premium"
   └─ Should show pricing table

4. Click "🚀 Upgrade Now" → "Monthly"
   └─ Should redirect to Stripe checkout

5. Use TEST CARD:
   Card: 4242 4242 4242 4242
   Expiry: 12/25
   CVC: 123

6. Complete checkout
   └─ Stripe processes payment (test)

7. Back to app (should be marked premium)
   └─ Take unlimited quizzes ✅
```

### 4C. Verify in Supabase

```bash
# Go to Supabase dashboard
# Click: SQL Editor → New query
# Paste and run:

SELECT * FROM users ORDER BY created_at DESC LIMIT 1;
SELECT * FROM subscriptions WHERE status = 'active';
SELECT * FROM quiz_results LIMIT 5;

# Should see your test data ✅
```

---

## PHASE 5: Go Live with Real Payments (5 min)

### 5A. Switch to Stripe Live Keys

```bash
# When ready for REAL money:

# 1. In Stripe dashboard:
#    - Confirm you're in "Live" mode (not Test)
#    - Copy pk_live_... and sk_live_... keys

# 2. Update Streamlit Cloud secrets:
#    - Replace pk_test_ with pk_live_
#    - Replace sk_test_ with sk_live_

# Wait ~30 seconds for redeploy
```

### 5B. Add Webhook for Payments

```bash
# In Stripe dashboard:
# 1. Go to: Developers → Webhooks → Add endpoint
# 2. Endpoint URL: 
#    https://athena-ai-RANDOM.streamlit.app/webhook
#
# 3. Select events:
#    - checkout.session.completed
#    - customer.subscription.deleted
#
# 4. Copy "Signing secret" → Add to Streamlit secrets as:
#    STRIPE_WEBHOOK_SECRET = "whsec_..."
#
# Click "Add endpoint" ✅
```

### 5C. You're Live! 🎉

Your app can now:
- ✅ Accept real payments
- ✅ Create subscriptions
- ✅ Save user data
- ✅ Track usage

---

## PHASE 6: Market & Grow (Ongoing)

### 6A. Share Your URL

```
https://athena-ai-RANDOM.streamlit.app
```

### 6B. Launch on Platforms

```bash
# Reddit
# - Post on r/learnprogramming, r/HongKong, r/DSE (r/hkeducation)
# - Title: "Built an AI DSE tutor to help students study"
# - Link: your app URL

# Twitter
# - "Just launched a free AI DSE tutor for Hong Kong students"
# - Post your app link

# WeChat Groups
# - Share in DSE prep groups

# School Teachers
# - Email teachers about bulk licenses

# WhatsApp
# - Send to DSE student friends
# - Ask for shares
```

### 6C. Optimize

```bash
# Week 1: Monitor
# - Check: How many free users?
# - Stripe: Any payments?
# - Supabase: Data flowing?

# Week 2: Feedback
# - Ask users: Would you pay?
# - Pricing too high/low?
# - Missing features?

# Week 3: Tweak
# - Adjust pricing if needed
# - Add features based on feedback
# - Push more marketing
```

---

## TROUBLESHOOTING

### "App says 'Please install supabase'"
```bash
pip install supabase==2.4.1
streamlit run streamlit_app.py
```

### "Payment button doesn't work"
```bash
# Check:
1. STRIPE_PUBLIC_KEY is filled (pk_... not blank)
2. STRIPE_SECRET_KEY is filled (sk_... not blank)  
3. Keys are in Streamlit Cloud secrets
4. Redeploy after adding secrets
```

### "Users not saving to database"
```bash
# Check Supabase:
1. Tables created? (SQL ran successfully)
2. SUPABASE_URL correct?
3. SUPABASE_KEY correct?
4. API key has read/write permissions
```

### "Stripe webhook failing"
```bash
# Check:
1. Endpoint URL is EXACTLY: 
   https://athena-ai-RANDOM.streamlit.app/webhook
2. Webhook secret added to Streamlit secrets
3. You're using LIVE keys for live endpoint
```

---

## COSTS (First Month)

| Service | Cost | Notes |
|---------|------|-------|
| Supabase | $25/mo | Can use free tier initially |
| Streamlit Cloud | Free | or $20/mo for pro |
| Stripe | 2.9% + $0.30 | Per transaction (only if you get paid!) |
| Anthropic (Claude) | Usage-based | ~$0.50 per 100 quizzes |
| **Total** | **~$25/mo** | Only if 0-1 users paying |

**Break-even**: ~50 paying users × $9.99 = $500 - $25 cost = $475 profit

---

## SUCCESS METRICS (Track These)

```bash
# In Supabase dashboard SQL Editor:

# Daily active users
SELECT DATE(created_at), COUNT(*) 
FROM quiz_results 
GROUP BY DATE(created_at);

# Premium conversion rate
SELECT 
  ROUND(100.0 * 
    COUNT(DISTINCT subscription user_id) / 
    COUNT(DISTINCT user_id), 2) as conversion_pct
FROM users u
LEFT JOIN subscriptions s ON u.id = s.user_id;

# Total revenue
SELECT 
  COUNT(*) as total_subscriptions,
  SUM(CASE WHEN plan_type='monthly' THEN 9.99 ELSE 99.99 END) as total_revenue
FROM subscriptions
WHERE status = 'active';
```

---

## FINAL CHECKLIST

Before hitting "Deploy":

- [ ] `.env` filled with all keys
- [ ] Supabase tables created (SQL ran)
- [ ] Tested locally with Stripe test card
- [ ] `.gitignore` includes `.env` (don't commit keys!)
- [ ] Pushed to GitHub
- [ ] Deployed to Streamlit Cloud
- [ ] Added secrets to Streamlit Cloud
- [ ] Verified app opens at live URL ✅

Once live:

- [ ] Test guest mode (free tier)
- [ ] Test premium upgrade (Stripe)
- [ ] Check Supabase has data
- [ ] Share URL on social media
- [ ] Monitor first week for issues

---

## YOU'RE DONE! 🎉

**From couch coding to live revenue in ~1 hour.**

Your app is now:
- ✅ **Public** — Anyone can access
- ✅ **Live** — Serving real users
- ✅ **Monetized** — Accepting payments
- ✅ **Scalable** — Handles 1000s of users

**Next**: Wait for first users → Get first payment → Celebrate 🥳

---

## QUESTIONS?

If something breaks:
1. Check logs: Streamlit dashboard
2. Check DB: Supabase SQL editor
3. Check errors: Browser developer tools (F12)
4. Read: DEPLOYMENT.md for more details

**Good luck! You've got this.** 🚀💰
