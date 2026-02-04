/** @odoo-module */

import { registry } from "@web/core/registry";
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { ListRenderer } from "@web/views/list/list_renderer";

export class OpsolMovesListRenderer extends ListRenderer {
    static template = "opsol_stock_move_tools.ListRenderer";
    static props = [
        ...super.props,
        "showResetSelectedMoves",
    ];

    get hasSelectors() {
        this.props.allowSelectors = true;
        const list = this.props.list;
        if (!list.selectDomain) {
            list.selectDomain = (value) => {
                list.isDomainSelected = value;
                list.model.notify();
            };
        }
        return this.props.allowSelectors && !this.env.isSmall;
    }

    get hasSelectedMoves() {
        return this.props.list?.records?.some((record) => record.selected);
    }

    get showResetSelectedMoves() {
        return this.props.showResetSelectedMoves !== false;
    }

    get selectAll() {
        const list = this.props.list;
        if (list.isDomainSelected) {
            return true;
        }
        return false;
    }

    toggleSelection() {
        const list = this.props.list;
        if (!this.canSelectRecord) {
            return;
        }
        const selectedCount = list.records.filter((rec) => rec.selected).length;
        if (selectedCount === list.records.length) {
            list.records.forEach((record) => {
                record.toggleSelection(false);
                list.selectDomain(false);
            });
        } else {
            list.records.forEach((record) => {
                record.toggleSelection(true);
            });
        }
    }

    async resetSelectedMoves() {
        if (this.props.readonly) {
            return;
        }
        const selected = this.props.list.records.filter((record) => record.selected);
        for (const record of selected) {
            const updates = {};
            if ("quantity" in record.data) {
                updates.quantity = 0;
            }
            if (Object.keys(updates).length) {
                await record.update(updates, { save: false });
            }
        }
    }

    async sortDrop(dataRowId, dataGroupId, { element, previous }) {
        const list = this.props.list;
        const selected = list.records.filter((record) => record.selected);
        const isMultiDrag = selected.length > 1 && selected.some((record) => record.id === dataRowId);

        if (!isMultiDrag) {
            return super.sortDrop(dataRowId, dataGroupId, { element, previous });
        }

        element.classList.remove("o_row_draggable");
        try {
            const orderedSelected = list.records.filter((record) => record.selected);
            const remaining = list.records.filter((record) => !record.selected);
            let refId = null;
            if (previous) {
                const prevId = previous.dataset.id;
                if (remaining.some((record) => `${record.id}` === prevId)) {
                    refId = prevId;
                } else {
                    const prevIndex = list.records.findIndex((record) => `${record.id}` === prevId);
                    for (let i = prevIndex - 1; i >= 0; i--) {
                        const record = list.records[i];
                        if (!record.selected) {
                            refId = record.id;
                            break;
                        }
                    }
                }
            }

            for (const record of orderedSelected) {
                this.resequencePromise = list.resequence(record.id, refId, {
                    handleField: list.handleField,
                });
                await this.resequencePromise;
                refId = record.id;
            }
        } finally {
            element.classList.add("o_row_draggable");
            await list.leaveEditMode();
        }
    }
}

export class OpsolStockMoveX2ManyField extends X2ManyField {
    static components = {
            ...super.components,
            ListRenderer: OpsolMovesListRenderer,
        };
    static props = {
        ...super.props,
        showResetSelectedMoves: { type: Boolean, optional: true },
    };

    get rendererProps() {
        const rp = super.rendererProps;
        if (this.props.viewMode === "list") {
            rp.showResetSelectedMoves = this.props.showResetSelectedMoves;
        }
        return rp;
    }
}

export const opsolStockMoveX2ManyField = {
    ...x2ManyField,
    component: OpsolStockMoveX2ManyField,
    extractProps: (staticInfo, dynamicInfo) => {
        return {
            ...x2ManyField.extractProps(staticInfo, dynamicInfo),
            showResetSelectedMoves: staticInfo.options?.show_reset_selected_moves ?? false,
        };
    },

};

registry.category("fields").add("opsol_stock_move_one2many", opsolStockMoveX2ManyField);
