-- ============================================
-- PocketTrack — PostgreSQL Schema
-- HOW TO RUN: Open pgAdmin → your DB →
--   Query Tool → paste this → Run (F5)
-- ============================================

-- TABLE 1: users
-- Stores your login credentials + password reset info
CREATE TABLE IF NOT EXISTS users (
    id                    SERIAL PRIMARY KEY,
    username              VARCHAR(50)  NOT NULL UNIQUE,
    password_hash         VARCHAR(255) NOT NULL,
    security_question     TEXT         NOT NULL DEFAULT '',
    security_answer_hash  VARCHAR(255) NOT NULL DEFAULT '',
    created_at            TIMESTAMP    DEFAULT NOW()
);

-- TABLE 2: transactions
-- Every income and expense you add
CREATE TABLE IF NOT EXISTS transactions (
    id          SERIAL PRIMARY KEY,
    type        VARCHAR(10)  NOT NULL CHECK (type IN ('income', 'expense')),
    amount      DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    category    VARCHAR(20)  NOT NULL DEFAULT 'Other'
                    CHECK (category IN ('Food', 'Travel', 'Fun', 'Other', 'Income')),
    description TEXT,
    date        DATE         NOT NULL DEFAULT CURRENT_DATE,
    month       VARCHAR(7)   NOT NULL,   -- Format: YYYY-MM
    user_id     INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  TIMESTAMP    DEFAULT NOW()
);

-- TABLE 3: friends
-- Unique friend names — no duplicates allowed
CREATE TABLE IF NOT EXISTS friends (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    user_id    INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP    DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- TABLE 4: friend_transactions
-- Money you owe or will receive per friend entry
CREATE TABLE IF NOT EXISTS friend_transactions (
    id               SERIAL PRIMARY KEY,
    friend_id        INTEGER       NOT NULL REFERENCES friends(id) ON DELETE CASCADE,
    total_amount     DECIMAL(10,2) NOT NULL CHECK (total_amount > 0),
    paid_amount      DECIMAL(10,2) NOT NULL DEFAULT 0,
    remaining_amount DECIMAL(10,2) GENERATED ALWAYS AS (total_amount - paid_amount) STORED,
    type             VARCHAR(10)   NOT NULL CHECK (type IN ('pay', 'receive')),
    status           VARCHAR(15)   NOT NULL DEFAULT 'pending'
                         CHECK (status IN ('pending', 'completed')),
    description      TEXT,
    date             DATE          NOT NULL DEFAULT CURRENT_DATE,
    month            VARCHAR(7)    NOT NULL,
    user_id          INTEGER       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at       TIMESTAMP     DEFAULT NOW()
);

-- INDEXES (for faster queries)
CREATE INDEX IF NOT EXISTS idx_tx_month       ON transactions(month);
CREATE INDEX IF NOT EXISTS idx_tx_type        ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_tx_user_id     ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_ft_friend_id   ON friend_transactions(friend_id);
CREATE INDEX IF NOT EXISTS idx_ft_month       ON friend_transactions(month);
CREATE INDEX IF NOT EXISTS idx_ft_status      ON friend_transactions(status);
CREATE INDEX IF NOT EXISTS idx_ft_user_id     ON friend_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_friends_user_id ON friends(user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- MIGRATIONS: Add user_id columns for multi-user support
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE friend_transactions ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE friends ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
