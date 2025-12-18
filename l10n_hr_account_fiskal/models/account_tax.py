# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    l10n_hr_fiskal_type = fields.Selection(
        selection=[
            ("Pdv", "PDV"),
            ("Pnp", "Porez na potrosnju"),
            ("OstaliPor", "Ostali porezi"),
            ("oslobodenje", "Oslobodjenje"),
            ("marza", "Oporezivanje marze"),
            ("ne_podlijeze", "Ne podlijeze oporezivanju"),
            ("Naknade", "Naknade (npr. ambalaza)"),
        ],
        string="Fiskal tax type",
        #domain="[('type_tax_use', '!=', 'purchase')]",
    )
