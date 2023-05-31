from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_hr_date_document = fields.Date(
        string="Document Date",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Date when the document was actually created. "
        "Leave blank for current date",
    )
    l10n_hr_date_delivery = (
        fields.Date(  # to avoid possible name conflict in delivery module!
            string="Delivery Date",
            copy=False,
            readonly=True,
            states={"draft": [("readonly", False)]},
            help="Date of delivery of goods or service. "
            "Leave blank for current date",
        )
    )
    l10n_hr_vrijeme_izdavanja = fields.Char(
        # DB: namjerno kao char da izbjegnem timezone problem!
        string="Time of invoicing",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Croatia Fiskal datetime value as string, should respect format: ",
    )
    l10n_hr_fiskalni_broj = fields.Char(
        string="Fiskal number",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Required fiscal number, generated according to "
        "regulations regardless of journal number",
    )
    # i za ulazne račune se ovdje moze upisati
    l10n_hr_nacin_placanja = fields.Selection(
        selection=[("T", "Bank transfer")],
        string="Croatia payment means",
        default="T",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="According to Fiscalization Law and regulative "
        "there is 5 possible options: T, G, K, C, O\n"
        "T - Transaction bank account, is applicable without fiskalisation\n"
        " and for other options needed please install fiscalisation extension module",
    )

    l10n_hr_fiskal_uredjaj_id = fields.Many2one(
        comodel_name="l10n.hr.fiskal.uredjaj",
        string="Fiskal device",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Device on which is fiscal payment registred",
    )
    l10n_hr_allowed_fiskal_uredjaj_ids = fields.Many2many(
        comodel_name="l10n.hr.fiskal.uredjaj",
        compute="_compute_allowed_fiskal_device",
        string="Alowed Fiskal device",
    )
    l10n_hr_fiskal_uredjaj_visible = fields.Boolean(
        help="Technical field to show device selection"
        " only if there is something to select"
        " like 2 or more devices for this journal",
    )

    @api.depends(
        "invoice_line_ids.currency_rate",
        "invoice_line_ids.tax_base_amount",
        "invoice_line_ids.tax_line_id",
        "invoice_line_ids.price_total",
        "invoice_line_ids.price_subtotal",
        "invoice_payment_term_id",
        "partner_id",
        "currency_id",
    )
    def _compute_tax_totals(self):
        super()._compute_tax_totals()
        """ Storno hack for Croatia,
        We print Storno invoices with negative amounts,
        So this sets the minus sign in formmated text values
        Second part of this hack is in qweb view, adding the same
        for quantity and amount  fields.
        """

        def add_minus(s):
            return "- " + s
        for move in self:
            if (
                move.move_type == "out_refund"
                and self.company_id.account_fiscal_country_id.code == "HR"
            ):
                totals = move.tax_totals
                totals["formatted_amount_total"] = add_minus(
                    totals["formatted_amount_total"]
                )
                totals["formatted_amount_untaxed"] = add_minus(
                    totals["formatted_amount_untaxed"]
                )
                for st in totals["subtotals"]:
                    st["formatted_amount"] = add_minus(st["formatted_amount"])
                for sg in totals["groups_by_subtotal"].keys():
                    cgt = totals["groups_by_subtotal"][sg]
                    for group in cgt:
                        group["formatted_tax_group_amount"] = add_minus(
                            group["formatted_tax_group_amount"]
                        )
                        group["formatted_tax_group_base_amount"] = add_minus(
                            group["formatted_tax_group_base_amount"]
                        )
                move.tax_totals = totals
            # return res

    @api.depends(
        "journal_id",
        "journal_id.l10n_hr_prostor_id",
        "journal_id.l10n_hr_prostor_id.state",
        "journal_id.l10n_hr_fiskal_uredjaj_ids",
        "journal_id.l10n_hr_fiskal_uredjaj_ids.state",
    )
    def _compute_allowed_fiskal_device(self):
        for move in self:
            vals = []
            if move.journal_id.l10n_hr_prostor_id.state == "active":
                vals = [
                    (4, fd.id)
                    for fd in move.journal_id.l10n_hr_fiskal_uredjaj_ids
                    if fd.state == "active"
                ]

            move.l10n_hr_fiskal_uredjaj_id = vals and vals[0][1]
            move.l10n_hr_allowed_fiskal_uredjaj_ids = vals
            move.l10n_hr_fiskal_uredjaj_visible = len(vals) > 1

    def _gen_fiskal_number(self):
        self.ensure_one()  # one at a time only!
        prostor = self.l10n_hr_fiskal_uredjaj_id.prostor_id
        uredjaj = self.l10n_hr_fiskal_uredjaj_id
        sequence = (
            prostor.sljed_racuna == "P" and prostor.sequence_id or uredjaj.sequence_id
        )
        broj = sequence._next(sequence_date=self.date)
        if broj.endswith("__"):
            broj = broj.replace("__", str(uredjaj.oznaka_uredjaj))
        return broj

    def _l10n_hr_post_check(self):
        """
        Inherit for all other controlls needed adding a line for each
        missing or wrong entry data for out invoices / refunds needed
        Better that raising error for each error
        :return:
        """
        self.ensure_one()
        res = []
        if not self.l10n_hr_fiskal_uredjaj_id:
            res.append(_("No active PoS devices found for this journal"))
        if self.l10n_hr_fiskal_uredjaj_id.state != "active":
            res.append(_("PoS device selected is not active"))
        return res

    def _l10n_hr_post_out_invoice(self):
        self.ensure_one()
        l10n_hr_errors = self._l10n_hr_post_check()
        if l10n_hr_errors:
            msg = _("Invoice posting not possible:\n") + "\n".join(l10n_hr_errors)
            raise ValidationError(msg)
        # set date fields
        if not self.l10n_hr_date_document:
            self.l10n_hr_date_document = fields.Date.today()
        if not self.l10n_hr_date_delivery:
            self.l10n_hr_date_delivery = fields.Date.today()
        if not self.date:
            self.date = fields.Date.today()
        if not self.l10n_hr_vrijeme_izdavanja:  # depend na l10n_hr_base?
            # DEV NOTE: mozda i ostaviti datetime field? za sad.. char
            datum = self.company_id.get_l10n_hr_time_formatted()
            self.l10n_hr_vrijeme_izdavanja = datum["datum_racun"]
        # set fiskal number
        if not self.invoice_user_id:
            self.invoice_user_id = self.env.user
        if not self.l10n_hr_fiskalni_broj:
            self.l10n_hr_fiskalni_broj = self._gen_fiskal_number()
        # now and set lock on journals,
        # after first posting journal is locked for changes
        if not self.l10n_hr_fiskal_uredjaj_id.lock:
            self.l10n_hr_fiskal_uredjaj_id.lock = True
            if not self.l10n_hr_fiskal_uredjaj_id.prostor_id.lock:
                self.l10n_hr_fiskal_uredjaj_id.prostor_id.lock = True

    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        for move in posted:
            if move.company_id.account_fiscal_country_id.code != "HR":
                continue  # only for croatia
            if not move.is_invoice(include_receipts=False):
                continue  # only invoices
            if move.move_type in ("out_invoice", "out_refund"):
                move._l10n_hr_post_out_invoice()
        return posted
