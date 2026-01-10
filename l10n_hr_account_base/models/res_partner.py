from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    l10n_hr_sale_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Sale Journal',
        company_dependent=1, # required=1,
        domain=[('type', '=', 'sale')])
    l10n_hr_purchase_journal_id = fields.Many2one(
        'account.journal', 'Purchase Journal',
        company_dependent=1, # required=1,
        domain=[('type', '=', 'purchase')])
