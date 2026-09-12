-- Migration: Initial schema for AITextCoach
-- D1 (SQLite) compatible

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    is_pro INTEGER DEFAULT 0,
    subscription_id TEXT,
    paypal_status TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    ip_address TEXT,
    chars_used INTEGER DEFAULT 0,
    usage_date TEXT DEFAULT (date('now')),
    UNIQUE(email, usage_date)
);

CREATE TABLE IF NOT EXISTS click_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    button_type TEXT NOT NULL,
    click_date TEXT DEFAULT (date('now')),
    count INTEGER DEFAULT 1,
    UNIQUE(button_type, click_date)
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_usage_email_date ON usage_stats(email, usage_date);
CREATE INDEX IF NOT EXISTS idx_click_type_date ON click_stats(button_type, click_date);
