from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    l10n_hr_fiskal_prostor_ids = fields.One2many(
        comodel_name="l10n.hr.fiskal.prostor",
        inverse_name="company_id",
        string="Business premises",
    )
    l10n_hr_fiskal_separator = fields.Selection(
        selection=[
            ("/", "/"),
            ("-", "-"),
        ],
        string="Invoice parts separator",
        default="/",
        help="Only '/' or '-' are legaly defined as allowed",
    )
    l10n_hr_fiskal_invoice_sequences = fields.Many2many(
        comodel_name="ir.sequence",
        string="Invoice fiskal sequences for company",
        compute="_compute_l10n_hr_sequences",
        context={"active_test": False},  # want to see inactive also!
    )
    l10n_hr_tax_model = fields.Selection(
        selection=[
            ("r1", "R1 - tax based on invoice"),
            ("r2", "R2 - tax based on payment"),
            ("r0", "R0 - NOT subject of taxation"),
            ("not_rh", "Not subject of taxation in Croatia"),
        ],
        string="Tax model",
        required=True,
        tracking=True,
        default="r1",  # TODO: multicompany improove!
    )
    l10n_hr_sale_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Sale Journal',
        company_dependent=1,  # required=1,
        domain=[('type', '=', 'sale')])
    l10n_hr_purchase_journal_id = fields.Many2one(
        'account.journal', 'Purchase Journal',
        company_dependent=1,  # required=1,
        domain=[('type', '=', 'purchase')])

    def _compute_l10n_hr_sequences(self):
        for company in self:
            sequences = (
                self.env["ir.sequence"]
                .with_context(active_test=False)
                .search(
                    [("company_id", "=", company.id), ("code", "=", "l10n_hr.fiscal")]
                )
            )
            company.l10n_hr_fiskal_invoice_sequences = [(4, s.id) for s in sequences]

    def l10n_hr_sequence_add_year(self):
        for sequence in self.l10n_hr_fiskal_invoice_sequences:
            if sequence.date_range_ids:
                last_date = sequence.date_range_ids.sorted(lambda l: l.date_to)[0]
                last_date.year + 1
            else:
                fields.Date.today().year


class IrSequenceDateRange(models.Model):
    _inherit = "ir.sequence.date_range"

    def name_get(self):
        res = [(d.id, "%s-%s" % (d.date_from.year, d.number_next_actual)) for d in self]
        return res
