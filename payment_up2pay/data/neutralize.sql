-- disable aps payment provider
UPDATE payment_provider
   SET up2pay_site = NULL,
       up2pay_rank = NULL,
       up2pay_identifier = NULL,
       up2pay_key = NULL;
