#!/usr/bin/env python3
"""
Penny Pilot - a command-line Money Tracker built on SQLite.

Run it:   python money_tracker.py
Reset DB: python money_tracker.py --reset
Demo:     python money_tracker.py --demo   (prints sample reports, no typing)

Only the Python standard library is used - nothing to install.
"""
import os
import sqlite3
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(HERE, "penny_pilot.db")
BAR_WIDTH = 20


# ------------------------------------------------------------------
# Database setup
# ------------------------------------------------------------------
def read_sql(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read()


def connect(reset=False):
    if reset and os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    first_run = not os.path.exists(DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if first_run:
        conn.executescript(read_sql("schema.sql"))
        conn.executescript(read_sql("sample_data.sql"))
        conn.commit()
        print("Fresh database created with sample data.\n")
    return conn


# ------------------------------------------------------------------
# Small helpers
# ------------------------------------------------------------------
def money(x):
    return f"Rs {x:,.2f}"


def bar(spent, limit):
    """Text progress bar, e.g. [#########-----------]  45%"""
    pct = 0 if limit == 0 else spent / limit
    filled = min(BAR_WIDTH, int(round(pct * BAR_WIDTH)))
    return f"[{'#' * filled}{'-' * (BAR_WIDTH - filled)}] {pct * 100:5.0f}%"


def ask(prompt, default=None):
    text = input(prompt).strip()
    return text if text else default


def ask_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value > 0:
                return value
            print("  Please enter a number greater than 0.")
        except ValueError:
            print("  That is not a number, try again.")


def ask_date(prompt):
    while True:
        text = ask(prompt + " [today]: ", date.today().isoformat())
        try:
            date.fromisoformat(text)
            return text
        except ValueError:
            print("  Use the format YYYY-MM-DD.")


def pick(rows, label_fn, title):
    """Show a numbered list and return the chosen row."""
    print(f"\n{title}")
    for i, row in enumerate(rows, 1):
        print(f"  {i}. {label_fn(row)}")
    while True:
        choice = input("Choose a number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(rows):
            return rows[int(choice) - 1]
        print("  Invalid choice.")


def month_prompt():
    default = date.today().strftime("%Y-%m")
    return ask(f"Month YYYY-MM [{default}]: ", default)


# ------------------------------------------------------------------
# Features
# ------------------------------------------------------------------
def choose_user(conn):
    users = conn.execute("SELECT * FROM Users ORDER BY user_id").fetchall()
    return pick(users, lambda u: f"{u['name']} ({u['email']})", "Who is using Penny Pilot?")


def show_accounts(conn, user):
    rows = conn.execute(
        "SELECT account_name, account_type, balance FROM Accounts WHERE user_id = ?",
        (user["user_id"],),
    ).fetchall()
    print("\n--- Your accounts ---")
    for r in rows:
        print(f"  {r['account_name']:<14} {r['account_type']:<5} {money(r['balance']):>16}")
    total = sum(r["balance"] for r in rows)
    print(f"  {'TOTAL':<20} {money(total):>16}")


def add_transaction(conn, user, kind):
    cats = conn.execute(
        "SELECT * FROM Categories WHERE type = ? ORDER BY category_name", (kind,)
    ).fetchall()
    accounts = conn.execute(
        "SELECT * FROM Accounts WHERE user_id = ?", (user["user_id"],)
    ).fetchall()
    cat = pick(cats, lambda c: c["category_name"], f"{kind} category:")
    acc = pick(accounts, lambda a: f"{a['account_name']} ({money(a['balance'])})", "Account:")
    amount = ask_float("Amount: ")
    when = ask_date("Date")
    note = ask("Note (optional): ", "")
    conn.execute(
        "INSERT INTO Transactions (user_id, account_id, category_id, amount, txn_date, note) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user["user_id"], acc["account_id"], cat["category_id"], amount, when, note),
    )
    conn.commit()
    print(f"  Saved {kind.lower()} of {money(amount)} under {cat['category_name']}.")
    if kind == "Expense":
        check_budget_alert(conn, user, cat["category_id"], when[:7])


def check_budget_alert(conn, user, category_id, month):
    row = conn.execute(
        "SELECT * FROM v_budget_status WHERE user_id = ? AND month = ? "
        "AND category_name = (SELECT category_name FROM Categories WHERE category_id = ?)",
        (user["user_id"], month, category_id),
    ).fetchone()
    if row is None:
        return
    if row["spent"] > row["limit_amount"]:
        print(f"  !! ALERT: you are OVER your {row['category_name']} budget by "
              f"{money(row['spent'] - row['limit_amount'])}.")
    elif row["spent"] >= 0.8 * row["limit_amount"]:
        print(f"  Heads up: {row['category_name']} budget is at "
              f"{row['spent'] / row['limit_amount'] * 100:.0f}%.")


def list_transactions(conn, user, limit=10):
    rows = conn.execute(
        """SELECT t.transaction_id, t.txn_date, c.category_name, c.type, t.amount,
                  a.account_name, t.note
           FROM Transactions t
           JOIN Categories c ON c.category_id = t.category_id
           JOIN Accounts   a ON a.account_id  = t.account_id
           WHERE t.user_id = ?
           ORDER BY t.txn_date DESC, t.transaction_id DESC LIMIT ?""",
        (user["user_id"], limit),
    ).fetchall()
    print(f"\n--- Last {limit} transactions ---")
    print(f"  {'ID':<4} {'Date':<11} {'Category':<14} {'Amount':>12}  Account / Note")
    for r in rows:
        sign = "+" if r["type"] == "Income" else "-"
        print(f"  {r['transaction_id']:<4} {r['txn_date']:<11} {r['category_name']:<14} "
              f"{sign}{r['amount']:>11,.2f}  {r['account_name']} / {r['note'] or ''}")
    return rows


def delete_transaction(conn, user):
    list_transactions(conn, user)
    tid = ask("ID of the transaction to delete (blank to cancel): ")
    if not tid or not tid.isdigit():
        print("  Cancelled.")
        return
    cur = conn.execute(
        "DELETE FROM Transactions WHERE transaction_id = ? AND user_id = ?",
        (int(tid), user["user_id"]),
    )
    conn.commit()
    print("  Deleted; account balance restored." if cur.rowcount else "  No such transaction.")


def monthly_report(conn, user, month=None):
    month = month or month_prompt()
    s = conn.execute(
        "SELECT * FROM v_monthly_summary WHERE user_id = ? AND month = ?",
        (user["user_id"], month),
    ).fetchone()
    print(f"\n=== Report for {month} ===")
    if s is None:
        print("  No transactions this month.")
        return
    print(f"  Income  : {money(s['total_income'])}")
    print(f"  Expenses: {money(s['total_expense'])}")
    print(f"  Savings : {money(s['net_savings'])}")
    if s["total_income"] > 0:
        rate = s["net_savings"] / s["total_income"] * 100
        print(f"  You saved {rate:.0f}% of what you earned.")

    rows = conn.execute(
        """SELECT c.category_name, SUM(t.amount) AS total
           FROM Transactions t JOIN Categories c ON c.category_id = t.category_id
           WHERE t.user_id = ? AND c.type = 'Expense'
             AND strftime('%Y-%m', t.txn_date) = ?
           GROUP BY c.category_name ORDER BY total DESC""",
        (user["user_id"], month),
    ).fetchall()
    if rows:
        print("\n  Where your money went:")
        top = rows[0]["total"]
        for r in rows:
            print(f"   {r['category_name']:<14} {bar(r['total'], top)} {money(r['total'])}")
        print(f"\n  Biggest leak: {rows[0]['category_name']}")


def budget_status(conn, user, month=None):
    month = month or month_prompt()
    rows = conn.execute(
        "SELECT * FROM v_budget_status WHERE user_id = ? AND month = ? ORDER BY category_name",
        (user["user_id"], month),
    ).fetchall()
    print(f"\n=== Budgets for {month} ===")
    if not rows:
        print("  No budgets set for this month.")
        return
    for r in rows:
        flag = "OVER!" if r["spent"] > r["limit_amount"] else (
            "close" if r["spent"] >= 0.8 * r["limit_amount"] else "ok")
        print(f"  {r['category_name']:<14} {bar(r['spent'], r['limit_amount'])} "
              f"{money(r['spent'])} / {money(r['limit_amount'])}  {flag}")


def set_budget(conn, user):
    cats = conn.execute(
        "SELECT * FROM Categories WHERE type = 'Expense' ORDER BY category_name"
    ).fetchall()
    cat = pick(cats, lambda c: c["category_name"], "Set a budget for:")
    month = month_prompt()
    limit = ask_float("Monthly limit: ")
    conn.execute(
        """INSERT INTO Budgets (user_id, category_id, month, limit_amount)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(user_id, category_id, month)
           DO UPDATE SET limit_amount = excluded.limit_amount""",
        (user["user_id"], cat["category_id"], month, limit),
    )
    conn.commit()
    print(f"  Budget for {cat['category_name']} in {month} set to {money(limit)}.")


def goals_menu(conn, user):
    while True:
        goals = conn.execute(
            "SELECT * FROM Goals WHERE user_id = ?", (user["user_id"],)
        ).fetchall()
        print("\n=== Savings goals ===")
        for g in goals:
            print(f"  {g['goal_name']:<14} {bar(g['saved_amount'], g['target_amount'])} "
                  f"{money(g['saved_amount'])} / {money(g['target_amount'])}  by {g['deadline']}")
        if not goals:
            print("  No goals yet.")
        print("\n  a) add goal   d) deposit to a goal   b) back")
        choice = ask("  > ", "b").lower()
        if choice == "a":
            name = ask("Goal name: ")
            target = ask_float("Target amount: ")
            deadline = ask_date("Deadline")
            conn.execute(
                "INSERT INTO Goals (user_id, goal_name, target_amount, deadline) VALUES (?,?,?,?)",
                (user["user_id"], name, target, deadline),
            )
            conn.commit()
        elif choice == "d" and goals:
            goal = pick(goals, lambda g: g["goal_name"], "Deposit to:")
            amt = ask_float("Amount: ")
            conn.execute(
                "UPDATE Goals SET saved_amount = saved_amount + ? WHERE goal_id = ?",
                (amt, goal["goal_id"]),
            )
            conn.commit()
            print("  Nice, one step closer!")
        else:
            return


# ------------------------------------------------------------------
# Main menu
# ------------------------------------------------------------------
MENU = """
===== PENNY PILOT : Money Tracker =====
 1. Add expense            6. Set a budget
 2. Add income             7. Savings goals
 3. Recent transactions    8. My accounts
 4. Monthly report         9. Delete a transaction
 5. Budget status          0. Exit
"""


def main_menu(conn, user):
    print(f"\nWelcome, {user['name']}!")
    while True:
        print(MENU)
        choice = ask("Choose: ", "")
        if choice == "1":
            add_transaction(conn, user, "Expense")
        elif choice == "2":
            add_transaction(conn, user, "Income")
        elif choice == "3":
            list_transactions(conn, user)
        elif choice == "4":
            monthly_report(conn, user)
        elif choice == "5":
            budget_status(conn, user)
        elif choice == "6":
            set_budget(conn, user)
        elif choice == "7":
            goals_menu(conn, user)
        elif choice == "8":
            show_accounts(conn, user)
        elif choice == "9":
            delete_transaction(conn, user)
        elif choice == "0":
            print("Bye! Keep tracking.")
            return
        else:
            print("Please choose a number from the menu.")


def demo(conn):
    user = conn.execute("SELECT * FROM Users WHERE user_id = 1").fetchone()
    show_accounts(conn, user)
    list_transactions(conn, user, 5)
    monthly_report(conn, user, "2026-10")
    budget_status(conn, user, "2026-10")


if __name__ == "__main__":
    connection = connect(reset="--reset" in sys.argv)
    try:
        if "--demo" in sys.argv:
            demo(connection)
        else:
            main_menu(connection, choose_user(connection))
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
    finally:
        connection.close()
