# Copyright 2023 Ecodica
{
    "name": """Croatian fiscal 2.0 KPD classification""",
    "summary": """Defines KPD classifications.""",
    'description': """
        KPD Classification

        Implemented based on:
        * Klasus - https://web.dzs.hr/App/klasus/

        + https://showvoc.op.europa.eu/#/datasets/ESTAT_Statistical_classification_of_products_by_activity/data

        borrowed and backported from Ecodica 18.0-dev branch
    """,
    "category": "Croatia",
    "images": [],
    "version": "16.0.1.0.0",
    "application": False,
    'author': "Ecodica, Daj mi 5",
    "license": 'LGPL-3',
    #'website': "https://www.ecodica.eu",
    #"support": "support@ecodica.eu",
    "licence": "AGPL-3",

    "depends": [
        "l10n_hr_codebook",
        "account",
    ],
    "external_dependencies": {
        "python": [],
        "bin": []
    },
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Data
        "data/l10n_hr_kpd_data.xml",
        # Views
        "views/l10n_hr_kpd_views.xml",
        "views/product_template_views.xml",
        "views/product_category_views.xml",
        "views/account_move_views.xml",
        "views/menu_items.xml",
    ],
    "qweb": [],
    "demo": [],
    "auto_install": False,
    "installable": True,
}
