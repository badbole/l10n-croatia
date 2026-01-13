from odoo import fields, models


class Nkd(models.Model):
    _name = "l10n.hr.nkd"
    _description = "HR NKD - national occupational calssification"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code'


    code = fields.Char(size=16, required=True)
    name = fields.Char(required=True)
    parent_id = fields.Many2one(
        comodel_name="l10n.hr.nkd",
        index=True, ondelete='cascade'
    )
    child_ids = fields.One2many(
        comodel_name="l10n.hr.nkd",
        inverse_name="parent_id",
        string="Elements"
    )
    parent_path = fields.Char(index=True, unaccent=False)


    def name_get(self):
        res = [((c.id, "%s - %s" % (c.code, c.name))) for c in self]
        return res
