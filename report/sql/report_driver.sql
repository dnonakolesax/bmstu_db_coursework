SELECT Name, cargo_weight, inv_amount, rep_month, rep_year
FROM personal JOIN personal_report on (P_id=personal_id)
where rep_month = '$rep_month' and rep_year = '$rep_year'