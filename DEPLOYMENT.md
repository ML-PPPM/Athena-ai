# 🚀 Deployment Guide — Athena AI

Complete guide to launching your monetized app to production.

## Phase 1: Setup (15 minutes)

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Create new project
4. Save your `SUPABASE_URL` and `SUPABASE_ANON_KEY`

### 1.2 Create Database Tables

In Supabase SQL Editor, run:

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    is_premium BOOLEAN DEFAULT false,
    premium_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Usage logs (daily limits)
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE DEFAULT CURRENT_DATE,
    quiz_count INT DEFAULT 0,
    past_paper_count INT DEFAULT 0,
    plan_count INT DEFAULT 0,
    learn_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    plan_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    started_at TIMESTAMP DEFAULT NOW(),
    renews_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Quiz results
CREATE TABLE quiz_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(255),
    topic VARCHAR(255),
    score INT,
    total INT,
    percentage INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Study plans
CREATE TABLE study_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(255),
    plan_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id, date);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_quiz_results_user_id ON quiz_results(user_id);
CREATE INDEX idx_study_plans_user_id ON study_plans(user_id);
```

### 1.3 Create Stripe Account

1. Go to [stripe.com](https://stripe.com)
2. Create account
3. Get **Publishable Key** and **Secret Key** from dashboard
4. Save to `.env` file

## Phase 2: Local Testing (30 minutes)

### 2.1 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.2 Create `.env` File

Copy `.env.example` and fill in:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2.3 Create `.streamlit/secrets.toml`

For local dev, create this file with same keys as `.env`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJI..."
STRIPE_PUBLIC_KEY = "pk_test_..."
STRIPE_SECRET_KEY = "sk_test_..."
DEBUG = true
ENVIRONMENT = "development"
```

### 2.4 Test Locally

```bash
streamlit run streamlit_app.py
```

Test these flows:
- ✅ Guest login (demo mode)
- ✅ Quiz generation + usage tracking
- ✅ Premium upgrade button (redirects to Stripe)
- ✅ Study plan generation
- ✅ Logout

## Phase 3: Deploy to Streamlit Cloud (10 minutes)

### 3.1 Push to GitHub

```bash
git add .
git commit -m "Add production features"
git push origin main
```

### 3.2 Deploy

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Deploy an app"
3. Select your GitHub repo (`ML-PPPM/Athena-ai`)
4. Fill in details:
   - URL: `streamlit_app.py`
   - Branch: `main`

### 3.3 Add Secrets to Streamlit Cloud

In Streamlit Cloud deployment settings, add all keys from `.env`:

```
ANTHROPIC_API_KEY = sk-ant-...
SUPABASE_URL = https://...
SUPABASE_KEY = eyJ...
STRIPE_PUBLIC_KEY = pk_live_...
STRIPE_SECRET_KEY = sk_live_...
ENVIRONMENT = production
DEBUG = false
```

## Phase 4: Setup Stripe Webhooks (10 minutes)

### 4.1 Add Webhook Endpoint

1. Stripe Dashboard → Webhooks
2. Add endpoint:
   - URL: `https://your-app.streamlit.app/webhook`
   - Events: `checkout.session.completed`, `customer.subscription.deleted`

3. Copy signing secret → Add to `.env` as `STRIPE_WEBHOOK_SECRET`

### 4.2 Test Webhook

Use Stripe CLI or test cards:
- **Card**: `4242 4242 4242 4242`
- **Expiry**: Any future date
- **CVC**: Any 3 digits

## Phase 5: Monitor & Optimize (Ongoing)

### 5.1 Usage Monitoring

```python
# Check via Supabase dashboard
SELECT user_id, COUNT(*) as quizzes_completed 
FROM quiz_results 
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY user_id
ORDER BY quizzes_completed DESC;
```

### 5.2 Subscribe to Logs

```bash
# Real-time logs from Streamlit Cloud
streamlit logs my-app
```

### 5.3 Setup Error Monitoring

Add to `streamlit_app.py`:

```python
import sentry_sdk
sentry_sdk.init("your-sentry-dsn")
```

## Finance Checklist

- [ ] Set Stripe pricing
- [ ] Update Terms of Service
- [ ] Create Privacy Policy
- [ ] Add refund policy
- [ ] Setup tax implications

## Monetization Tips

1. **Freemium** → Focus on free experience
2. **Conversion** → Make upgrade obvious (limit nags)
3. **Retention** → Save user scores/plans
4. **Virality** → Share feature (export plans)

## Troubleshooting

### Supabase Connection Fails
```python
# Add to streamlit_app.py for debugging
if not db.is_connected():
    st.error("Database connection failed")
    st.write(settings.SUPABASE_URL)  # Debug
```

### Stripe Webhook Not Working
- Check signing secret matches
- Verify endpoint URL is public
- Test with Stripe CLI: `stripe trigger checkout.session.completed`

### Users Stuck on Auth Page
- Check `SUPABASE_URL` in secrets
- Verify user table exists
- Check `.streamlit/` folder permissions

## Next Steps

1. ✅ Test 5+ payment flows
2. ✅ Get 10 beta users
3. ✅ Gather feedback on pricing
4. ✅ Optimize weak conversion steps
5. ✅ Launch publicly

---

**Expected launch time: 2-3 weeks** from setup to first paying customers.

Total cost:
- Supabase: $25/month (PostgreSQL + hosting)
- Streamlit Cloud: Free tier → $20/month
- Stripe: 2.9% + $0.30 per transaction
- **Total: ~$50/month** + payment fees

ROI calculation:
- 100 users × $9.99/month = $999
- Costs: ~$50 + payment fees (~$30) = $80
- **Profit: $920/month from 100 users**
