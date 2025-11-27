from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_hr_business_process_type_id = fields.Many2one(
        comodel_name='l10n.hr.business.process.type',
        string="Business Process Type")

    l10n_hr_business_process_type_code = fields.Char(
        related='l10n_hr_business_process_type_id.code',
        string="Business Process Type Code")

    l10n_hr_business_process_name = fields.Char(
        string='Definition of business process for P99'
    )

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        res = super()._onchange_journal_id()
        if self.company_id.account_fiscal_country_id.code != "HR":
            return res
        if self.journal_id.l10n_hr_business_process_type_id:
            self.l10n_hr_business_process_type_id = self.journal_id.l10n_hr_business_process_type_id.id
        return res
