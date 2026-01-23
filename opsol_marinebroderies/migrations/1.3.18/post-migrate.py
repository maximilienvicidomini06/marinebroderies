# -*- coding: utf-8 -*-
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    model = env['stock.picking'].with_context(active_test=False)

    batch_size = 1000
    offset = 0
    total = 0
    while True:
        pickings = model.search([], offset=offset, limit=batch_size)
        if not pickings:
            break
        pickings._compute_display_name()
        env.flush_all()
        total += len(pickings)
        offset += batch_size

    _logger.info("Recomputed display_name for %s stock.picking records.", total)
