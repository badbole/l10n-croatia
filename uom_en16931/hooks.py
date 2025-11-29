# Copyright (C) 2025 - Ecodica d.o.o
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

def _pre_init_hook(cr):
    cr.execute("""
        UPDATE ir_model_data SET noupdate = FALSE
            WHERE model = 'uom.uom' AND module = 'uom'
    """)


def _post_init_hook(cr, registry):
    cr.execute("""
        UPDATE ir_model_data SET noupdate = TRUE
            WHERE model = 'uom.uom' AND module = 'uom'
    """)
