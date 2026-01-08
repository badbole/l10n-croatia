# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def _hub3_amount_to_str(self, amount, size=None):
        #TODO check digits!
        res = str(amount)
        if res.endswith(".0"):
            res += "0"
        res = res.replace(".","").replace(",","")
        if size:
            add = size - len(res)
            res = "0" * add + res
        return res


    def _get_qr_vals(self, qr_method, amount, currency, debtor_partner, free_communication, structured_communication):
        if qr_method == 'hr_qr':
            model, pnbr = structured_communication.split(" ")
            qr_code_vals = [
                'HRVHUB30',                                             # Barcode version - Zaglavlje:                      fixed 8
                'EUR',                                                  # Valuta hardcoded EUR , only for local tranfers,   fixed : 3
                self._hub3_amount_to_str(amount, 15),                                            # Iznos,                                            fixed 15
                debtor_partner.name[:30],                               # Platitelj, Ime i prezime/Naziv                    fixed 30
                debtor_partner.street[:27],                                 # Adresa platitelj,                                 fixed 27
                " ".join((debtor_partner.zip, debtor_partner.city))[:27],# Adresa platitelj pošta i mjesto,                  fixed 27
                (self.acc_holder_name or self.partner_id.name)[:25],    # Primatelj naziv                                   fixed 25
                self.partner_id.street[:25],                            # Primatelj adresa ulica i broj                     fixed 25
                " ".join((
                    self.partner_id.zip,
                    self.partner_id.city
                ))[:27],                                                     # Primatelj PTT i grad,                             fixed 27
                self.sanitized_acc_number,                              # Account Number primatelja                         fixed 21
                model,                                                   # Model kontrole poziva na broj primatelja          fixed 4
                pnbr,                                             # Poziv na broj primatelja                          fixed 22
                "COST",                                                 # Šifra namjene                                     fixed 4
                "Po rn: %s" % free_communication                                 # Opis plaćanja                                     fixed 35
            ]
            return qr_code_vals
        return super()._get_qr_vals(qr_method, amount, currency, debtor_partner, free_communication, structured_communication)

    def _get_qr_code_generation_params(self, qr_method, amount, currency, debtor_partner, free_communication, structured_communication):
        if qr_method == 'hr_qr':
            return {
                'barcode_type': 'QR',
                'width': 200,
                'height': 200,
                'humanreadable': 1,
                #'barLevel': 'Q',
                'value': '\n'.join(self._get_qr_vals(qr_method, amount, currency, debtor_partner, free_communication, structured_communication)),
            }
        return super()._get_qr_code_generation_params(qr_method, amount, currency, debtor_partner, free_communication, structured_communication)

    def _eligible_for_qr_code(self, qr_method, debtor_partner, currency, raises_error=True):
        if qr_method == 'hr_qr':
            return currency.name == 'EUR' and \
                   self.acc_type == 'iban' and \
                   self.journal_id.invoice_reference_type in ('hr', 'invoice') and \
                   debtor_partner.country_id and \
                   debtor_partner.country_id.code == 'HR'
        return super()._eligible_for_qr_code(qr_method, debtor_partner, currency, raises_error=raises_error)

    def _check_for_qr_code_errors(self, qr_method, amount, currency, debtor_partner, free_communication, structured_communication):
        if qr_method == 'hr_qr':
            if not self.acc_holder_name and not self.partner_id.name:
                return _("The account receiving the payment must have an account holder name or partner name set.")

        return super()._check_for_qr_code_errors(qr_method, amount, currency, debtor_partner, free_communication, structured_communication)

    @api.model
    def _get_available_qr_methods(self):
        rslt = super()._get_available_qr_methods()
        rslt.append(('hr_qr', _("HUB3 - QR (Croatia)"), 10))
        # rslt.append(('hr_pdf417', _("PDF417 Barcode sdandard (Croatia)"), 10))
        return rslt
