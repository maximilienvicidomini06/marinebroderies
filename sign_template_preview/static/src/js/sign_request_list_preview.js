/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

export class SignRequestListController extends ListController {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.previewState = useState({
            pdfUrl: null,
            selectedId: null,
            loading: false,
            error: null,
            documentName: null,
            isSigned: false,
        });
    }

    async openRecord(record) {
        const recId = record.resId;

        // Toggle : re-clic sur la même ligne ferme le panneau
        if (this.previewState.selectedId === recId) {
            this.previewState.selectedId = null;
            this.previewState.pdfUrl = null;
            this.previewState.documentName = null;
            this.previewState.error = null;
            this.previewState.isSigned = false;
            return;
        }

        this.previewState.selectedId = recId;
        this.previewState.loading = true;
        this.previewState.error = null;
        this.previewState.pdfUrl = null;
        this.previewState.isSigned = false;

        try {
            // Lecture des champs sur sign.request
            const result = await this.orm.read(
                "sign.request",
                [recId],
                ["display_name", "template_id", "state"]
            );

            if (!result.length) {
                this.previewState.error = "Enregistrement introuvable.";
                return;
            }

            const rec = result[0];
            this.previewState.documentName = rec.display_name || "";
            this.previewState.isSigned = rec.state === "signed";

            // Stratégie 1 : document signé → cherche le PDF final en pièce jointe
            if (rec.state === "signed") {
                const attachments = await this.orm.searchRead(
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
                    this.previewState.pdfUrl = `/web/content/${attachments[0].id}?inline=true`;
                    return;
                }
            }

            // Stratégie 2 : PDF original via template_id.attachment_id
            if (rec.template_id) {
                const templateId = rec.template_id[0];
                const tpl = await this.orm.read(
                    "sign.template",
                    [templateId],
                    ["attachment_id"]
                );
                if (tpl.length && tpl[0].attachment_id) {
                    const attachId = tpl[0].attachment_id[0];
                    this.previewState.pdfUrl = `/web/content/${attachId}?inline=true`;
                    return;
                }
            }

            this.previewState.error = "Aucun document PDF disponible pour cet enregistrement.";

        } catch (e) {
            this.previewState.error = "Impossible de charger le document.";
            console.error("[SignRequestPreview]", e);
        } finally {
            this.previewState.loading = false;
        }
    }

    // Double-clic → ouvre le formulaire complet
    async editRecord(record) {
        await super.openRecord(record);
    }
}

registry.category("views").add("sign_request_list_preview", {
    ...listView,
    Controller: SignRequestListController,
    template: "sign_request_preview.SignRequestListView",
});
