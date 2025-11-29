from odoo import models, fields


class ProductUoM(models.Model):
    _inherit = 'uom.uom'

    uom_en16931_id = fields.Many2one(
        comodel_name='uom.en16931',
        string="EN16931 UoM")
