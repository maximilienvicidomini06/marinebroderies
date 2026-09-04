from collections import defaultdict

from odoo import models
from odoo.tools import SQL


class FinancialPartnerLedgerReportHandler(models.AbstractModel):
    _name = "opsol.financial.partner.ledger.report.handler"
    _inherit = "account.partner.ledger.report.handler"
    _description = "Financial Partner Ledger Custom Handler"

    def _custom_options_initializer(self, report, options, previous_options):
        super()._custom_options_initializer(report, options, previous_options)
        options["custom_display_config"]["templates"].update({
            "AccountReportFilters": "opsol_produit_financier.FinancialPartnerLedgerFilters",
            "AccountReportLineName": "opsol_produit_financier.FinancialPartnerLedgerLineName",
        })
        options["forced_domain"] = options.get("forced_domain", []) + [
            ("financial_quantity", "!=", 0),
            ("partner_id.is_financial_product", "=", True),
        ]

    def _get_report_line_partners(self, options, partner, partner_values, level_shift=0):
        line = super()._get_report_line_partners(
            options, partner, partner_values, level_shift=level_shift
        )
        if partner:
            line["name"] = partner.display_name[:128]
        return line

    def _get_additional_column_aml_values(self):
        return SQL(
            "%s account_move_line.financial_quantity AS financial_quantity,",
            super()._get_additional_column_aml_values(),
        )

    def _query_partners(self, report, options):
        partners_results = super()._query_partners(report, options)
        queries = []

        for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
            query = report._get_report_query(column_group_options, "from_beginning")
            queries.append(SQL(
                """
                    SELECT
                        account_move_line.partner_id AS partner_id,
                        %(column_group_key)s AS column_group_key,
                        SUM(account_move_line.financial_quantity) AS financial_quantity
                    FROM %(table_references)s
                    WHERE %(search_condition)s
                    GROUP BY account_move_line.partner_id
                """,
                column_group_key=column_group_key,
                table_references=query.from_clause,
                search_condition=query.where_clause,
            ))

        quantities = defaultdict(dict)
        if queries:
            self.env.cr.execute(SQL(" UNION ALL ").join(queries))
            for result in self.env.cr.dictfetchall():
                quantities[result["partner_id"]][result["column_group_key"]] = (
                    result["financial_quantity"] or 0.0
                )

        for partner, partner_values in partners_results:
            partner_id = partner.id if partner else None
            for column_group_key, values in partner_values.items():
                quantity = quantities[partner_id].get(column_group_key, 0.0)
                values["financial_quantity_cumulative"] = quantity
                values["financial_average_price"] = (
                    values["balance"] / quantity if quantity else None
                )

        return partners_results

    def _build_partner_lines(self, report, options, level_shift=0):
        lines = []
        totals_by_column_group = {
            column_group_key: {
                total: 0.0
                for total in ("debit", "credit", "amount", "balance")
            }
            for column_group_key in options["column_groups"]
        }

        for partner, results in self._query_partners(report, options):
            partner_values = defaultdict(dict)
            for column_group_key in options["column_groups"]:
                partner_sum = results.get(column_group_key, {})
                values = partner_values[column_group_key]
                for label in ("debit", "credit", "amount", "balance"):
                    values[label] = partner_sum.get(label, 0.0)
                    totals_by_column_group[column_group_key][label] += values[label]

                values["financial_quantity_cumulative"] = partner_sum.get(
                    "financial_quantity_cumulative", 0.0
                )
                values["financial_average_price"] = partner_sum.get(
                    "financial_average_price"
                )

            lines.append(
                self._get_report_line_partners(
                    options, partner, partner_values, level_shift=level_shift
                )
            )

        return lines, totals_by_column_group

    def _get_initial_balance_values(self, partner_ids, options):
        initial_values = super()._get_initial_balance_values(partner_ids, options)
        report = self.env.ref("account_reports.partner_ledger_report")
        queries = []

        for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
            initial_options = self._get_options_initial_balance(column_group_options)
            query = report._get_report_query(
                initial_options,
                "from_beginning",
                domain=[("partner_id", "in", partner_ids)],
            )
            queries.append(SQL(
                """
                    SELECT
                        account_move_line.partner_id,
                        %(column_group_key)s AS column_group_key,
                        SUM(account_move_line.financial_quantity) AS financial_quantity
                    FROM %(table_references)s
                    WHERE %(search_condition)s
                    GROUP BY account_move_line.partner_id
                """,
                column_group_key=column_group_key,
                table_references=query.from_clause,
                search_condition=query.where_clause,
            ))

        if queries:
            self.env.cr.execute(SQL(" UNION ALL ").join(queries))
            for result in self.env.cr.dictfetchall():
                values = initial_values[result["partner_id"]][result["column_group_key"]]
                quantity = result["financial_quantity"] or 0.0
                values["financial_quantity_cumulative"] = quantity
                values["financial_average_price"] = (
                    values["balance"] / quantity if quantity else None
                )

        for partner_values in initial_values.values():
            for values in partner_values.values():
                quantity = values.get("financial_quantity_cumulative", 0.0)
                values.setdefault("financial_quantity_cumulative", quantity)
                values.setdefault(
                    "financial_average_price",
                    values["balance"] / quantity if quantity else None,
                )

        return initial_values

    def _get_aml_values(self, options, partner_ids, offset=0, limit=None):
        aml_values = super()._get_aml_values(options, partner_ids, offset=offset, limit=limit)
        initial_values = self._get_initial_balance_values(partner_ids, options)

        for partner_id, results in aml_values.items():
            cumulative_quantity = defaultdict(float)
            cumulative_balance = defaultdict(float)
            for column_group_key, values in initial_values[partner_id].items():
                cumulative_quantity[column_group_key] = values["financial_quantity_cumulative"]
                cumulative_balance[column_group_key] = values["balance"]

            for result in results:
                column_group_key = result["column_group_key"]
                cumulative_quantity[column_group_key] += result["financial_quantity"] or 0.0
                cumulative_balance[column_group_key] += result["balance"]
                result["financial_quantity_cumulative"] = cumulative_quantity[column_group_key]
                result["financial_average_price"] = (
                    cumulative_balance[column_group_key] / cumulative_quantity[column_group_key]
                    if cumulative_quantity[column_group_key]
                    else None
                )

        return aml_values
