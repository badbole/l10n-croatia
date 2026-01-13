from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"


    nace_id = fields.Many2one(
        help="Main occupation classified according to EU NACE 2.0 / NKD-2025",
    )


class ResPartnerIndustry(models.Model):
    _inherit = "res.partner.industry"

    #code = fields.Char()

    # def name_get(self):
    #     def get_names(cat):
    #         """Return the list [cat.name, cat.parent_id.name, ...]"""
    #         res = []
    #         while cat:
    #             res.append(" - ".join((cat.code, cat.name)))
    #             cat = cat.parent_id
    #         return res
    #
    #     if (
    #         self.env["ir.config_parameter"]
    #         .sudo()
    #         .get_param("partner_industry_secondary.display_last_child_first")
    #     ):
    #         # Display last child first
    #         result = []
    #         for cat in self:
    #             cat_name, *parent_cats = get_names(cat)
    #
    #             if parent_cats:
    #                 cat_name = f"{str(cat_name)} ({' < '.join(parent_cats)})"
    #             result.append((cat.id, cat_name))
    #         return result
    #     # Default display (Grandparent / Parent / Child)
    #     return [(cat.id, " / ".join(get_names(cat)[::-1])) for cat in self]
