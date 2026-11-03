# Penny Pilot - Money Tracker (DBMS Mini Project)

A simple command-line **money tracker** built with **Python + SQLite**.
Track income and expenses, set monthly budgets, get over-budget alerts and
save towards goals. Nothing to install: it uses only Python's standard library.

## Features
- Multiple users, each with several accounts (Cash, Bank, UPI, Card)
- Add income and expenses by category
- **Account balances update automatically** (database triggers)
- Monthly report with text bar charts and a "biggest leak" category
- Monthly **budgets per category** with live alerts when you reach 80% or go over
- **Savings goals** with progress bars (the creative extra)
- Delete a transaction and the balance is restored automatically

## How to run
```bash
python money_tracker.py            # start the app (database is created on first run)
python money_tracker.py --demo     # print sample reports without typing anything
python money_tracker.py --reset    # rebuild the database from scratch
python run_queries.py              # run all the example SQL queries from queries.sql
```
Requires Python 3.8 or newer. No extra packages.

## Project files
| File | Purpose |
|---|---|
| `schema.sql` | Tables, constraints, triggers, views and indexes |
| `sample_data.sql` | Demo users, accounts, transactions, budgets and goals |
| `queries.sql` | 12 example queries (JOIN, GROUP BY, HAVING, subquery, UPDATE, DELETE) |
| `money_tracker.py` | The application (menu-driven) |
| `run_queries.py` | Runs `queries.sql` and prints the results |

## Database design

### Tables
| Table | Columns |
|---|---|
| **Users** | user_id (PK), name, email (unique), created_at |
| **Accounts** | account_id (PK), user_id (FK), account_name, account_type, balance |
| **Categories** | category_id (PK), category_name (unique), type (Income/Expense), emoji |
| **Transactions** | transaction_id (PK), user_id (FK), account_id (FK), category_id (FK), amount, txn_date, note |
| **Budgets** | budget_id (PK), user_id (FK), category_id (FK), month, limit_amount |
| **Goals** | goal_id (PK), user_id (FK), goal_name, target_amount, saved_amount, deadline |

### Relationships (ER diagram)
```
Users 1 ──< Accounts 1 ──< Transactions >── 1 Categories 1 ──< Budgets >── 1 Users
  │                              ^
  │                              └── also Users 1 ──< Transactions
  └──< Goals
```
- One user has many accounts, transactions, budgets and goals (1:N)
- One account has many transactions (1:N)
- One category has many transactions and many budgets (1:N)

### Normalization
All tables are in **3NF**: every column depends only on its table's primary key.
Category names are stored once in `Categories`, not repeated in each transaction.

### Constraints used
`PRIMARY KEY`, `FOREIGN KEY` (with `ON DELETE CASCADE`), `UNIQUE`, `NOT NULL`,
`CHECK` (amount > 0, valid account/category types), `DEFAULT`.

### Advanced features
- **Triggers** `trg_txn_after_insert` / `trg_txn_after_delete` keep `Accounts.balance` correct.
- **Views** `v_monthly_summary` and `v_budget_status` power the reports.
- **Indexes** speed up per-user and per-category lookups.

## Upload to GitHub
```bash
cd penny-pilot
git init
git add .
git commit -m "Penny Pilot: money tracker DBMS mini project"
git branch -M main
git remote add origin https://github.com/<your-username>/penny-pilot.git
git push -u origin main
```
(Create an empty repository named `penny-pilot` on GitHub first.)

## Ideas to extend it
- Monthly CSV export
- Recurring transactions (rent, subscriptions)
- A web front end with Flask
- Transfers between accounts

## Author
Made by `<your name>` - `<your college / course>`
