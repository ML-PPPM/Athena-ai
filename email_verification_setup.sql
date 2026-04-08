-- Email verification table for storing temporary verification codes
-- Run this in your Supabase SQL editor

CREATE TABLE IF NOT EXISTS email_verifications (
    email VARCHAR(255) PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add email_verified column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_email_verifications_expires_at ON email_verifications(expires_at);

-- Optional: Create a function to clean up expired verification codes
CREATE OR REPLACE FUNCTION cleanup_expired_verifications()
RETURNS void AS $$
BEGIN
    DELETE FROM email_verifications WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Optional: Set up a cron job to run cleanup (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-verifications', '0 */6 * * *', 'SELECT cleanup_expired_verifications();');