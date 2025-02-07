# -*- coding: utf-8 -*-
{
    'name': "l10n_hr_hub3_qr_code",

    'description': """
        This module adds support for HUB3 Croatian local format QR-code generation.
    """,

    'category': 'Accounting/Payment',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'base_iban',
        'l10n_hr_account_reference',
    ],

    'auto_install': True,
    'license': 'LGPL-3',
}
