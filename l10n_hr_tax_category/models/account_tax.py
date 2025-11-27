from odoo import models, fields, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    l10n_hr_tax_category_id = fields.Many2one(
        comodel_name='l10n.hr.tax.category',
        string="Tax Category")

    def write(self, vals):
        return super().write(vals)