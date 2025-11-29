# Copyright 2025 Ecodica
{
    "name": """UNTDID5189 Discount Code Book""",
    "summary": """Defines additional codebook for discount based on UNTDID5189 standard""",
    'description': """
    """,
    "category": "Sales/Sales",
    "images": [],
    "version": "16.0.1.0.0",
    "application": False,
    'author': "Daj mi 5",
    "license": 'LGPL-3',
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
        "data/l10n.hr.discount.type.csv",
        # Views
        "views/account_move_views.xml",
        "views/untid5189_views.xml.xml",
        "views/menu_items.xml",
    ],
    # "pre_init_hook": '_pre_init_hook',
    # "post_init_hook": '_post_init_hook',
    "qweb": [],
    "demo": [],
    "auto_install": False,
    "installable": True,
}
