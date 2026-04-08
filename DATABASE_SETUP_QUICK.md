# Quick Fix: Database Tables Setup

## The Problem
You got this error because the `subscriptions` table doesn't exist in your Supabase database:
```
APIError: Could not find the table 'public.subscriptions'
```

## The Solution

### 3 Simple Steps to Fix It:

**Step 1: Open Your Supabase Dashboard**
- Go to [https://supabase.com](https://supabase.com)
- Log in and select your project
- Click **SQL Editor** on the left sidebar

**Step 2: Create the Tables**
- Click **New Query**
- Copy and paste **ALL** the SQL from the `SUPABASE_SETUP.md` file
- Click the **Run** button (or press Ctrl+Enter)

**Step 3: Refresh Your App**
- Go back to your app at `http://localhost:8505`
- Press F5 or refresh the page
- Done! ✅

---

## What Gets Created

The SQL creates 5 tables for Athena AI:

| Table | Purpose |
|-------|---------|
| **users** | Store user profile data |
| **subscriptions** | Track premium subscriptions |
| **usage_logs** | Track feature usage (quizzes, plans, etc.) |
| **quiz_results** | Save quiz scores and performance |
| **study_plans** | Save generated study plans |

---

## Quick Reference

If you want to just create the essential table first, run this:

```sql
CREATE TABLE IF NOT EXISTS subscriptions (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  stripe_subscription_id TEXT,
  plan_type TEXT NOT NULL,
  status TEXT DEFAULT 'active',
  started_at TIMESTAMP NOT NULL,
  renews_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

Then run the other commands when you're ready.

---

## Need Help?

See the full setup guide in: **SUPABASE_SETUP.md**
