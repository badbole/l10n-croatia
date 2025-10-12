import base64
import io
import logging
from datetime import datetime

import qrcode

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..fiskal import fiskal

_logger = logging.getLogger(__name__)


class FiscalFiscalMixin(models.AbstractModel):
    """
    Basic fields and methods for all fiscal classes
    - inherit for invoice, sale, procurment etc...
    """

    _name = "l10n.hr.fiskal.mixin"
    _description = "Croatia Fiscalisation base mixin"

    def _generate_fiskal_qr_code(self):
        self.ensure_one()
        data = "https://porezna.gov.hr/rn?"
        if self.l10n_hr_jir:
            data += "jir=" + self.l10n_hr_jir  # fiskalizirani racun
        else:
            # ispis prije poslane fiskalne poruke ili je poslana poruka
            # imala neku gresku pa JIR nije dodjeljen
            data += "zki=" + self.l10n_hr_zki
        datum = datetime.strptime(
            self.l10n_hr_vrijeme_izdavanja, "%d.%m.%Y %H:%M"
        ).strftime("%Y%m%d_%H%M")
        data += "&datv=" + datum
        iznos = "&izn=%.2f" % self.amount_total
        data += iznos.replace(".", "")  # bez decimalne tocke u linku!
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)
        try:
            img = qr.make_image(fill_color="black", back_color="white")
            ret = io.BytesIO()
            img.save(ret, img.kind)
            ret.seek(0)
            res = base64.b64encode(ret.getvalue())
        except Exception as e:
            _logger.error(repr(e))
            res = False
        return res

    @api.depends("l10n_hr_jir", "l10n_hr_zki")
    def _compute_l10n_hr_fiskal_qr(self):
        for inv in self:
            if not inv.l10n_hr_jir and not inv.l10n_hr_zki:
                inv.l10n_hr_fiskal_qr
                continue
            inv.l10n_hr_fiskal_qr = self._generate_fiskal_qr_code()

    l10n_hr_zki = fields.Char(string="ZKI", readonly=True, copy=False)
    l10n_hr_jir = fields.Char(string="JIR", readonly=True, copy=False)
    l10n_hr_fiskal_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Fiscal user",
        help="User who sent the fiscalisation message to FINA."
        " Can be different from responsible person on invoice.",
    )
    # l10n_hr_vrijeme_xml = fields.Char(  # probably not needed but heck...
    #     string="XML time",
    #     help="Value for fiscalization msg stored as string",
    #     size=19,
    #     readonly=True,
    #     copy=False,
    # )
    l10n_hr_paragon_br = fields.Char(
        "Paragon nr.",
        readonly=True,
        copy=False,
        states={"draft": [("readonly", False)]},
        # TODO translateME!
        help="If system was down, and invoice is records on 'paragon blok',"
        ". This needs to be entered BEFORE confirming the invoice.",
    )
    l10n_hr_late_delivery = fields.Boolean(
        string="Late delivery",
        readonly=True,
        copy=False,
        states={"draft": [("readonly", False)]},
        help="Checked if message could not be sent at time of invoicing",
    )
    l10n_hr_fiskal_qr = fields.Binary(
        compute="_compute_l10n_hr_fiskal_qr",
        help="Binary field visible in the interface",
    )

    def _l10n_hr_post_fiskal_check(self):
        res = []

        if (
            self.l10n_hr_fiskal_uredjaj_id.fiskalisation_active
            and not self.company_id.partner_id.vat
        ):
            res.append(
                _("Comapny OIB is not not entered! It is required for fiscalisation")
            )
        if (
            self.l10n_hr_fiskal_uredjaj_id.fiskalisation_active
            and not self.l10n_hr_fiskal_user_id.partner_id.vat
        ):
            res.append(
                _("User OIB is not not entered! It is required for fiscalisation")
            )
        if (
            self.l10n_hr_nacin_placanja != "T"
            and not self.company_id.l10n_hr_fiskal_cert_id
        ):
            res.append(
                _(
                    "No fiscal certificate found, please install one "
                    "activate and select it on company setup!"
                )
            )
        return res

    def _get_fisk_tax_values(self):
        tax_data = {
            "Pdv": {},
            "Pnp": {},
            "OstaliPor": [],
            "Naknade": [],
        }
        iznos_oslob_pdv, iznos_ne_podl_opor, iznos_marza = 0.00, 0.00, 0.00

        base_lines = self.invoice_line_ids.filtered(
            lambda line: line.display_type == "product"
        )
        base_line_values_list = [
            line._convert_to_tax_base_line_dict() for line in base_lines
        ]

        for line in base_line_values_list:
            for tax in line["taxes"]:
                # TODO: taxex with 0 percent have no tax line !!!
                # for now, let's assume we have tax lines with amount zero!
                if not tax.l10n_hr_fiskal_type:
                    raise ValidationError(_("Tax '%s' missing fiskal type!") % tax.name)
                fiskal_type = tax.l10n_hr_fiskal_type
                naziv = tax.name
                stopa = tax.amount  # if amount type == percent??
                osnovica = line["price_subtotal"]
                iznos = 0.0
                if stopa != 0.0:
                    iznos = osnovica * 100 / stopa

                if fiskal_type == "Pdv":
                    if tax_data["Pdv"].get(stopa):
                        tax_data["Pdv"][stopa]["Osnovica"] += osnovica
                        tax_data["Pdv"][stopa]["Iznos"] += iznos
                    else:
                        tax_data["Pdv"][stopa] = {"Osnovica": osnovica, "Iznos": iznos}
                elif fiskal_type == "Pnp":
                    if tax_data["Pnp"].get(stopa):
                        tax_data["Pnp"][stopa]["Osnovica"] += osnovica
                        tax_data["Pnp"][stopa]["Iznos"] += iznos
                    else:
                        tax_data["Pnp"][stopa] = {"Osnovica": osnovica, "Iznos": iznos}
                elif fiskal_type == "OstaliPor":
                    tax_data["OstaliPor"].append(
                        {
                            "Naziv": naziv,
                            "Stopa": stopa,
                            "Osnovica": osnovica,
                            "Iznos": iznos,
                        }
                    )
                elif fiskal_type == "Naknade":
                    tax_data["Naknade"].append({"NazivN": naziv, "IznosN": iznos})
                elif fiskal_type == "oslobodenje":
                    iznos_oslob_pdv += osnovica
                elif fiskal_type == "ne_podlijeze":
                    iznos_ne_podl_opor += osnovica
                elif fiskal_type == "marza":
                    iznos_marza += osnovica

        if iznos_oslob_pdv:
            tax_data["IznosOslobPdv"] = fiskal.format_decimal(iznos_oslob_pdv)
        if iznos_ne_podl_opor:
            tax_data["IznosNePodlOpor"] = fiskal.format_decimal(iznos_ne_podl_opor)
        if iznos_marza:
            tax_data["IznosMarza"] = fiskal.format_decimal(iznos_marza)
        return tax_data

    def _prepare_fisk_racun_taxes(self, factory):
        res = {}
        if not self.company_id.l10n_hr_fiskal_taxative:
            return res
        tax_data = self._get_fisk_tax_values()
        for pdv in tax_data["Pdv"]:
            if not res.get("Pdv"):
                res["Pdv"] = []
            _pdv = tax_data["Pdv"][pdv]
            porez = factory.type_factory.PorezType(
                Stopa=fiskal.format_decimal(pdv),
                Osnovica=fiskal.format_decimal(_pdv["Osnovica"]),
                Iznos=fiskal.format_decimal(_pdv["Iznos"]),
            )
            res["Pdv"].append(porez)
        for pnp in tax_data["Pnp"]:
            if not res.get("Pnp"):
                res["Pnp"] = []
            _pnp = tax_data["Pnp"][pnp]
            porez = factory.type_factory.PorezType(
                Stopa=fiskal.format_decimal(pnp),
                Osnovice=fiskal.format_decimal(_pnp["Osnovica"]),
                Iznos=fiskal.format_decimal(_pnp["Iznos"]),
            )
            res["Pnp"].append(porez)

        # - currenty no such
        # for ost in tax_data['OstaliPor']:
        #     _ost = tax_data['OstaliPor'][ost]
        #     porez = factory.type_factory.Porez
        #     porez.Naziv = _ost['Naziv']
        #     porez.Stopa = fiskal.format_decimal(ost)
        #     porez.Osnovica = fiskal.format_decimal(_ost['Osnovica'])
        #     porez.Iznos = fiskal.format_decimal(_pnp['Iznos'])
        #     racun.OstaliPor.Porez.append(porez)

        for nak in tax_data["Naknade"]:
            if not res.get("Naknade"):
                res["Naknade"] = []
            naziv, iznos = nak
            naknada = factory.type_factory.Naknada(
                NazivN=naziv, IznosN=fiskal.format_decimal(iznos)
            )
            res["Naknade"].append(naknada)
        return res

    def _prepare_fisk_racun(self, factory, fiskal_data):
        porezi = self._prepare_fisk_racun_taxes(factory)
        BrRac = factory.type_factory.BrojRacunaType(
            BrOznRac=fiskal_data["racun"][0],
            OznPosPr=fiskal_data["racun"][1],
            OznNapUr=fiskal_data["racun"][2],
        )
        pdv, pnp = None, None
        if porezi.get("Pdv", None):
            pdv = factory.type_factory.PdvType(Porez=porezi["Pdv"])
        if porezi.get("Pnp", None):
            pnp = factory.type_factory.PnpType(Porez=porezi["Pnp"])
        oib_company = self.company_id.partner_id.vat[2:]
        if self.company_id.l10n_hr_fiskal_cert_id.cert_type == "demo":
            # demo cert na tudjoj bazi... onda ide oib iz certa
            oib_company = self.company_id.l10n_hr_fiskal_cert_id.cert_oib[2:]
        racun = factory.type_factory.RacunType(
            Oib=oib_company,
            USustPdv=self.company_id.l10n_hr_fiskal_taxative,
            DatVrijeme=fiskal_data["time"]["datum_vrijeme"],
            OznSlijed=self.l10n_hr_fiskal_uredjaj_id.prostor_id.sljed_racuna,
            BrRac=BrRac,
            Pdv=pdv,
            Pnp=pnp,
            IznosOslobPdv=porezi.get("PdvIznosOslobPdv", None),
            IznosMarza=porezi.get("IznosMarza", None),
            IznosNePodlOpor=porezi.get("IznosNePodlOpor", None),
            # Naknade=ws_naknade,
            IznosUkupno=fiskal.format_decimal(self.amount_total),
            NacinPlac=self.l10n_hr_nacin_placanja,
            OibOper=self.l10n_hr_fiskal_user_id.partner_id.vat[2:],
            ZastKod=self.l10n_hr_zki,
            NakDost=self.l10n_hr_late_delivery,
            ParagonBrRac=self.l10n_hr_paragon_br or None,
            # See Fiskalizacija Tehnička specifikacija, section 13: Errors
            # error v125: "Trenutno ne postoje 'Ostali porezi'"
            OstaliPor=None,
            # error v141: Polje 'Specifična namjena' je namijenjeno za buduće potrebe.
            SpecNamj=None,
        )
        return racun

    def fiskaliziraj(self, msg_type="racuni"):
        """
        Fiskalizira jedan izlazni racun ili point of sale račun
        msg_type : Racun,
        """
        if self.l10n_hr_jir and len(self.l10n_hr_jir) > 30:
            # existing in shema 1.4 not in 1.5!
            if msg_type != "provjera":
                msg_type = "provjera"
        if self.l10n_hr_zki and not self.l10n_hr_jir and not self.l10n_hr_late_delivery:
            # imam ZKI, nemam jir = naknadna dostava
            self.l10n_hr_late_delivery = True
        time_start = self.company_id.get_l10n_hr_time_formatted()
        if not self.l10n_hr_fiskal_user_id:
            # MUST USE CURRENT user for fiscalization!
            # Except in case of paragon račun? or naknadna dostava?
            # but then it should be manualy entered already!
            self.l10n_hr_fiskal_user_id = self._uid

        errors = self._l10n_hr_post_fiskal_check()
        if errors:
            msg = _("Fiscalisation not possible: \n")
            msg += "\n".join(errors)
            raise ValidationError(msg)

        fiskal_data = self.company_id.get_fiskal_data()
        fiskal_data["time"] = time_start
        fis_racun = self.l10n_hr_fiskalni_broj.split(
            self.company_id.l10n_hr_fiskal_separator
        )
        assert len(fis_racun) == 3, "Invoice must be assembled using 3 values!"
        fiskal_data["racun"] = fis_racun
        if not self.l10n_hr_zki:
            if fiskal_data["demo"]:
                # uzimam oib iz certifikata, bez obzira na company oib
                oib = fiskal_data["cert_oib"]
            else:
                oib = fiskal_data["company_oib"]

            zki_datalist = [
                oib[2:],
                self.l10n_hr_vrijeme_izdavanja or time_start["datum_racun"],
                fis_racun[0],
                fis_racun[1],
                fis_racun[2],
                fiskal.format_decimal(self.amount_total),
            ]
            fisk = fiskal.Fiskalizacija(fiskal_data=fiskal_data)
            self.l10n_hr_zki = fiskal.generate_zki(
                zki_datalist=zki_datalist, signer=fisk.signer
            )
        fisk = fiskal.Fiskalizacija(fiskal_data=fiskal_data)
        if msg_type in ["racuni", "provjera"]:
            racun = self._prepare_fisk_racun(factory=fisk, fiskal_data=fiskal_data)
            zaglavlje = fisk.create_request_header()  # self._create_fiskal_header(fisk)
            req_kw = dict(Zaglavlje=zaglavlje, Racun=racun)
            service_proxy = fisk.client.service.racuni
            response = fisk._call_service(service_proxy, req_kw)
        self.company_id.create_fiskal_log(msg_type, fisk, response, time_start, self)
        if hasattr(response, "Jir"):
            if not self.l10n_hr_jir:
                self.l10n_hr_jir = response.Jir
