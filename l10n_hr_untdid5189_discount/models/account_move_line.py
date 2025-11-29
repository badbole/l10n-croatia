from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_hr_discount_type_id = fields.Many2one(
        comodel_name="l10n.hr.discount.type",
        string="Discount type"
    )

    @api.onchange('discount')
    def onchange_discount(self):
        if self.discount and self.discount > 0:
            self.l10n_hr_discount_type_id = self.env.ref("l10n_hr_untdid5189_discount.discount_code_95")
        elif self.discount and self.discount < 0:
            self.l10n_hr_discount_type_id = self.env.ref("l10n_hr_untdid5189_discount.discount_code_99")
        else:
            self.l10n_hr_discount_type_id = False
