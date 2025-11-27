from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    # original fields modification
    code = fields.Char(size=16)  # DB: default size 5 mi se cini premalecki...

    # new fields needed for localization
    l10n_hr_prostor_id = fields.Many2one(
        comodel_name="l10n.hr.fiskal.prostor",
        string="Business premise",
    )
    l10n_hr_fiskal_uredjaj_ids = fields.Many2many(
        comodel_name="l10n.hr.fiskal.uredjaj",
        relation="l10n_hr_fiskal_uredjaj_account_journal_rel",
        column1="journal_id",
        column2="uredjaj_id",
        string="Allowed PoS Devices",
    )

    l10n_hr_default_nacin_placanja = fields.Selection(
        selection=[("T", "Bank transfer")],
        string="Default fiskal payment method for this journal",
        default="T",
    )
