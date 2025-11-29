from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "l10n.hr.fiskal.mixin", "l10n.hr.xml.mixin"]


    l10n_hr_fiskal_model = fields.Selection(
        selection=[
            ("f1", "Fiskalizacija 1 (B2C)"),
            ("f2", "Fiskalizacija 2 (B2B, B2G)"),
            ("fx", "Nema fiskallizacije (INO, EU)"),
            ("no", "Not applicable")
        ], compute="_compute_l10n_hr_fiskal_model",
        string="Fiscal model"
    )
    l10n_hr_nacin_placanja = fields.Selection(
        selection_add=[
            ("G", "Cash (bills and coins)"),
            ("K", "Credit or debit cards"),
            ("C", "Bank Cheque"),
            ("O", "Other payment means"),
        ],
        help="According to Fiscalization Law and regulative "
        "there is 5 possible options: \n"
        "T - Transaction bank account\n"
        "G - Cash (coins or bills), fiskalisation required\n"
        "K - Bank cards, fiskalisation required\n"
        "C - Cheque payment, fiskalisation required\n"
        "O - Other payment, fiskalisation required\n",
    )
    l10n_hr_fiskal_log_ids = fields.One2many(
        comodel_name="l10n.hr.fiskal.log",
        inverse_name="invoice_id",
        string="Fiskal message logs",
        help="Log of all messages sent and received for FINA",
    )

    @api.depends('company_id', 'partner_id')
    def _compute_l10n_hr_fiskal_model(self):
        for move in self:
            if move.company_id.country_id.code != "HR" or not move.partner_id:
                move.l10n_hr_fiskal_model = "no"
                continue
            if move.partner_id.country_id.code != "HR":
                if move.partner_id.is_company:
                    # strana tvrtka
                    move.l10n_hr_fiskal_model = "fx"
                else:
                    # privatna osoba stranac
                    move.l10n_hr_fiskal_model = "f1"
            else:
                if move.partner_id.is_company:
                    move.l10n_hr_fiskal_model = "f2"
                else:
                    move.l10n_hr_fiskal_model = "f1"


    def button_fiskaliziraj(self):
        self.ensure_one()
        # ako imam JIR pokreće provjeru ili ako nema fiskalizaciju.
        self.fiskaliziraj()  # from 10n.hr.fixcal.mixin

    def _l10n_hr_post_out_invoice(self):
        # singleton record! checked in super()
        res = super()._l10n_hr_post_out_invoice()
        # TODO selection or decision which to send ?
        # - possible not fiscalisation of invoices paid on transaction acc?
        # need to put smart options what and when not to send...
        if (
            self.l10n_hr_fiskal_model == 'f1' and
            not self.l10n_hr_fiskal_uredjaj_id.fiskalisation_active
            and self.l10n_hr_nacin_placanja != "T"
        ):
            raise ValidationError(
                _(
                    "Fiscalization is not active for %s!! "
                    "Only Transaction account payment is allowed!"
                )
                % self.journal_id.display_name
            )
        if self.l10n_hr_fiskal_model == 'f1' and self.l10n_hr_fiskal_uredjaj_id.fiskalisation_active:
            self.fiskaliziraj()
        return res
