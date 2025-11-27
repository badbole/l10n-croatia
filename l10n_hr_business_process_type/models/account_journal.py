from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    l10n_hr_business_process_type_id = fields.Many2one(
        comodel_name='l10n.hr.business.process.type',
        string="Business Process Type")
