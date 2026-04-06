# 📖 QUICKSTART GUIDE — Athena AI Premium

**Your production-ready, monetized DSE tutor is ready!**

## 🎯 What You Have

✅ **Complete AI app** with:
- Authentication (Supabase)
- Payment processing (Stripe)
- Usage limits & freemium tiers
- Quiz saving & stats
- Full deployment config

## 🚀 Launch in 3 Steps

### STEP 1: Setup Accounts (10 min)

1. **Supabase** (free tier):
   - Go to https://supabase.com
   - Create project
   - Copy `SUPABASE_URL` and `SUPABASE_ANON_KEY`
   - Run SQL from [DEPLOYMENT.md](DEPLOYMENT.md) to create tables

2. **Stripe** (payments):
   - Go to https://stripe.com
   - Create account
   - Copy `STRIPE_PUBLIC_KEY` and `STRIPE_SECRET_KEY`

3. **Anthropic** (already have):
   - Your `ANTHROPIC_API_KEY` is ready ✅

### STEP 2: Configure Locally (5 min)

```bash
# Copy template
cp .env.example .env

# Edit with your keys
nano .env
# SUPABASE_URL=https://...
# SUPABASE_KEY=...
# STRIPE_PUBLIC_KEY=...
# STRIPE_SECRET_KEY=...
# ANTHROPIC_API_KEY=...
```

### STEP 3: Deploy (5 min)

```bash
# Option A: Streamlit Cloud (easiest)
streamlit login
streamlit deploy

# Option B: Docker (if you prefer)
docker build -t athena-ai .
docker run -p 8501:8501 athena-ai
```

**That's it!** Your app is now live. 🎉

## 💰 How Money Flows

```
User pays $9.99/month on Stripe
  ↓
Stripe webhook notifies app
  ↓
App marks user as premium in Supabase
  ↓
User unlocks unlimited features
  ↓
You get paid (Stripe keeps 2.9% + $0.30)
```

## 📊 Key Files

| File | Purpose |
|------|---------|
| `streamlit_app.py` | Main app - add features here |
| `database.py` | Save user data - queries work automatically |
| `payments.py` | Stripe integration - webhook handling |
| `auth.py` | Login/signup UI - freemium model |
| `config.py` | Settings & pricing tiers |
| `DEPLOYMENT.md` | **READ THIS** before going live |

## 🆓 Free vs 💰 Premium

**Free Tier:**
- 5 quizzes/day
- 2 study plans/day
- 3 past papers/day

**Premium ($9.99/mo):**
- Unlimited everything
- Ad-free
- Priority support

Users can try free → upgrade when they hit limits.

## 🧪 Test Before Launch

```bash
# 1. Start locally
streamlit run streamlit_app.py

# 2. Try these flows:
# - Click "Guest Mode" → take 5 quizzes (then hit limit)
# - See "Upgrade" button appears
# - Click it → goes to Stripe test checkout
# - Use test card: 4242 4242 4242 4242

# 3. Check Supabase dashboard
# - quota_usage table updated
# - subscriptions table shows purchase

# 4. Upgrade again → sees unlimited features
```

## ⚠️ Before Going Live (Critical!)

- [ ] Updated pricing in `config.py`
- [ ] Replaced all "demo" references
- [ ] Tested payment flow end-to-end
- [ ] Added Terms of Service
- [ ] Added Privacy Policy
- [ ] Set `ENVIRONMENT=production` in secrets
- [ ] Enabled error logging (Sentry)
- [ ] Backed up database

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete checklist.

## 💼 Business Numbers

**Assumptions:**
- 100 active free users
- 10% convert to premium ($10/month each)
- 90% monthly retention

**Monthly Revenue:**
- 10 paying users × $9.99 = $99.90
- Stripe fee (2.9% + $0.30) = ~$3.20
- **Net: $96.70/month**

**Costs:**
- Supabase: $25/month
- Streamlit Cloud: $0 (free tier) or $20/month
- **Total: $25/month**

**Profit: $71.70/month** (from 100 users)

At scale (1000 users, 10% conversion):
- Revenue: $999/month
- Costs: ~$100/month
- **Profit: $900/month** 💰

## 🎓 How to Grow

1. **Reddit/Twitter**: HSK students looking for tutors
2. **Schools**: Sell to teachers for class license
3. **WeChat**: Hong Kong student groups
4. **SEO**: Optimize for "DSE tutor", "mock exam generator"
5. **Referral**: $5 credit for each friend referred

## 🐛 Troubleshooting

**"Database not connected"**
- Check `SUPABASE_URL` matches prod URL
- Verify tables exist in Supabase dashboard
- Restart app: `streamlit run streamlit_app.py`

**"Stripe payment failed"**
- Using live keys (pk_live_, sk_live_)?
- Not test keys (pk_test_)?
- Webhook URL correct in Stripe dashboard?

**"User data not saving"**
- Check `usage_logs` table has today's record
- Verify `quiz_results` table has new row
- Database connection = working ✅

## 📞 Support

- **Logs**: `streamlit logs` (Streamlit Cloud)
- **Database**: Supabase dashboard
- **Payments**: Stripe dashboard
- **Code**: GitHub Issues

## ⏭️ Next Steps

1. ✅ Complete DEPLOYMENT.md
2. ✅ Set up Supabase + Stripe
3. ✅ Test locally
4. ✅ Deploy to Streamlit Cloud
5. ✅ Send to 10 beta users
6. ✅ Get feedback on pricing
7. ✅ Launch publicly
8. ✅ Market on social media

**Expected time: 2-3 weeks to first customers.**

---

**Ready?** → [DEPLOYMENT.md](DEPLOYMENT.md)

**Questions?** → Open GitHub Issue

**Let's get paid!** 🚀💰
