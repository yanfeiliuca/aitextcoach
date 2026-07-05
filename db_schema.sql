-- AI Text Coach Database Schema
-- Run this once to initialize the PostgreSQL database

-- Users table (Pro subscribers + free users)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_pro BOOLEAN DEFAULT FALSE,
    subscription_id VARCHAR(255),
    paypal_status VARCHAR(50) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage tracking (daily quota)
CREATE TABLE IF NOT EXISTS usage_stats (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    ip_address VARCHAR(45),
    chars_used INTEGER DEFAULT 0,
    usage_date DATE DEFAULT CURRENT_DATE,
    UNIQUE(email, usage_date)
);

-- Click analytics
CREATE TABLE IF NOT EXISTS click_stats (
    id SERIAL PRIMARY KEY,
    button_type VARCHAR(50) NOT NULL,
    click_date DATE DEFAULT CURRENT_DATE,
    count INTEGER DEFAULT 1,
    UNIQUE(button_type, click_date)
);

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_usage_email_date ON usage_stats(email, usage_date);
CREATE INDEX IF NOT EXISTS idx_click_type_date ON click_stats(button_type, click_date);
