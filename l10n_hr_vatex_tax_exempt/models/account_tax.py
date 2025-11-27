from odoo import models, fields, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    l10n_hr_vatex_tax_exempt_id = fields.Many2one(
        comodel_name='l10n.hr.vatex.tax.exempt',
        string="VATEX Tax Exempt")


