# -*- coding: utf-8 -*-
import base64
from datetime import datetime

from lxml import etree

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_repr

# ---------------------------------------------------------------------------
# IMPORTANT : le namespace ci-dessous doit correspondre EXACTEMENT au XSD
# attendu par la banque. La valeur la plus répandue pour la v02 (et celle
# utilisée par les modules OCA) est "urn:swift:xsd:$pain.001.001.02".
# Certaines banques utilisent une variante (ex. "urn:sepade:xsd:pain.001.001.02").
# En cas de rejet par le portail bancaire, ajuster PAIN_NS en premier lieu.
# ---------------------------------------------------------------------------
PAIN_NS = "urn:swift:xsd:$pain.001.001.02"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"


class AccountBatchPayment(models.Model):
    _inherit = "account.batch.payment"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _pain02_clean(self, value, max_len=140):
        """Translittère en ASCII latin et tronque (jeu de caractères SEPA restreint)."""
        if not value:
            return ""
        try:
            from unidecode import unidecode
            value = unidecode(value)
        except ImportError:
            # unidecode est normalement fourni par Odoo ; sinon on dégrade proprement
            value = value.encode("ascii", "ignore").decode("ascii")
        return value[:max_len].strip()

    def _pain02_sub(self, parent, tag, text=None):
        el = etree.SubElement(parent, tag)
        if text is not None:
            el.text = text
        return el

    def _pain02_bic(self, parent_fininstnid, bic):
        """Ajoute le BIC, ou un Othr/NOTPROVIDED si absent (IBAN-only)."""
        if bic:
            self._pain02_sub(parent_fininstnid, "BIC", bic.replace(" ", "").upper())
        else:
            othr = etree.SubElement(parent_fininstnid, "Othr")
            self._pain02_sub(othr, "Id", "NOTPROVIDED")

    # ------------------------------------------------------------------
    # Génération du XML pain.001.001.02
    # ------------------------------------------------------------------
    def _generate_pain_001_001_02(self):
        self.ensure_one()

        if self.batch_type != "outbound":
            raise UserError(_("Le format pain.001.001.02 ne concerne que les virements (lots sortants)."))

        payments = self.payment_ids
        if not payments:
            raise UserError(_("Aucun paiement dans ce lot."))

        journal = self.journal_id
        company = journal.company_id
        debtor_bank = journal.bank_account_id
        if not debtor_bank:
            raise UserError(_("Le journal « %s » n'a pas de compte bancaire configuré.") % journal.name)
        if not debtor_bank.sanitized_acc_number:
            raise UserError(_("Le compte bancaire du journal « %s » n'a pas d'IBAN.") % journal.name)

        nb_txs = len(payments)
        ctrl_sum = sum(payments.mapped("amount"))

        # --- Racine ---
        nsmap = {None: PAIN_NS, "xsi": XSI_NS}
        document = etree.Element("Document", nsmap=nsmap)
        root = etree.SubElement(document, "pain.001.001.02")

        # --- Group Header ---
        grphdr = etree.SubElement(root, "GrpHdr")
        msg_id = ("OS%s-%s" % (self.id, datetime.now().strftime("%Y%m%d%H%M%S")))[:35]
        self._pain02_sub(grphdr, "MsgId", msg_id)
        self._pain02_sub(grphdr, "CreDtTm", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        self._pain02_sub(grphdr, "NbOfTxs", str(nb_txs))
        self._pain02_sub(grphdr, "CtrlSum", float_repr(ctrl_sum, 2))
        # <Grpg> est OBLIGATOIRE en .02 (supprimé en .03) : GRPD / MIXD / SNGL
        self._pain02_sub(grphdr, "Grpg", "MIXD")
        initg = etree.SubElement(grphdr, "InitgPty")
        self._pain02_sub(initg, "Nm", self._pain02_clean(company.name, 70))

        # --- Payment Information (un seul bloc, regroupement MIXD) ---
        pmtinf = etree.SubElement(root, "PmtInf")
        self._pain02_sub(pmtinf, "PmtInfId", msg_id)
        self._pain02_sub(pmtinf, "PmtMtd", "TRF")
        pmttpinf = etree.SubElement(pmtinf, "PmtTpInf")
        svclvl = etree.SubElement(pmttpinf, "SvcLvl")
        self._pain02_sub(svclvl, "Cd", "SEPA")
        exec_date = (self.date or fields.Date.context_today(self)).strftime("%Y-%m-%d")
        self._pain02_sub(pmtinf, "ReqdExctnDt", exec_date)

        dbtr = etree.SubElement(pmtinf, "Dbtr")
        self._pain02_sub(dbtr, "Nm", self._pain02_clean(company.name, 70))
        dbtracct = etree.SubElement(pmtinf, "DbtrAcct")
        dbtracct_id = etree.SubElement(dbtracct, "Id")
        self._pain02_sub(dbtracct_id, "IBAN", debtor_bank.sanitized_acc_number)
        dbtragt = etree.SubElement(pmtinf, "DbtrAgt")
        dbtragt_fin = etree.SubElement(dbtragt, "FinInstnId")
        self._pain02_bic(dbtragt_fin, debtor_bank.bank_id.bic if debtor_bank.bank_id else False)
        self._pain02_sub(pmtinf, "ChrgBr", "SLEV")

        # --- Transactions ---
        for payment in payments:
            creditor_bank = payment.partner_bank_id
            if not creditor_bank or not creditor_bank.sanitized_acc_number:
                raise UserError(
                    _("Le paiement « %s » n'a pas de compte bancaire bénéficiaire (IBAN) valide.")
                    % (payment.name or payment.id)
                )

            tx = etree.SubElement(pmtinf, "CdtTrfTxInf")
            pmtid = etree.SubElement(tx, "PmtId")
            e2e = (payment.name or str(payment.id)).replace("/", "").replace(" ", "")[:35]
            self._pain02_sub(pmtid, "EndToEndId", e2e or "NOTPROVIDED")

            amt = etree.SubElement(tx, "Amt")
            instdamt = self._pain02_sub(amt, "InstdAmt", float_repr(payment.amount, 2))
            instdamt.set("Ccy", payment.currency_id.name or "EUR")

            cdtragt = etree.SubElement(tx, "CdtrAgt")
            cdtragt_fin = etree.SubElement(cdtragt, "FinInstnId")
            self._pain02_bic(cdtragt_fin, creditor_bank.bank_id.bic if creditor_bank.bank_id else False)

            cdtr = etree.SubElement(tx, "Cdtr")
            self._pain02_sub(cdtr, "Nm", self._pain02_clean(payment.partner_id.name, 70))
            cdtracct = etree.SubElement(tx, "CdtrAcct")
            cdtracct_id = etree.SubElement(cdtracct, "Id")
            self._pain02_sub(cdtracct_id, "IBAN", creditor_bank.sanitized_acc_number)

            communication = payment.memo or payment.name or ""
            if communication:
                rmtinf = etree.SubElement(tx, "RmtInf")
                self._pain02_sub(rmtinf, "Ustrd", self._pain02_clean(communication, 140))

        # Pas de BOM, déclaration XML, UTF-8
        return etree.tostring(document, xml_declaration=True, encoding="UTF-8", pretty_print=True)

    def action_generate_pain_001_001_02(self):
        self.ensure_one()
        xml_bytes = self._generate_pain_001_001_02()
        filename = "PAIN_001_001_02_%s.xml" % (self.name or str(self.id)).replace("/", "_").replace(" ", "_")
        attachment = self.env["ir.attachment"].create({
            "name": filename,
            "datas": base64.b64encode(xml_bytes),
            "res_model": "account.batch.payment",
            "res_id": self.id,
            "mimetype": "application/xml",
        })
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }
