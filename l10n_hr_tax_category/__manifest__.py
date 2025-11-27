# Copyright 2023 Ecodica
{
    "name": """Croatian fiscal 2.0 Tax Categories""",
    "summary": """Defines Tax Categories with UNTDID(5305/5153) codebooks for Croatian fiscal 2.0""",
    "category": "Croatia",
    "countries": ['hr'],
    "images": [],
    "version": "16.0.1.0.0",
    "application": False,
    'author': "Ecodica, Daj mi 5",
    "license": 'LGPL-3',
    #'website': "https://www.ecodica.eu",
    #"support": "support@ecodica.eu",

    "depends": [
        #"l10n_hr",
        "l10n_hr_codebook",
    ],
    "external_dependencies": {
        "python": [],
        "bin": []
    },
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Data
        "data/l10n.hr.tax.category.csv",
        # Views
        "views/l10n_hr_tax_category_views.xml",
        "views/account_tax_views.xml",
        "views/menu_items.xml",
    ],
    "qweb": [],
    "demo": [],
    "auto_install": False,
    "installable": True,
}
