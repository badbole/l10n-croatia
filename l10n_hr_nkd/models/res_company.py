from odoo import api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    nace_id = fields.Many2one(related='partner_id.nace_id', store=True, readonly=False,
                              help="Main occupation classified according to NKD/ EU NACE 2.0", )
    industry_id = fields.Many2one(related='partner_id.industry_id',
                                  store=True, readonly=False,string="Main Industry")

    secondary_industry_ids = fields.Many2many(
        related='partner_id.secondary_industry_ids',
        store=True, readonly=False,
        comodel_name="res.partner.industry",
        string="Secondary Industries",
        domain="[('id', '!=', industry_id)]",
    )

    @api.onchange("nace_id")
    def _onchange_nkd_id(self):
        self.l10n_hr_nkd = self.nace_id.code

