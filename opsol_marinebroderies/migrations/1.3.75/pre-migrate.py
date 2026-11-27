# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1
          FROM information_schema.columns
         WHERE table_name = 'stock_picking'
           AND column_name = 'calendar_color'
        """
    )
    if not cr.fetchone():
        return

    cr.execute(
        """
        ALTER TABLE stock_picking
        ALTER COLUMN calendar_color TYPE integer
        USING CASE
            WHEN calendar_color ~ '^[0-9]+$' THEN calendar_color::integer
            ELSE 0
        END
        """
    )
