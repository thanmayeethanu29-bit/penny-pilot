-- ============================================================
--  Penny Pilot : sample data (a fictional student, Aarav)
--  Account balances start at the opening amount; the trigger
--  then adjusts them as transactions are inserted.
-- ============================================================
PRAGMA foreign_keys = ON;

INSERT INTO Users (name, email) VALUES
  ('Aarav Sharma', 'aarav@example.com'),
  ('Meera Iyer',   'meera@example.com');

INSERT INTO Accounts (user_id, account_name, account_type, balance) VALUES
  (1, 'Wallet Cash',  'Cash', 1500),
  (1, 'SBI Savings',  'Bank', 8000),
  (1, 'GPay',         'UPI',  6000),
  (2, 'HDFC Savings', 'Bank', 15000);

INSERT INTO Categories (category_name, type, emoji) VALUES
  ('Salary',        'Income',  '$'),
  ('Pocket Money',  'Income',  '+'),
  ('Freelance',     'Income',  '#'),
  ('Food',          'Expense', 'F'),
  ('Travel',        'Expense', 'T'),
  ('Shopping',      'Expense', 'S'),
  ('Entertainment', 'Expense', 'E'),
  ('Education',     'Expense', 'B'),
  ('Bills',         'Expense', 'R');

-- ---------- October 2026 (Aarav) ----------
INSERT INTO Transactions (user_id, account_id, category_id, amount, txn_date, note) VALUES
  (1, 2, 2, 6000, '2026-10-01', 'Monthly pocket money'),
  (1, 2, 3, 2500, '2026-10-05', 'Logo design for a friend'),
  (1, 3, 4,  180, '2026-10-02', 'Canteen lunch'),
  (1, 3, 4,  420, '2026-10-06', 'Pizza with friends'),
  (1, 1, 4,  150, '2026-10-09', 'Tea and snacks'),
  (1, 3, 4,  650, '2026-10-14', 'Birthday dinner'),
  (1, 3, 4,  210, '2026-10-20', 'Biryani'),
  (1, 3, 5,  300, '2026-10-03', 'Metro card recharge'),
  (1, 1, 5,  120, '2026-10-12', 'Auto fare'),
  (1, 3, 5,  900, '2026-10-22', 'Bus to hometown'),
  (1, 2, 6, 1800, '2026-10-10', 'New headphones'),
  (1, 3, 7,  350, '2026-10-15', 'Movie ticket'),
  (1, 3, 7,  199, '2026-10-18', 'OTT subscription'),
  (1, 2, 8,  800, '2026-10-08', 'Reference books'),
  (1, 2, 9,  399, '2026-10-11', 'Mobile recharge');

-- ---------- November 2026 (Aarav) ----------
INSERT INTO Transactions (user_id, account_id, category_id, amount, txn_date, note) VALUES
  (1, 2, 2, 6000, '2026-11-01', 'Monthly pocket money'),
  (1, 3, 4,  240, '2026-11-01', 'Breakfast and lunch'),
  (1, 3, 5,  300, '2026-11-02', 'Metro card recharge'),
  (1, 1, 4,  130, '2026-11-03', 'Tea and samosa');

-- ---------- Meera (second user, shows data separation) ----------
INSERT INTO Transactions (user_id, account_id, category_id, amount, txn_date, note) VALUES
  (2, 4, 1, 40000, '2026-10-01', 'October salary'),
  (2, 4, 4,  3200, '2026-10-12', 'Groceries'),
  (2, 4, 9,  2500, '2026-10-15', 'Electricity bill');

-- ---------- Budgets ----------
INSERT INTO Budgets (user_id, category_id, month, limit_amount) VALUES
  (1, 4, '2026-10', 1500),
  (1, 5, '2026-10', 1200),
  (1, 6, '2026-10', 1500),
  (1, 7, '2026-10',  700),
  (1, 4, '2026-11', 1800),
  (1, 5, '2026-11', 1000),
  (1, 7, '2026-11',  600);

-- ---------- Savings goals ----------
INSERT INTO Goals (user_id, goal_name, target_amount, saved_amount, deadline) VALUES
  (1, 'New Laptop',       55000, 12000, '2027-03-31'),
  (1, 'Goa Trip',         15000,  4500, '2027-01-15'),
  (2, 'Emergency Fund',  100000, 30000, '2027-06-30');
