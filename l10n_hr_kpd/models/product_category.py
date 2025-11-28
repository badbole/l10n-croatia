from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    l10n_hr_kpd_id = fields.Many2one(comodel_name='l10n.hr.kpd', string="KPD Code", domain=[('type', '=', '6')])
