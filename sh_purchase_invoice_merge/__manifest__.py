# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

{
    "name": "Merge Purchase Orders & Bills | Merge Purchase Orders | Merge Bills | Merge Request For Quotation | Merge PO | Merge RFQ",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Accounting",
    "license": "OPL-1",
    "summary": "Merge Bill Combine Credit Note Append Debit Note Merge Vendor Bills merge Invoice merge accounting Merge Quotations Merge Purchase Order merge quote merge account merge po merge Purchases all in one merge bunch orders merge Odoo",
    "description": """This module useful to Merge Purchase Orders & Bills. Some times required to make a single quote from the multi quotation or merge two different invoices/credit note/debit note/vendor bills. This module helps the user to merge quotation/Purchase order/invoices/credit note/debit note/vendor bills with many more options. When two bills are merged then a new bill is created and that bill will be linked with related Purchase orders.""",
    "version": "0.0.1",
    "depends" : [
                "purchase",
            ],
    "application" : True,
    "data" : [

           'security/ir.model.access.csv',
           'wizard/merge_invoice.xml',
           'wizard/merge_purchase_order.xml',

            ],
    "auto_install":False,
    "installable" : True,
    "images": ["static/description/background.png", ],
    "price": 29,
    "currency": "EUR",
}
