# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class AccountMove(models.Model):
    _inherit = "account.move"



    date_document = fields.Date(
        string='Document Date',
        readonly=True, states={'draft': [('readonly', False)]},
        help="Date when the document was actually created. "
             "Leave blank for current date",
        copy=False)
    date_delivery = fields.Date(
        string='Delivery Date',
        readonly=True, states={'draft': [('readonly', False)]},
        copy=False,
        help="Date of delivery of goods or service. "
             "Leave blank for current date")

    # DB: namjerno su nazivi polja na hrvatskom!
    # radi potencijalno drugih lokalizacija
    vrijeme_izdavanja = fields.Char(
        # DB: namjerno kao char da izbjegnem timezone problem!
        string="Time of confirming",
        help="Croatia Fiskal datetime value", copy=False,
        readonly=True, states={'draft': [('readonly', False)]})
    fiskalni_broj = fields.Char(
        string="Fiskal number", copy=False,
        help="Fiskalni broj računa, ukoliko je različit od broja računa",
        readonly=True, states={'draft': [('readonly', False)]})
    # i za ulazne račune se ovdje moze upisati
    nacin_placanja = fields.Selection(
        selection=[('T', 'TRANSACTION BANK ACCOUNT')],
        string="Croatia payment means", default="T",
        readonly=True, states={'draft': [('readonly', False)]})

    fiskal_uredjaj_id = fields.Many2one(
        comodel_name='fiskal.uredjaj',
        string="Fiskal device",
        help="Device on which is fiscal payment registred",
        readonly=True, states={'draft': [('readonly', False)]},
        )

    fiskal_responsible_id = fields.Many2one(
        comodel_name='res.partner',
        string="Responsible person",
        domain="[('fiskal_responsible','=',True)]",
        help="Fiscal responsible person for this invoice",
        readonly=True, states={'draft': [('readonly', False)]})

    @api.model
    def default_get(self, fields):
        res = super(AccountMove, self).default_get(fields)
        user = self.env.user

        if not user.company_id.croatia:
            return res
        type = res.get('move_type')
        if type in ('out_invoice', 'out_refund'):

            journal = res.get('journal_id')
            journal = self.env['account.journal'].browse(journal)
            responsible = journal.fiskal_responsible_id
            if not responsible:
                responsible = user.company_id.fiskal_responsible_id
            uredjaj = journal.fiskal_uredjaj_ids and journal.fiskal_uredjaj_ids[0] or None
            # uzmi sve, i napravi presjek sa dozvoljneima za usera!!!
            #if uredjaj not in user.uredjaj_ids:
                # provjeriti ima li koji drugi? koji su dozvoljeni korisniku?
            #    pass
            if uredjaj:
                res['fiskal_uredjaj_id'] = uredjaj.id
            res['fiskal_responsible_id'] = responsible.id
        return res

    def _gen_fiskal_number(self):
        self.ensure_one()  # one at a time only!
        prostor = self.fiskal_uredjaj_id.prostor_id
        uredjaj = self.fiskal_uredjaj_id
        separator = self.company_id.fiskal_separator

        sequence = prostor.sljed_racuna == 'P' and prostor.sequence_id \
                    or uredjaj.sequence_id
        # prefix i suffux nesmiju postojati u ovoj sekvenci!!
        pref, suff = sequence.prefix, sequence.suffix
        if pref or suff:
            raise Warning(_('Sequence should not have prefix or suffix!'))
        broj = sequence._next(sequence_date=self.date)

        fiskalni_broj = separator.join((str(int(broj)), prostor.oznaka_prostor, uredjaj.oznaka_uredjaj))
        return fiskalni_broj

    def _set_fiskal_dates(self):
        self.ensure_one()
        if not self.date_document:
            self.date_document = fields.Date.today()
        if not self.vrijeme_izdavanja:
            datum = self.company_id.get_l10n_hr_time_formatted()
            self.vrijeme_izdavanja = datum['datum_racun']

    def _set_fiskal_number(self):
        self.ensure_one()
        if not self.date:
            self.date = fields.Date.today()
        self.env.cr.execute("""
            select name, fiskalni_broj, date from account_move
            where journal_id = %(journal)s
              and state = 'posted'
              and date > %(date)s
            order by date desc
            """, {
            'journal': self.journal_id.id,
            'date': self.date,
            })
        res = self.env.cr.fetchall()
        if res:
            msg = _("Date %s is not valid!" % self.date)
            for name, broj, dt in res:
                msg += "\n %s - %s from %s" % (name, broj, dt)
            raise Warning(msg)
        self.fiskalni_broj = self._gen_fiskal_number()
        # now and set lock on journals,
        # after first posting journal is locked for changes
        if not self.fiskal_uredjaj_id.lock:
            self.fiskal_uredjaj_id.lock = True
        if not self.fiskal_uredjaj_id.prostor_id.lock:
            self.fiskal_uredjaj_id.prostor_id.lock = True

    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        for move in posted:
            if not move.company_id.croatia:
                continue  # only for croatia
            if not move.is_invoice(include_receipts=False):
                continue  # only invoices
            if move.move_type not in ('out_invoice', 'out_refund'):
                continue  # only required for out invoice/refind
            if move.fiskal_uredjaj_id.prostor_id.state != 'active':
                raise Warning(_(
                        "Invoice posting not possible, "
                        "business premisse %s is not active!" %
                        move.fiskal_uredjaj_id.prostor_id.name
                    ))
            move._set_fiskal_dates()
            if not move.fiskalni_broj:
                move._set_fiskal_number()
        return posted
