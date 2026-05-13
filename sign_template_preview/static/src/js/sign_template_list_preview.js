/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";
import { useState, useRef, onWillUnmount } from "@odoo/owl";

/**
 * Controller étendu pour la vue liste sign.template.
 * Intercepte le clic sur une ligne pour afficher l'aperçu PDF
 * dans un panneau latéral sans ouvrir le formulaire.
 */
export class SignTemplateListController extends ListController {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.previewState = useState({
            pdfUrl: null,
            selectedId: null,
            loading: false,
            error: null,
            templateName: null,
        });
    }

    /**
     * Intercepte l'ouverture d'un enregistrement (clic sur une ligne).
     * Charge l'URL du PDF et met à jour le panneau d'aperçu.
     * @param {Object} record - L'enregistrement cliqué
     */
    async openRecord(record) {
        const recId = record.resId;

        // Si on reclique sur le même enregistrement, on le désélectionne
        if (this.previewState.selectedId === recId) {
            this.previewState.selectedId = null;
            this.previewState.pdfUrl = null;
            this.previewState.templateName = null;
            this.previewState.error = null;
            return;
        }

        this.previewState.selectedId = recId;
        this.previewState.loading = true;
        this.previewState.error = null;
        this.previewState.pdfUrl = null;
        this.previewState.templateName = null;

        try {
            const result = await this.orm.read(
                "sign.template",
                [recId],
                ["attachment_id", "display_name"]
            );

            if (result.length && result[0].attachment_id) {
                const attachId = result[0].attachment_id[0];
                this.previewState.pdfUrl = `/web/content/${attachId}?inline=true`;
                this.previewState.templateName = result[0].display_name || "";
            } else {
                this.previewState.error = "Aucun document PDF associé à ce modèle.";
            }
        } catch (e) {
            this.previewState.error = "Impossible de charger le document.";
            console.error("[SignTemplatePreview] Erreur chargement PDF:", e);
        } finally {
            this.previewState.loading = false;
        }
    }

    /**
     * Ouvre le formulaire complet (double-clic ou bouton Modifier).
     * @param {Object} record
     */
    async editRecord(record) {
        await super.openRecord(record);
    }
}

// Enregistrement de la vue custom dans le registre Odoo
registry.category("views").add("sign_template_list_preview", {
    ...listView,
    Controller: SignTemplateListController,
    template: "sign_template_preview.SignTemplateListView",
});
