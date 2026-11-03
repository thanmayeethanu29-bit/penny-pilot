-- ============================================================
--  Penny Pilot : Money Tracker  |  Database schema (SQLite)
--  Tables are in 3NF. Triggers keep account balances correct.
-- ============================================================

PRAGMA foreign_keys = ON;

DROP VIEW    IF EXISTS v_monthly_summary;
DROP VIEW    IF EXISTS v_budget_status;
DROP TRIGGER IF EXISTS trg_txn_after_insert;
DROP TRIGGER IF EXISTS trg_txn_after_delete;
DROP TABLE   IF EXISTS Goals;
DROP TABLE   IF EXISTS Budgets;
DROP TABLE   IF EXISTS Transactions;
DROP TABLE   IF EXISTS Categories;
DROP TABLE   IF EXISTS Accounts;
DROP TABLE   IF EXISTS Users;

-- 1. Users ---------------------------------------------------
CREATE TABLE Users (
    user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    created_at  TEXT NOT NULL DEFAULT (date('now'))
);

-- 2. Accounts (Cash, Bank, UPI, Card) ------------------------
CREATE TABLE Accounts (
    account_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    account_name  TEXT NOT NULL,
    account_type  TEXT NOT NULL CHECK (account_type IN ('Cash','Bank','UPI','Card')),
    balance       REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    UNIQUE (user_id, account_name)
);

-- 3. Categories ----------------------------------------------
CREATE TABLE Categories (
    category_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name  TEXT NOT NULL UNIQUE,
    type           TEXT NOT NULL CHECK (type IN ('Income','Expense')),
    emoji          TEXT NOT NULL DEFAULT '*'
);

-- 4. Transactions --------------------------------------------
CREATE TABLE Transactions (
    transaction_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    account_id      INTEGER NOT NULL,
    category_id     INTEGER NOT NULL,
    amount          REAL NOT NULL CHECK (amount > 0),
    txn_date        TEXT NOT NULL DEFAULT (date('now')),
    note            TEXT,
    FOREIGN KEY (user_id)     REFERENCES Users(user_id)           ON DELETE CASCADE,
    FOREIGN KEY (account_id)  REFERENCES Accounts(account_id)     ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

-- 5. Budgets (monthly limit per category) --------------------
CREATE TABLE Budgets (
    budget_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    category_id   INTEGER NOT NULL,
    month         TEXT NOT NULL,              -- format YYYY-MM
    limit_amount  REAL NOT NULL CHECK (limit_amount > 0),
    FOREIGN KEY (user_id)     REFERENCES Users(user_id)       ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id),
    UNIQUE (user_id, category_id, month)
);

-- 6. Savings goals (the creative extra) ----------------------
CREATE TABLE Goals (
    goal_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    goal_name      TEXT NOT NULL,
    target_amount  REAL NOT NULL CHECK (target_amount > 0),
    saved_amount   REAL NOT NULL DEFAULT 0 CHECK (saved_amount >= 0),
    deadline       TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- ============================================================
--  TRIGGERS : keep Accounts.balance in sync automatically
-- ============================================================
CREATE TRIGGER trg_txn_after_insert
AFTER INSERT ON Transactions
BEGIN
    UPDATE Accounts
       SET balance = balance +
           CASE (SELECT type FROM Categories WHERE category_id = NEW.category_id)
                WHEN 'Income' THEN  NEW.amount
                ELSE               -NEW.amount
           END
     WHERE account_id = NEW.account_id;
END;

CREATE TRIGGER trg_txn_after_delete
AFTER DELETE ON Transactions
BEGIN
    UPDATE Accounts
       SET balance = balance -
           CASE (SELECT type FROM Categories WHERE category_id = OLD.category_id)
                WHEN 'Income' THEN  OLD.amount
                ELSE               -OLD.amount
           END
     WHERE account_id = OLD.account_id;
END;

-- ============================================================
--  VIEWS : ready-made reports
-- ============================================================
CREATE VIEW v_monthly_summary AS
SELECT t.user_id,
       strftime('%Y-%m', t.txn_date) AS month,
       SUM(CASE WHEN c.type = 'Income'  THEN t.amount ELSE 0 END) AS total_income,
       SUM(CASE WHEN c.type = 'Expense' THEN t.amount ELSE 0 END) AS total_expense,
       SUM(CASE WHEN c.type = 'Income'  THEN t.amount ELSE -t.amount END) AS net_savings
FROM Transactions t
JOIN Categories c ON c.category_id = t.category_id
GROUP BY t.user_id, strftime('%Y-%m', t.txn_date);

CREATE VIEW v_budget_status AS
SELECT b.user_id,
       b.month,
       c.category_name,
       c.emoji,
       b.limit_amount,
       COALESCE(SUM(t.amount), 0) AS spent,
       b.limit_amount - COALESCE(SUM(t.amount), 0) AS remaining
FROM Budgets b
JOIN Categories c ON c.category_id = b.category_id
LEFT JOIN Transactions t
       ON t.user_id = b.user_id
      AND t.category_id = b.category_id
      AND strftime('%Y-%m', t.txn_date) = b.month
GROUP BY b.budget_id;

-- Helpful indexes for faster reports
CREATE INDEX idx_txn_user_date ON Transactions(user_id, txn_date);
CREATE INDEX idx_txn_category  ON Transactions(category_id);
