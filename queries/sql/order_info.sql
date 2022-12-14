SELECT Inv_id, Invoice_date, Name, Organization_name, Status, From_address, To_address, Price FROM invoice
 JOIN client on (Orderer_id=Client_id)
 JOIN personal on (Personal_id=P_id) where Inv_id = '$invoice_id'