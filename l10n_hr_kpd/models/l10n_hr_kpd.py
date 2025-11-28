from odoo import models, fields, api, _
from odoo.exceptions import UserError

import re

CODE_PATTERNS = {
    '1': r"[A-Z]",
    '2': r"^\d{2}$",
    '3': r"^\d{2}\.\d$",
    '4': r"^\d{2}\.\d{2}$",
    '5': r"^\d{2}\.\d{2}\.\d$",
    '6': r"^\d{2}\.\d{2}\.\d{2}$"
}


class L10nHrKpd(models.Model):
    _name = 'l10n.hr.kpd'
    _description = 'Defines KPD classification.'
    _order = 'code ASC'
    _rec_name = 'display_name'
    #_inherit = ['mail.thread']

    code = fields.Char(string="Code", required=True, copy=False)
    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date")
    level = fields.Char(string="Level", readonly=True, required=True)
    name = fields.Char(string="Name", required=True, translate=True)
    display_name = fields.Char(string="Display Name", compute='_compute_display_name', store=True)
    type = fields.Selection(
        string="Type",
        selection=[
            ('1', 'Section'),
            ('2', 'Division'),
            ('3', 'Group'),
            ('4', 'Class'),
            ('5', 'Category'),
            ('6', 'Subcategory')
        ], compute="_compute_type", store=True)
    parent_id = fields.Many2one(comodel_name='l10n.hr.kpd', string="Parent")

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'The KPD code has to be unique!')
    ]

    @api.depends('level')
    def _compute_type(self):
        for kpd in self:
            kpd.type = kpd.level

    @staticmethod
    def _is_code_valid(code, level):
        """
            Check if KPD code is in proper format depending on record type.
        """
        valid_pattern = CODE_PATTERNS.get(level)
        return bool(re.fullmatch(valid_pattern, code))

    @api.constrains('code')
    def _check_subcategory_code(self):
        for kpd in self:
            if not self._is_code_valid(code=kpd.code, level=kpd.level):
                raise UserError(
                    _("The KPD code is not properly formatted!")
                )

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for dt in self:
            if dt.code and dt.name:
                dt.display_name = dt.code + ' - ' + dt.name
