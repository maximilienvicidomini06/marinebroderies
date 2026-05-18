/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { useState, onMounted, onWillUnmount } from "@odoo/owl";

const viewRegistry = registry.category("views");

function applySignPreviewPatch() {
    const signListView = viewRegistry.get("sign_list", false);
    if (!signListView) {
        console.warn("[SignDocPreview] sign_list not found in registry");
        return;
    }

    const OriginalController = signListView.Controller;

    class SignPreviewController extends OriginalController {
        setup() {
            super.setup();
            this._orm = useService("orm");
            this._sdpState = useState({
                loading: false,
                error: null,
                pdfUrl: null,
                docName: "",
                isSigned: false,
                selectedId: null,
            });
            this._panelEl = null;
            this._wrapperEl = null;
            this._stateInterval = null;

            onMounted(() => this._injectPanel());
            onWillUnmount(() => this._removePanel());
        }

        _renderPanel() {
            if (!this._panelEl) return;
            const s = this._sdpState;
            if (s.loading) {
                this._panelEl.innerHTML = `
                    <div class="o_sdp_placeholder">
                        <i class="fa fa-spinner fa-spin fa-2x text-muted"></i>
                        <p class="mt-2 text-muted">Chargement...</p>
                    </div>`;
            } else if (s.error) {
                this._panelEl.innerHTML = `
                    <div class="o_sdp_placeholder">
                        <i class="fa fa-exclamation-circle fa-2x text-warning"></i>
                        <p class="mt-2 text-muted">${s.error}</p>
                    </div>`;
            } else if (s.pdfUrl) {
                const badge = s.isSigned ? `<span class="badge bg-success ms-2">Sign&#233;</span>` : "";
                const iconColor = s.isSigned ? "text-success" : "text-danger";
                this._panelEl.innerHTML = `
                    <div class="o_sdp_header">
                        <i class="fa fa-file-pdf-o me-2 ${iconColor}"></i>
                        <span class="o_sdp_title">${s.docName || ""}</span>
                        ${badge}
                        <a class="btn btn-sm btn-outline-secondary ms-auto"
                           href="${s.pdfUrl}" target="_blank">
                            <i class="fa fa-external-link"></i>
                        </a>
                    </div>
                    <iframe src="${s.pdfUrl}" class="o_sdp_iframe" frameborder="0"></iframe>`;
            } else {
                this._panelEl.innerHTML = `
                    <div class="o_sdp_placeholder">
                        <i class="fa fa-file-pdf-o fa-3x text-muted"></i>
                        <p class="mt-3 text-muted">Cliquez sur un document<br>pour afficher l&#39;aper&#231;u</p>
                    </div>`;
            }
        }

        _injectPanel() {
            const el = this.__owl__.bdom && this.__owl__.bdom.el;
            if (!el) return;
            const parent = el.parentElement;
            if (!parent) return;

            const wrapper = document.createElement("div");
            wrapper.className = "o_sdp_root";
            parent.insertBefore(wrapper, el);
            wrapper.appendChild(el);
            el.classList.add("o_sdp_list_panel");
            this._wrapperEl = wrapper;

            const panel = document.createElement("div");
            panel.className = "o_sdp_panel";
            wrapper.appendChild(panel);
            this._panelEl = panel;

            this._renderPanel();
            this._stateInterval = setInterval(() => this._renderPanel(), 150);
        }

        _removePanel() {
            if (this._stateInterval) {
                clearInterval(this._stateInterval);
                this._stateInterval = null;
            }
            const el = this.__owl__.bdom && this.__owl__.bdom.el;
            if (el) el.classList.remove("o_sdp_list_panel");
            if (this._wrapperEl && this._wrapperEl.parentElement) {
                if (el) this._wrapperEl.parentElement.insertBefore(el, this._wrapperEl);
                this._wrapperEl.remove();
            }
            this._wrapperEl = null;
            this._panelEl = null;
        }

        async openRecord(record) {
            const recId = record.resId;

            if (this._sdpState.selectedId === recId) {
                Object.assign(this._sdpState, {
                    selectedId: null, pdfUrl: null,
                    docName: "", error: null,
                    loading: false, isSigned: false,
                });
                return;
            }

            Object.assign(this._sdpState, {
                selectedId: recId, loading: true,
                error: null, pdfUrl: null, isSigned: false,
            });

            try {
                const result = await this._orm.read(
                    "sign.request", [recId],
                    ["display_name", "template_id", "state"]
                );
                if (!result.length) {
                    this._sdpState.error = "Introuvable.";
                    return;
                }

                const rec = result[0];
                this._sdpState.docName = rec.display_name || "";
                this._sdpState.isSigned = rec.state === "signed";

                if (rec.state === "signed") {
                    const atts = await this._orm.searchRead(
                        "ir.attachment",
                        [
                            ["res_model", "=", "sign.request"],
                            ["res_id", "=", recId],
                            ["mimetype", "=", "application/pdf"],
                        ],
                        ["id"], { limit: 1, order: "id desc" }
                    );
                    if (atts.length) {
                        this._sdpState.pdfUrl = `/web/content/${atts[0].id}?inline=true`;
                        return;
                    }
                }

                if (rec.template_id) {
                    const tplResult = await this._orm.read(
                        "sign.template", [rec.template_id[0]], ["attachment_id"]
                    );
                    if (tplResult.length && tplResult[0].attachment_id) {
                        this._sdpState.pdfUrl = `/web/content/${tplResult[0].attachment_id[0]}?inline=true`;
                        return;
                    }
                }

                this._sdpState.error = "Aucun PDF disponible.";

            } catch (e) {
                this._sdpState.error = "Erreur de chargement.";
                console.error("[SignDocPreview]", e);
            } finally {
                this._sdpState.loading = false;
            }
        }
    }

    viewRegistry.add("sign_list", {
        ...signListView,
        Controller: SignPreviewController,
    }, { force: true });
}

applySignPreviewPatch();
