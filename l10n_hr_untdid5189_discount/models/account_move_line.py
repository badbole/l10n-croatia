from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_hr_discount_type_id = fields.Many2one(
        comodel_name="l10n.hr.discount.type",
        string="Discount type"
    )
