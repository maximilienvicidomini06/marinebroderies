/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

// ── Composant Dialog pour l'aperçu PDF ───────────────────────────

class PdfPreviewDialog extends Component {
    static template = "sign_doc_preview.PdfPreviewDialog";
    static components = { Dialog };
    static props = {
        title: String,
        pdfUrl: String,
        onOpenForm: { type: Function, optional: true },
        close: Function,
    };

    openForm() {
        this.props.close();
        if (this.props.onOpenForm) {
            this.props.onOpenForm();
        }
    }
}

// ── Patch du controller natif sign_list ──────────────────────────

import { SignRequestListController } from "@sign/views/sign_list/sign_request_list_controller";

patch(SignRequestListController.prototype, {
    setup() {
        super.setup();
        this._previewOrm = useService("orm");
        this._previewDialog = useService("dialog");
    },

    async openRecord(record) {
        const recId = record.resId;
        let pdfUrl = null;
        let docName = "";

        try {
            const result = await this._previewOrm.read(
                "sign.request",
                [recId],
                ["display_name", "template_id", "state"]
            );

            if (result.length) {
                const rec = result[0];
                docName = rec.display_name || "";

                // 1. Document signé → cherche le PDF final en pièce jointe
                if (rec.state === "signed") {
                    const attachments = await this._previewOrm.searchRead(
                        "ir.attachment",
                        [
                            ["res_model", "=", "sign.request"],
                            ["res_id", "=", recId],
                            ["mimetype", "=", "application/pdf"],
                        ],
                        ["id"],
                        { limit: 1, order: "id desc" }
                    );
                    if (attachments.length) {
                        pdfUrl = `/web/content/${attachments[0].id}?inline=true`;
                    }
                }

                // 2. Fallback → PDF original du template
                if (!pdfUrl && rec.template_id) {
                    const tpl = await this._previewOrm.read(
                        "sign.template",
                        [rec.template_id[0]],
                        ["attachment_id"]
                    );
                    if (tpl.length && tpl[0].attachment_id) {
                        pdfUrl = `/web/content/${tpl[0].attachment_id[0]}?inline=true`;
                    }
                }
            }
        } catch (e) {
            console.error("[SignDocPreview] Erreur chargement PDF:", e);
        }

        if (pdfUrl) {
            this._previewDialog.add(PdfPreviewDialog, {
                title: docName,
                pdfUrl: pdfUrl,
                onOpenForm: () => super.openRecord(record),
            });
            return;
        }

        // Pas de PDF trouvé → comportement standard
        return super.openRecord(record);
    }
});
