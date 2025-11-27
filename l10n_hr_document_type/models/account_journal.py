from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    l10n_hr_untdid1001_document_type_id = fields.Many2one(
        comodel_name='l10n.hr.document.type',
        string="Document Type")
