/** @odoo-module */

import { registry } from "@web/core/registry";
import { x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { MovesListRenderer, StockMoveX2ManyField } from "@stock/views/picking_form/stock_move_one2many";

export class OpsolMovesListRenderer extends MovesListRenderer {
    static template = "opsol_stock_move_tools.ListRenderer";

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
}

export class OpsolStockMoveX2ManyField extends StockMoveX2ManyField {
    static components = { ...StockMoveX2ManyField.components, ListRenderer: OpsolMovesListRenderer };
}

export const opsolStockMoveX2ManyField = {
    ...x2ManyField,
    component: OpsolStockMoveX2ManyField,
};

registry.category("fields").add("opsol_stock_move_one2many", opsolStockMoveX2ManyField);
