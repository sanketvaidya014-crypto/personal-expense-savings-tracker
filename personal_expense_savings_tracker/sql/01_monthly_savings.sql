WITH m AS (SELECT substr(transaction_date,1,7) month,
SUM(CASE WHEN type='income' THEN amount_paise ELSE 0 END) income_paise,
SUM(CASE WHEN type='expense' THEN amount_paise WHEN type='refund' THEN -amount_paise ELSE 0 END) net_expense_paise
FROM transactions GROUP BY 1)
SELECT month, income_paise/100.0 income_inr, net_expense_paise/100.0 net_expenses_inr,
(income_paise-net_expense_paise)/100.0 savings_inr,
ROUND(100.0*(income_paise-net_expense_paise)/NULLIF(income_paise,0),2) savings_rate_pct
FROM m ORDER BY month;
