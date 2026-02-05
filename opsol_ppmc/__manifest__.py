{
    "name": "OPSol PPMC",
    "version": "19.0.1.0.0",
    "summary": "PPMC vendor payments report",
    "category": "Accounting",
    "author": "OpenSolution",
    "license": "LGPL-3",
    "depends": ["account"],
    "assets": {
        "web.report_assets_common": [
            "opsol_ppmc/static/src/css/ppmc_report.css",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/ppmc_report_wizard.xml",
        "reports/ppmc_report.xml",
        "reports/ppmc_header_footer.xml",
        "reports/ppmc_templates.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
}
