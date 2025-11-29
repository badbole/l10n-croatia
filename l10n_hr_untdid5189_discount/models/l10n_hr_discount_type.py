from odoo import models, fields, api


class L10nHrDiscountType(models.Model):
    _name = "l10n.hr.discount.type"
    _description = "Defines discount codes"
    _rec_name = 'display_name'
    #_inherit = ['mail.thread']

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    display_name = fields.Char(string="Display Name", compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'The discount code has to be unique!')
    ]

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for bpt in self:
            if bpt.code and bpt.name:
                bpt.display_name = bpt.code + ' - ' + bpt.name
