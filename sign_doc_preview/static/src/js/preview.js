/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted, onWillUnmount, useRef, mount } from "@odoo/owl";
import { SignRequestListController } from "@sign/views/sign_list/sign_request_list_controller";

// ─── Composant panneau PDF ────────────────────────────────────────
class PdfPanel extends Component {
    static template = "sign_doc_preview.PdfPanel";
    static props = {
        loading: Boolean,
        error: { type: String, optional: true },
        pdfUrl: { type: String, optional: true },
        docName: { type: String, optional: true },
        isSigned: Boolean,
    };
}

// ─── Patch du controller natif ───────────────────────────────────
patch(SignRequestListController.prototype, {
    setup() {
        super.setup();
        this._sdpOrm = useService("orm");
        this._sdpState = useState({
            loading: false,
            error: null,
            pdfUrl: null,
            docName: "",
            isSigned: false,
            selectedId: null,
        });

        // Référence vers l'instance du composant panneau monté
        this._sdpApp = null;
        this._sdpContainer = null;

        onMounted(() => this._sdpMount());
        onWillUnmount(() => this._sdpDestroy());
    },

    _sdpMount() {
        // Trouve le conteneur de la vue liste
        const viewEl = this.__owl__.bdom.el;
        if (!viewEl) return;

        // Trouve le parent pour wrapper liste + panneau
        const parent = viewEl.parentElement;
        if (!parent) return;

        // Crée le wrapper flex
        const wrapper = document.createElement("div");
        wrapper.className = "o_sdp_root";
        parent.insertBefore(wrapper, viewEl);
        wrapper.appendChild(viewEl);
        viewEl.classList.add("o_sdp_list_panel");

        // Crée le conteneur du panneau PDF
        const panelContainer = document.createElement("div");
        panelContainer.className = "o_sdp_pdf_panel_wrapper";
        wrapper.appendChild(panelContainer);
        this._sdpContainer = panelContainer;

        // Monte le composant OWL PdfPanel dans le conteneur
        const state = this._sdpState;
        this._sdpApp = mount(PdfPanel, panelContainer, {
            env: this.env,
            props: state,
        });
    },

    _sdpDestroy() {
        if (this._sdpApp) {
            this._sdpApp.destroy();
            this._sdpApp = null;
        }
        // Remet le DOM en ordre
        const viewEl = this.__owl__.bdom && this.__owl__.bdom.el;
        if (viewEl) {
            viewEl.classList.remove("o_sdp_list_panel");
            const wrapper = viewEl.parentElement;
            if (wrapper && wrapper.classList.contains("o_sdp_root")) {
                wrapper.parentElement.insertBefore(viewEl, wrapper);
                wrapper.remove();
            }
        }
        this._sdpContainer = null;
    },

    async openRecord(record) {
        const recId = record.resId;

        // Toggle
        if (this._sdpState.selectedId === recId) {
            Object.assign(this._sdpState, {
                selectedId: null,
                pdfUrl: null,
                docName: "",
                error: null,
                loading: false,
                isSigned: false,
            });
            return;
        }

        Object.assign(this._sdpState, {
            selectedId: recId,
            loading: true,
            error: null,
            pdfUrl: null,
            isSigned: false,
        });

        try {
            const result = await this._sdpOrm.read(
                "sign.request",
                [recId],
                ["display_name", "template_id", "state"]
            );

            if (!result.length) {
                this._sdpState.error = "Enregistrement introuvable.";
                return;
            }

            const rec = result[0];
            this._sdpState.docName = rec.display_name || "";
            this._sdpState.isSigned = rec.state === "signed";

            // 1. Document signé → PDF final en pièce jointe
            if (rec.state === "signed") {
                const attachments = await this._sdpOrm.searchRead(
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
                    this._sdpState.pdfUrl = `/web/content/${attachments[0].id}?inline=true`;
                    return;
                }
            }

            // 2. Fallback → PDF original via template
            if (rec.template_id) {
                const tpl = await this._sdpOrm.read(
                    "sign.template",
                    [rec.template_id[0]],
                    ["attachment_id"]
                );
                if (tpl.length && tpl[0].attachment_id) {
                    this._sdpState.pdfUrl = `/web/content/${tpl[0].attachment_id[0]}?inline=true`;
                    return;
                }
            }

            this._sdpState.error = "Aucun PDF disponible.";

        } catch (e) {
            this._sdpState.error = "Erreur lors du chargement.";
            console.error("[SignDocPreview]", e);
        } finally {
            this._sdpState.loading = false;
        }
    },
});
