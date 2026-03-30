{
    "name": "OPSol PPMC",
    "version": "19.0.1.0.13",
    "summary": "PPMC vendor payments report",
    "description": """
PPMC vendor payments reports and layouts.
""",
    "category": "Accounting",
    "author": "OpenSolution",
    "license": "LGPL-3",
    "depends": ["account", "account_batch_payment"],
    "assets": {
        "web.report_assets_common": [
            "opsol_ppmc/static/src/css/ppmc_report.css",
        ],
        "web.assets_backend": [
            "opsol_ppmc/static/src/js/auto_print_batch_report.js",
        ],
    },
    "data": [
        "reports/ppmc_report.xml",
        "reports/ppmc_header_footer.xml",
        "reports/ppmc_templates.xml",
        "reports/order_virement_report.xml",
        "reports/order_virement_templates.xml",
        "views/account_move_view.xml",
    ],
    "installable": True,
    "application": False,
}
