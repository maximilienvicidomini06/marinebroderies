# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """
    Populate the x_customer_delivery_date on existing purchase.order.line records.

    This migration script identifies purchase order lines that were created
    through the MTO route from a sales order and copies the commitment date
    from the sales order (or sales order line) to the new custom field.
    """
    _logger.info("Starting migration to populate x_customer_delivery_date on purchase.order.line.")

    query = """
        UPDATE
            purchase_order_line pol
        SET
            x_customer_delivery_date = COALESCE(so.date_order::date)
        FROM
            stock_move sm
        JOIN
            sale_order_line sol ON sm.sale_line_id = sol.id
        JOIN
            sale_order so ON sol.order_id = so.id
        WHERE
            pol.id = sm.purchase_line_id
            AND pol.x_customer_delivery_date IS NULL
            AND sm.sale_line_id IS NOT NULL;
    """
    cr.execute(query)

    updated_rows = cr.rowcount
    _logger.info(f"Migration complete. Updated {updated_rows} purchase.order.line records.")
