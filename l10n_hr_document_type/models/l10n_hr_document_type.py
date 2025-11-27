from odoo import models, fields, api


class L10nHrDocumentType(models.Model):
    _name = "l10n.hr.document.type"
    _description = "Defines UNTDID1001 document type."
    _inherit = ['mail.thread']

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    display_name = fields.Char(string="Display Name", compute='_compute_display_name', store=True)
    description = fields.Text(string="Description")

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'The document type code has to be unique!')
    ]

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for dt in self:
            if dt.code and dt.name:
                dt.display_name = dt.code + ' - ' + dt.name
