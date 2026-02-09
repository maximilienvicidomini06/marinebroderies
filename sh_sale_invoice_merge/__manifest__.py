# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Merge Sale Orders & Invoices",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Accounting",
    "license": "OPL-1",
    "summary": "Merge Invoice Merge Credit Note Merge Debit Note Merge Vendor Bills Merge Bill Merge Accounting Merge Quotations Merge Sale Order Merge Quote Merge Account Merge SO Merge Sales All In One Merge Bunch Orders Merge Sale Orders Merge Invoices Merge Quotation Merge Combine Invoice Combine Credit Note Combine Debit Note Combine Vendor Bills Combine Bill Combine Accounting Combine Quotations Combine Sale Order Combine Quote Combine Account Combine SO Combine Sales Combine Sale Orders Combine Invoices Combine Quotation Combine Bills Odoo Merge Credit Notes Merge Debit Notes Merge Vendor Bill Merge Bills Merge SO Invoice Mere Sale With Invoice Merge Sales With Invoice Merge Sale Orders With Invoice Merge Sale Order With Invoice",
    "description": """This module useful to Merge Sale Orders & Invoices. Some times required to make a single quote from the multi quotation or merge two different invoices/credit note/debit note/vendor bills. This module helps the user to merge quotation/sale order/invoices/credit note/debit note/vendor bills with many more options. When two invoices are merged then a new invoice is created and that invoice will be linked with related sale orders.""",
    "version": "0.0.1",
    "depends" : [
                "sale_management",
            ],
    "application" : True,
    "data" : [

            'security/ir.model.access.csv',
            'wizard/merge_invoice.xml',
            'wizard/merge_sale_order.xml',
            ],
    "auto_install":False,
    "installable" : True,
    "images": ["static/description/background.png", ],
    "price": 26,
    "currency": "EUR"
}
