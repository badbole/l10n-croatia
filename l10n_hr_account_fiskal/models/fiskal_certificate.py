import base64
import logging
import os
from datetime import datetime

from OpenSSL import crypto as SSLCrypto

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import config as odoo_config

_logger = logging.getLogger(__name__)

PROD = {
    "root": "fina_cert/prod/FinaRootCA.pem",
    "FISKAL 2": "fina_cert/prod/FinaRDCCA2020.pem",
    "FISKAL 1": "fina_cert/prod/FinaRDCCA2015.pem",
}
DEMO = {
    "root": "fina_cert/demo/demo2014_root_ca.pem",
    "FISKAL 2": "fina_cert/demo/demo2020_sub_ca.pem",
    "FISKAL 1": "fina_cert/demo/demo2014_sub_ca.pem",
}

SCHEMA_HELP = """
verzija: 1.3 Datum verzije: 04.07.2016.
- u WSDL-u dodana nova metoda "provjera"
- u schemi dodani novi elementi "ProvjeraZahtjev" i "ProvjeraOdgovor"

verzija: 1.4 Datum verzije: 27.04.2017.
- u WSDL-u izbačena metoda "poslovniProstor"
-u schemi izbačeni elementi "PoslovniProstorZahtjev",
   "PoslovniProstorOdgovor"i ostalo vezano za prijavu poslovnih prostora

verzija: 1.5 Datum verzije: 20.12.2019.
- u WSDL-u dodane dvije metode "prateciDokumenti" i "racuniPD"
- u schemi dodani elementi "PrateciDokumentiZahtjev",
   "PrateciDokumentiOdgovor", "RacunPDZahtjev",
   "RacunPDOdgovor" i ostalo vezano za nove elemente.

verzija: 1.7 Datum verzije: 11.10.2023.
- u WSDL-u dodana nova metoda 'napojnica'
- u schemi dodani elementi "NapojnicaZahtjev",
  "NapojnicaOdgovor" i ostalo vezano za nove elemente.


"""


