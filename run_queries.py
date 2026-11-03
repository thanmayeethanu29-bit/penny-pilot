#!/usr/bin/env python3
"""
Runs every query in queries.sql and prints the results as tables.
Handy if you do not have the sqlite3 command-line tool installed.

Usage:  python run_queries.py
"""
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(HERE, "penny_pilot.db")


def print_table(headers, rows):
    widths = [len(h) for h in headers]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(str(value)))
    line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(line)
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print("  ".join(str(v).ljust(widths[i]) for i, v in enumerate(row)))


def main():
    if not os.path.exists(DB_FILE):
        print("Database not found. Run  python money_tracker.py  once first.")
        return
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    with open(os.path.join(HERE, "queries.sql"), encoding="utf-8") as f:
        text = f.read()

    # Drop sqlite3 shell commands (.headers / .mode) and split into statements
    text = "\n".join(l for l in text.splitlines() if not l.startswith("."))
    blocks = [b.strip() for b in re.split(r";\s*(?:\n|$)", text) if b.strip()]

    for block in blocks:
        comments = [l for l in block.splitlines() if l.strip().startswith("--")]
        sql = "\n".join(l for l in block.splitlines() if not l.strip().startswith("--")).strip()
        if not sql:
            continue
        print("\n" + "=" * 70)
        for c in comments:
            print(c.strip("- ").strip())
        print("=" * 70)
        cur = conn.execute(sql)
        if cur.description:
            print_table([d[0] for d in cur.description], cur.fetchall())
        else:
            # Not committed on purpose: running the examples never changes your data
            print(f"OK ({cur.rowcount} row(s) changed, rolled back after the demo)")
    conn.rollback()
    conn.close()


if __name__ == "__main__":
    main()
