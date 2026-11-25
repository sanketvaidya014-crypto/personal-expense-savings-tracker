SELECT category, COUNT(*) transactions, SUM(amount_paise)/100.0 income_inr
FROM transactions WHERE type='income' GROUP BY category ORDER BY income_inr DESC;
