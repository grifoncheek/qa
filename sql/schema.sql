-- Учебная схема «Банк» для практики SQL.
-- Совместима с SQLite 3.25+ и PostgreSQL 12+ (даты хранятся в ISO 8601).
-- Порядок создания: clients -> accounts -> cards -> transactions.

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS clients;

CREATE TABLE clients (
    client_id    INTEGER PRIMARY KEY,
    full_name    TEXT NOT NULL,
    phone        TEXT NOT NULL UNIQUE,
    email        TEXT,
    birth_date   DATE,
    city         TEXT,
    status       TEXT NOT NULL DEFAULT 'active'
                 CHECK (status IN ('active', 'blocked', 'closed')),
    created_at   TIMESTAMP NOT NULL
);

CREATE TABLE accounts (
    account_id      INTEGER PRIMARY KEY,
    client_id       INTEGER NOT NULL REFERENCES clients (client_id),
    account_number  TEXT NOT NULL UNIQUE,
    account_type    TEXT NOT NULL
                    CHECK (account_type IN ('current', 'savings', 'deposit', 'credit')),
    currency        TEXT NOT NULL CHECK (currency IN ('RUB', 'USD', 'EUR')),
    balance         NUMERIC(14, 2) NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'frozen', 'closed')),
    opened_at       TIMESTAMP NOT NULL
);

CREATE TABLE cards (
    card_id             INTEGER PRIMARY KEY,
    account_id          INTEGER NOT NULL REFERENCES accounts (account_id),
    card_number_masked  TEXT NOT NULL,
    card_type           TEXT NOT NULL CHECK (card_type IN ('debit', 'credit')),
    payment_system      TEXT NOT NULL CHECK (payment_system IN ('MIR', 'VISA', 'MasterCard')),
    status              TEXT NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'blocked', 'expired')),
    issued_at           DATE NOT NULL,
    expiry_date         DATE NOT NULL
);

CREATE TABLE transactions (
    transaction_id      INTEGER PRIMARY KEY,
    account_id          INTEGER NOT NULL REFERENCES accounts (account_id),
    operation_type      TEXT NOT NULL
                        CHECK (operation_type IN ('payment', 'transfer_in', 'transfer_out',
                                                  'cash_withdrawal', 'fee', 'refund')),
    amount              NUMERIC(14, 2) NOT NULL CHECK (amount > 0),
    currency            TEXT NOT NULL CHECK (currency IN ('RUB', 'USD', 'EUR')),
    status              TEXT NOT NULL
                        CHECK (status IN ('completed', 'pending', 'failed', 'reversed')),
    counterparty_account TEXT,
    description         TEXT,
    created_at          TIMESTAMP NOT NULL
);

CREATE INDEX idx_accounts_client_id ON accounts (client_id);
CREATE INDEX idx_cards_account_id ON cards (account_id);
CREATE INDEX idx_transactions_account_date ON transactions (account_id, created_at);
CREATE INDEX idx_transactions_created_at ON transactions (created_at);
