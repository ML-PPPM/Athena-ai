# Supabase Database Setup Guide

This guide will help you create the necessary tables in Supabase for Athena AI to work properly.

## Setup Instructions

### 1. Go to Supabase Dashboard
Navigate to [https://supabase.com](https://supabase.com) and open your project.

### 2. Open SQL Editor
Click on **SQL Editor** in the left sidebar, then click **New Query**.

### 3. Create the Required Tables

Copy and paste each SQL statement below into the SQL Editor and click **Run**.

---

## Table 1: Users

```sql
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  is_premium BOOLEAN DEFAULT FALSE,
  premium_until TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Table 2: Subscriptions

```sql
CREATE TABLE IF NOT EXISTS subscriptions (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  stripe_subscription_id TEXT,
  plan_type TEXT NOT NULL,
  status TEXT DEFAULT 'active',
  started_at TIMESTAMP NOT NULL,
  renews_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

---

## Table 3: Usage Logs

```sql
CREATE TABLE IF NOT EXISTS usage_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  feature TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at);
```

---

## Table 4: Quiz Results

```sql
CREATE TABLE IF NOT EXISTS quiz_results (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  subject TEXT NOT NULL,
  topic TEXT NOT NULL,
  score INT NOT NULL,
  total INT NOT NULL,
  percentage INT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_quiz_results_user_id ON quiz_results(user_id);
CREATE INDEX idx_quiz_results_created_at ON quiz_results(created_at);
```

---

## Table 5: Study Plans

```sql
CREATE TABLE IF NOT EXISTS study_plans (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  subject TEXT NOT NULL,
  plan_text TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_study_plans_user_id ON study_plans(user_id);
CREATE INDEX idx_study_plans_created_at ON study_plans(created_at);
```

---

## Verification

To verify all tables are created correctly, run this query:

```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

You should see:
- users
- subscriptions
- usage_logs
- quiz_results
- study_plans

---

## Row Level Security (Optional but Recommended)

To add security so users can only see their own data:

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_plans ENABLE ROW LEVEL SECURITY;

-- Create policies (users can only access their own data)
CREATE POLICY "Users can read only their own data" ON users
  FOR SELECT USING (auth.uid()::TEXT = id);

CREATE POLICY "Users can insert their own subscriptions" ON subscriptions
  FOR INSERT WITH CHECK (auth.uid()::TEXT = user_id);

CREATE POLICY "Users can read only their own subscriptions" ON subscriptions
  FOR SELECT USING (auth.uid()::TEXT = user_id);

-- Add similar policies for other tables as needed
```

---

## What's Next?

After creating the tables, your Athena AI app will be able to:
- ✅ Store user subscription information
- ✅ Track usage limits
- ✅ Save quiz results
- ✅ Store study plans
- ✅ Manage premium features

The app will now work smoothly without database errors!
