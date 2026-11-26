SELECT substr(transaction_date,1,7) month,type,COUNT(*) transactions,SUM(amount_paise)/100.0 amount_inr
FROM transactions GROUP BY 1,2 ORDER BY 1,2;
