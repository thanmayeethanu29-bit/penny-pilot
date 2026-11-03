-- ============================================================
--  Penny Pilot : example SQL queries for the project report
--  Run:  sqlite3 penny_pilot.db < queries.sql
-- ============================================================
.headers on
.mode column

-- Q1. Show all accounts with their current balance (SELECT + JOIN)
SELECT u.name, a.account_name, a.account_type, a.balance
FROM Accounts a
JOIN Users u ON u.user_id = a.user_id
ORDER BY u.name, a.account_name;

-- Q2. Total balance per user (GROUP BY + SUM)
SELECT u.name, SUM(a.balance) AS total_balance
FROM Users u
JOIN Accounts a ON a.user_id = u.user_id
GROUP BY u.user_id;

-- Q3. Latest 5 transactions of Aarav (4-table JOIN + ORDER BY + LIMIT)
SELECT t.txn_date, c.category_name, c.type, t.amount, a.account_name, t.note
FROM Transactions t
JOIN Categories c ON c.category_id = t.category_id
JOIN Accounts   a ON a.account_id  = t.account_id
JOIN Users      u ON u.user_id     = t.user_id
WHERE u.name = 'Aarav Sharma'
ORDER BY t.txn_date DESC, t.transaction_id DESC
LIMIT 5;

-- Q4. Category-wise spending in October 2026 (GROUP BY + HAVING)
SELECT c.category_name, SUM(t.amount) AS total_spent, COUNT(*) AS num_txns
FROM Transactions t
JOIN Categories c ON c.category_id = t.category_id
WHERE c.type = 'Expense'
  AND t.user_id = 1
  AND strftime('%Y-%m', t.txn_date) = '2026-10'
GROUP BY c.category_name
HAVING SUM(t.amount) > 0
ORDER BY total_spent DESC;

-- Q5. Monthly income vs expense vs savings (uses the VIEW)
SELECT * FROM v_monthly_summary WHERE user_id = 1 ORDER BY month;

-- Q6. Budget status with a warning flag (uses the VIEW + CASE)
SELECT category_name, month, limit_amount, spent, remaining,
       CASE
         WHEN spent > limit_amount          THEN 'OVER BUDGET'
         WHEN spent >= 0.8 * limit_amount   THEN 'Almost there'
         ELSE 'Safe'
       END AS status
FROM v_budget_status
WHERE user_id = 1
ORDER BY month, category_name;

-- Q7. Biggest single expense of each user (subquery)
SELECT u.name, t.amount, c.category_name, t.note
FROM Transactions t
JOIN Users u      ON u.user_id = t.user_id
JOIN Categories c ON c.category_id = t.category_id
WHERE c.type = 'Expense'
  AND t.amount = (SELECT MAX(t2.amount)
                  FROM Transactions t2
                  JOIN Categories c2 ON c2.category_id = t2.category_id
                  WHERE c2.type = 'Expense' AND t2.user_id = t.user_id);

-- Q8. Expense categories Meera has never used (LEFT JOIN + IS NULL)
SELECT c.category_name
FROM Categories c
LEFT JOIN Transactions t
       ON t.category_id = c.category_id AND t.user_id = 2
WHERE c.type = 'Expense' AND t.transaction_id IS NULL;

-- Q9. Savings goal progress in percent
SELECT goal_name, target_amount, saved_amount,
       ROUND(100.0 * saved_amount / target_amount, 1) AS percent_done,
       deadline
FROM Goals
WHERE user_id = 1;

-- Q10. Average daily spending in October 2026
SELECT ROUND(SUM(t.amount) / 31.0, 2) AS avg_daily_spend
FROM Transactions t
JOIN Categories c ON c.category_id = t.category_id
WHERE c.type = 'Expense' AND t.user_id = 1
  AND strftime('%Y-%m', t.txn_date) = '2026-10';

-- Q11. UPDATE : add money to a savings goal
UPDATE Goals SET saved_amount = saved_amount + 1000 WHERE goal_name = 'Goa Trip';

-- Q12. DELETE : remove a transaction (trigger restores the balance)
-- DELETE FROM Transactions WHERE transaction_id = 1;
