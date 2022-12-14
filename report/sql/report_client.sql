SELECT Organization_name, total_sum, inv_count, report_month, report_year
FROM client LEFT JOIN client_report using (client_id)
where report_month = '$rep_month' and report_year = '$rep_year'