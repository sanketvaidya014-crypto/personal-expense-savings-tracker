SELECT substr(transaction_date,1,7) month, category,
SUM(CASE WHEN type='expense' THEN amount_paise ELSE -amount_paise END)/100.0 net_spending_inr
FROM transactions WHERE type IN ('expense','refund') GROUP BY 1,2 ORDER BY month, net_spending_inr DESC;