class FiskalCertificate(models.Model):
    _name = "l10n.hr.fiskal.certificate"
    _description = "Fiskal certificate store"

    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda s: s.env.user.company_id,
    )
    # 1. load cert file fields
    cert_file = fields.Binary(string="Received cert file")
    cert_file_name = fields.Char()
    cert_password = fields.Char(string="Password for certificate")
    # the rest of fields filled on cert conversion
    name = fields.Char(readonly=True)
    cert_type = fields.Selection(
        selection=[
            ("prod", "Fiskal Prod"),
            ("demo", "Fiskal Demo"),
            ("other", "Other/Unknown"),
        ],
        readonly=True,
    )
    fiskal_schema = fields.Selection(
        selection=[
            ("EDUC_v1.6", "DEMO schema v1.6"),
            ("PROD_v1.6", "PROD Schema v1.6"),
        ],
        string="Fiskalizaction schema",
        help=SCHEMA_HELP,
    )
    cert_issuer = fields.Char(
        readonly=True,
    )
    cert_subject = fields.Char(
        readonly=True,
    )
    cert_oib = fields.Char(
        readonly=True,
    )
    pem_key = fields.Text(
        string="Private key",
        readonly=True,
        help="Private key from user P12/PFX cert file",
    )
    pem_crt = fields.Text(
        string="Certificate",
        readonly=True,
        help="Fiskal certificate from user P12/PFX cert file",
    )
    not_before = fields.Datetime(readonly=True)
    not_after = fields.Datetime(readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("convert", "Converted"),
            ("active", "Active"),
            ("expired", "Expired"),
            ("cancel", "Cancelled"),
        ],
        readonly=True,
        default="draft",
        tracking=1,
    )

    def button_convert_p12(self):
        self.ensure_one()
        if not self.cert_file:
            return False
        _password = self.cert_password or ""
        try:
            p12 = SSLCrypto.load_pkcs12(base64.decodebytes(self.cert_file), _password)
        except Exception as E:
            _logger.error(repr(E))
            raise UserError(
                _("Certificate access error, check password or uploaded file type!")
            )

        cert = p12.get_certificate()
        issuer = dict(cert.get_issuer().get_components())
        subject = dict(cert.get_subject().get_components())
        p12.get_friendlyname().decode("utf-8")
        cert_not_before = cert.get_notBefore().decode("utf-8")
        cert_not_after = cert.get_notAfter().decode("utf-8")
        self.not_before = datetime.strptime(cert_not_before, "%Y%m%d%H%M%SZ")
        self.not_after = datetime.strptime(cert_not_after, "%Y%m%d%H%M%SZ")
        self.cert_issuer = " | ".join(
            [
                issuer[b"O"].decode("utf-8"),
                issuer.get(b"CN", issuer.get(b"OU", b"")).decode("utf-8"),
            ]
        )
        self.cert_subject = " | ".join(
            [subject[b"O"].decode("utf-8"), subject[b"CN"].decode("utf-8")]
        )
        self.name = " | ".join(
            [
                subject[b"CN"].decode("utf-8"),
                issuer.get(b"CN", issuer.get(b"OU", b"")).decode("utf-8"),
                subject[b"O"].decode("utf-8"),
            ]
        )
        self.cert_oib = subject[b"O"].decode("utf-8").split(" ")[-1]
        self.pem_key = SSLCrypto.dump_privatekey(
            SSLCrypto.FILETYPE_PEM, p12.get_privatekey()
        )
        self.pem_crt = SSLCrypto.dump_certificate(
            SSLCrypto.FILETYPE_PEM, p12.get_certificate()
        )

        self.state = "convert"
        self.cert_type = "demo" if "demo" in self.cert_issuer.lower() else "prod"
        self.fiskal_schema = self.cert_type == "demo" and "EDUC_v1.6" or "PROD_V1.6"
        # fiskal_path = self.company_id._get_fiskal_path()
        # cert_paths = self.cert_type == "demo" and DEMO or PROD
        # sub_cert = subject.get(b"CN", False)
        # sub_cert = sub_cert == b"FISKAL 2" and "FISKAL 2" or "FISKAL 1"

    def action_validate(self):
        for cert in self:
            if cert.not_after < fields.Datetime.now():
                cert.state = "expired"
            else:
                cert.state = "active"
            if not cert.company_id.l10n_hr_fiskal_cert_id:
                cert.company_id.l10n_hr_fiskal_cert_id = cert

    def action_cancel(self):
        for cert in self:
            cert.state = "cancel"

    def unlink(self):
        for cert in self:
            if cert.state == "active":
                raise UserError(_("Deleting active certificate is not allowed!"))
        return super().unlink()

    def _get_datastore_path(self):
        return odoo_config.filestore(self._cr.dbname)

    def _get_fiskal_cert_path(self):
        fisk_cert_path = os.path.join(self._get_datastore_path(), "l10n_hr")
        if not os.path.exists(fisk_cert_path):
            os.mkdir(fisk_cert_path, 4600)  # setuid,rw, minimal rights applied
        return fisk_cert_path

    def _get_key_cert_file_name(self):
        key = "{}-{}-{}_key.pem".format(self.cert_type, self.id, self._cr.dbname)
        crt = "{}-{}-{}_crt.pem".format(self.cert_type, self.id, self._cr.dbname)
        # fina = "{}-{}-{}_fina.pem".format(self.cert_type, self.id, self._cr.dbname)
        return key, crt

    def _disk_check_exist(self, file):
        return os.path.exists(file)

    def _disk_same_content(self, file, content):
        try:
            with open(file, mode="r") as f:
                on_disk = f.read()
                f.close
        except Exception:
            on_disk = False
        return not on_disk == content

    def _disk_write_content(self, file, content):
        with open(file, mode="w") as f:
            f.write(content)
            f.flush()

    def get_fiskal_ssl_data(self):
        """
        key and cert are stored on disk because
        ssl and crypto libraries expect them readable on disk or some url.
        so we store both of them in odoo datastore
        :return:
        """
        production = self.cert_type == "prod"
        f_path = self._get_fiskal_cert_path()
        key, cert = self._get_key_cert_file_name()
        for pem in (key, cert):
            file = os.path.join(f_path, pem)
            if pem.endswith("_key.pem"):
                content = self.pem_key
                key = file
            else:
                content = self.pem_crt
                cert = file

            if self._disk_check_exist(file) or self._disk_same_content(file, content):
                self._disk_write_content(file, content)
        return key, cert, production
