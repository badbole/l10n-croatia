from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    l10n_hr_property_kpd_id = fields.Many2one(
        comodel_name='l10n.hr.kpd', string="KPD Code",
        domain=[('type', '=', '6')], company_dependent=True)
