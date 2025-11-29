from odoo import models, fields, api


class UomEn16931(models.Model):
    _name = "uom.en16931"
    _description = "Defines units of measure based on EN16931 standard."
    _order = "code ASC"

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    display_name = fields.Char(string="Display Name", compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'The EN16931 UoM code has to be unique!')
    ]

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for uom in self:
            if uom.code and uom.name:
                uom.display_name = uom.code + ' - ' + uom.name
