from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_hr_kpd_id = fields.Many2one(
        comodel_name='l10n.hr.kpd', string="KPD Code", compute='_compute_l10n_hr_kpd_id',
                                     store=True, readonly=False, precompute=True,
                                     domain=[('type', '=', '6')])

    def _compute_l10n_hr_kpd_id(self):
        for line in self:
            kpd = line.product_id.with_company(line.company_id).l10n_hr_property_kpd_id
            if not kpd:
                kpd = line.product_id.categ_id.l10n_hr_kpd_id
                if not kpd:
                    parent_categories = self.env['product.category'].search(
                        [('id', 'parent_of', line.product_id.categ_id.id),
                         ('l10n_hr_kpd_id', '!=', False)],
                        order='parent_id ASC'
                    )
                    kpd = fields.first(parent_categories).l10n_hr_kpd_id
            line.l10n_hr_kpd_id = kpd.id

    @api.onchange('product_id')
    def _inverse_product_id(self):
        super(AccountMoveLine, self)._inverse_product_id()
        if self.product_id or not self.l10n_hr_kpd_id:
            self._conditional_add_to_compute('l10n_hr_kpd_id', lambda line: (
                    line.display_type == 'product' and line.move_id.is_invoice(True)
            ))
