from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    vat = fields.Char(related="partner_id.vat", stroe=True, readonly=False)

