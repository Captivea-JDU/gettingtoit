# -*- coding: utf-8 -*-

{
    'name': 'Custom Module',
    'category': 'Sales',
    'summary': "This is a custom module",
    'version': '1.0 (v13)',
    'author': 'Captivea software Consulting, Jarvis Dumas',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """This is a custom module
        """,
    'depends': ['base', 'sale'],
    'data': [
        'views/views.xml',
        'views/cap_product_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
