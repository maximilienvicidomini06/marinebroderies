{
    "name": "OPSol PPMC",
    "version": "19.0.1.0.5",
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
    },
    "data": [
        "reports/ppmc_report.xml",
        "reports/ppmc_header_footer.xml",
        "reports/ppmc_templates.xml",
        "reports/order_virement_report.xml",
        "reports/order_virement_templates.xml",
    ],
    "installable": True,
    "application": False,
}
