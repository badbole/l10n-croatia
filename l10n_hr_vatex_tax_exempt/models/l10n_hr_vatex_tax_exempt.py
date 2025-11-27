from odoo import models, fields, api


class L10nHrVatexTaxExempt(models.Model):
    _name = "l10n.hr.vatex.tax.exempt"
    _description = "Defines VATEX tax category."
    _inherit = ['mail.thread']

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    display_name = fields.Char(string="Display Name", compute='_compute_display_name', store=True)
    description = fields.Text(string="Description")

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'The VATEX tax exempt code has to be unique!')
    ]

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for exempt in self:
            if exempt.code and exempt.name:
                exempt.display_name = exempt.code + ' - ' + exempt.name
