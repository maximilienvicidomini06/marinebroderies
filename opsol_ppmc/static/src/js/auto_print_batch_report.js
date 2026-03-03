/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useEffect } from "@odoo/owl";

patch(FormController.prototype, "opsol_ppmc_auto_print_batch_report", {
    setup() {
        this._super(...arguments);
        this.actionService = useService("action");
        useEffect(
            () => {
                const resModel = this.props.resModel;
                const resId = this.props.resId;
                const context = this.props.context || this.model?.root?.context || {};
                if (resModel !== "account.batch.payment" || !resId || !context.auto_print_ppmc_report) {
                    return;
                }
                const key = `opsol_ppmc_auto_print_batch_${resId}`;
                if (window.sessionStorage.getItem(key)) {
                    return;
                }
                window.sessionStorage.setItem(key, "1");
                this.actionService.doAction("opsol_ppmc.action_report_ppmc_payments", {
                    additionalContext: {
                        active_model: "account.batch.payment",
                        active_id: resId,
                        active_ids: [resId],
                    },
                });
            },
            () => [this.props.resModel, this.props.resId]
        );
    },
});
