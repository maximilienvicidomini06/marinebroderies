import base64

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

SAMPLE = (
    "MANDAT;041126;691332;Entretien, amenag.fourn.prest.;CP-1;CP-1;;;;;A;FOURNISSEUR A;;;;0;0;D;D;100,50;100,50;100,50;0;G;0;;;\n"
    "MANDAT;041126;691332;Entretien, amenag.fourn.prest.;CP-1;CP-1;;;;;A;FOURNISSEUR A;;;;0;0;D;D;100,50;100,50;100,50;0;G;0;;;\n"
    "MANDAT;041126;691332;Entretien, amenag.fourn.prest.;CP-2;CP-2;;;;;A;FOURNISSEUR B;;;;0;0;D;C;20;-20;0;20;G;0;;;\n"
    "MANDAT;041126;691380;Améliorations & travaux neufs;CP-3;CP-3;;;;;A;FOURNISSEUR B;;;;0;0;D;D;1000;1000;1000;0;G;0;;;\n"
)


@tagged("post_install", "-at_install")
class TestMandatImport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        plan = cls.env["account.analytic.plan"].create({"name": "Budget test"})
        cls.acc_entretien = cls.env["account.analytic.account"].create(
            {"name": "Entretien", "plan_id": plan.id})
        cls.acc_travaux = cls.env["account.analytic.account"].create(
            {"name": "Travaux", "plan_id": plan.id})
        cls.env["mandat.budget.mapping"].create(
            {"code": "691332", "analytic_account_id": cls.acc_entretien.id})

    def _wizard(self, content=SAMPLE, **kw):
        return self.env["mandat.import.wizard"].create(
            {"file": base64.b64encode(content.encode("cp1252")), "filename": "m.txt", **kw})

    def test_full_flow(self):
        wiz = self._wizard(create_partners=True)
        wiz.action_parse()
        self.assertEqual(len(wiz.line_ids), 4)
        self.assertEqual(wiz.count_unmapped, 1)
        with self.assertRaises(UserError):
            wiz.action_import()
        wiz.line_ids.filtered(lambda l: l.budget_code == "691380").analytic_account_id = self.acc_travaux
        wiz.action_import()

        lines = self.env["account.analytic.line"].search([("mandat_ref", "like", "CP-")])
        self.assertEqual(len(lines), 4)
        self.assertAlmostEqual(sum(lines.mapped("amount")), -(100.5 * 2 - 20 + 1000))
        plan_col = self.acc_entretien.root_plan_id._column_name()
        self.assertEqual(lines.filtered(lambda l: l.mandat_ref == "CP-2")[plan_col], self.acc_entretien)
        self.assertEqual(lines.filtered(lambda l: l.mandat_ref == "CP-2").amount, 20)
        self.assertTrue(lines.partner_id)
        # correspondance 691380 mémorisée
        self.assertTrue(self.env["mandat.budget.mapping"].search([("code", "=", "691380")]))

        # second import du même fichier : tout est détecté comme doublon
        wiz2 = self._wizard()
        wiz2.action_parse()
        self.assertEqual(wiz2.count_duplicate, 4)
        with self.assertRaises(UserError):
            wiz2.action_import()

    def test_bad_file(self):
        with self.assertRaises(UserError):
            self._wizard(content="foo;bar\n").action_parse()
