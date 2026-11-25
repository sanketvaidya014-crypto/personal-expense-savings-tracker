SELECT category,
SUM(CASE WHEN type='expense' THEN amount_paise ELSE 0 END)/100.0 gross_expenses_inr,
SUM(CASE WHEN type='refund' THEN amount_paise ELSE 0 END)/100.0 refunds_inr,
SUM(CASE WHEN type='expense' THEN amount_paise ELSE -amount_paise END)/100.0 net_spending_inr
FROM transactions WHERE type IN ('expense','refund') GROUP BY category ORDER BY net_spending_inr DESC;
