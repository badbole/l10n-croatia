from odoo import models, fields, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    l10n_hr_vatex_tax_exempt_id = fields.Many2one(
        comodel_name='l10n.hr.vatex.tax.exempt',
        string="VATEX Tax Exempt")

    is_exempt_required = fields.Boolean(
        compute="_compute_requires_reason"
    )


    @api.depends('l10n_hr_tax_category_id')
    def _compute_requires_reason(self):
        for tax in self:
            tax.is_exempt_required = tax.l10n_hr_tax_category_id and \
                 tax.l10n_hr_tax_category_id.code.replace("HR:","") in \
                  ['AE', 'E', 'G', 'O', 'K']
