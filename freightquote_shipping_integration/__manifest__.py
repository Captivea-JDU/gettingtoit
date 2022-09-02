# -*- coding: utf-8 -*-pack
{

    # App information
    'name': 'FreightQuote Shipping Integration',
    'category': 'Website',
    'version': '15.0.07.07.22',
    'summary': """Using FreightQuote Easily manage Shipping Operation in odoo.Export Order While Validate Delivery Order.Import Tracking From FreightQuote to odoo.Generate Label in odoo.We also Provide the ups,fedex,dhl express shipping integration.""",
    'license': 'OPL-1',

    # Dependencies
    'depends': ['delivery'],

    # Views
    'data': ['security/ir.model.access.csv',
             'views/res_company.xml',
             'views/delivery_carrier.xml',
             'views/sale_order.xml',
             'views/stock_picking.xml'
             ],



    # Odoo Store Specific
    'images': ['static/description/cover.png'],

    # Author
    'author': 'Vraja Technologies',
    'website': 'https://www.vrajatechnologies.com',
    'maintainer': 'Vraja Technologies',

    # Technical
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'live_test_url': 'https://www.vrajatechnologies.com/contactus',
    'price': '321',
    'currency': 'EUR',

}
# Devloped And Tested By Lathiya Mithilesh
# Version Log =  15.0.20.10.21 Initial Stage
# Version Log =  15.0.07.07.22 check error in shipping response

#Features
#1)Label(BOL)
#2)Cancel
#3)Rate
#4)Tracking Url Redirect in site
