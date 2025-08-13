# -*- coding: utf-8 -*-
{
    'name': "SMS Evolution",
    'summary': "SMS Evolution Connector",
    'author': "Ricardo Pérez",
    'website': "https://github.com/OCA/connector-telephony",
    'category': 'SMS',
    'version': '18.0.0.0.1',
    'application': False,
    'installable': True,
    'depends': ["base_phone", "sms", "iap_alternative_provider"],
    'license': 'AGPL-3',
    "data": [
        "views/iap_account_views.xml",
    ],
}

