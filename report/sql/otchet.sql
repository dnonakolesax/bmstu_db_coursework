SELECT
    invoice.Inv_id,
    personal.Name,
    invoice.Invoice_date,
    invoice.Invoice_cargo_weight
FROM
    invoice
        JOIN
    personal ON (Personal_id = P_id)
