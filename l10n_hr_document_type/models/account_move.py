from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_hr_untdid1001_document_type_id = fields.Many2one(
        comodel_name='l10n.hr.document.type',
        string="Document Type")
