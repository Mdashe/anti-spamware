CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE email_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    provider_email TEXT NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id INTEGER NOT NULL REFERENCES email_accounts(id) ON DELETE CASCADE,
    provider_email_id TEXT NOT NULL,
    thread_id TEXT,
    subject TEXT,
    sender TEXT,
    recipients TEXT[],
    snippet TEXT,
    received_at TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    cached_body TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE classifications (
    id SERIAL PRIMARY KEY,
    email_id INTEGER NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    confidence DECIMAL(5,4),
    model_version TEXT,
    classified_at TIMESTAMP DEFAULT NOW(),
    source TEXT DEFAULT 'model'
);

CREATE TABLE rules (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    condition_type TEXT NOT NULL,
    condition_value TEXT NOT NULL,
    action TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE email_notes (
    id SERIAL PRIMARY KEY,
    email_id INTEGER NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    note TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);