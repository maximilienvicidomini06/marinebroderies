"""Integration tests: run on a disposable Odoo 19 Enterprise database."""
import json
from pathlib import Path
from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestMonacoReport(TransactionCase):
    def test_portable_configuration(self):
        report = self.env.ref('opsol_monaco_tax_report.monaco_report')
        expected = json.loads(Path(__file__).with_name('source_contract.json').read_text())
        self.assertEqual(len(report.line_ids), len(expected['lines']))
        self.assertEqual(len(report.column_ids), 1)
        self.assertEqual(report.country_id, self.env.ref('base.fr'))
        self.assertEqual(report.root_report_id, self.env.ref('account.generic_tax_report'))
        self.assertFalse(report.custom_handler_model_id)
        self.assertFalse(report.return_type_ids)
        lines = {line.code: line for line in report.line_ids}
        for row in expected['lines']:
            line = lines[row['code']]
            for key in ('name', 'sequence', 'hierarchy_level'):
                self.assertEqual(line.with_context(lang='en_US')[key], row[key])
            self.assertEqual(line.parent_id.code, row['parent_code'])
        expressions = {(line.code, e.label): e for line in report.line_ids for e in line.expression_ids}
        self.assertEqual(len(expressions), len(expected['expressions']))
        for row in expected['expressions']:
            expression = expressions[(row['line_code'], row['label'])]
            for key in ('engine', 'formula', 'subformula', 'date_scope', 'carryover_target'):
                self.assertEqual(expression[key], row[key])
            if expression.engine == 'tax_tags':
                self.assertTrue(self.env['account.account.tag']._get_tax_tags(expression.formula, report.country_id.id))
        metadata = self.env['ir.model.data'].search([
            ('module', '=', 'opsol_monaco_tax_report'),
            ('model', 'in', ['account.report', 'account.report.line', 'account.report.column', 'account.report.expression']),
        ])
        self.assertTrue(metadata)
        self.assertTrue(all(metadata.mapped('noupdate')))
