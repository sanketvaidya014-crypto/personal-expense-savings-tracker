SELECT transaction_id,transaction_date,category,account,amount_paise/100.0 amount_inr,description
FROM transactions WHERE type='expense' ORDER BY amount_paise DESC, transaction_id LIMIT 10;
