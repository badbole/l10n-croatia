# Copyright 2023 Ecodica
{
    "name": """Croatian fiscal 2.0 document type""",
    "summary": """Defines UNTDID1001 document types for Croatian fiscal 2.0""",
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
    ],
    "external_dependencies": {
        "python": [],
        "bin": []
    },
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Data
        "data/l10n.hr.document.type.csv",
        # Views
        "views/l10n_hr_document_type_views.xml",
        "views/account_journal_views.xml",
        "views/menu_items.xml",
    ],
    "qweb": [],
    "demo": [],
    "auto_install": False,
    "installable": True,
}
