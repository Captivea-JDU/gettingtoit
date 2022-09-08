# -*- coding: utf-8 -*-

from datetime import date
from odoo import api, models, fields
import logging
_logger = logging.getLogger(__name__)

class CustomModExtended(models.Model):

    _inherit = 'sale.order'
    # _inherit = 'product.template'
    
    cap_year = fields.Integer(string='Year')
    cap_customer_birth_year = fields.Integer(string='Customer Birth Year')
    cap_customer_phone_number = fields.Char(string='Customer phone number')
    cap_customer_nickname = fields.Char(string='Customer Nickname')
    cap_customer_age = fields.Integer(string='Customer Age')
    cap_customer_address = fields.Char(string='Customer Address')
    cap_customer_favorite_genre = fields.Char(string='Favorite Genre')
    cap_display_type = fields.Char(string='Cap Display Type')
    cap_display_type1 = fields.Char(string='Cap Display Type1')
    cap_sequence = fields.Integer(string='Cap Sequence')
    cap_product_uom_category_id = fields.Char(string='Cap Product uom Category ID')
    cap_product_id = fields.Integer(string='Product ID')
    cap_invoice_status = fields.Char(string='Cap Invoice Status')
    cap_qty_to_invoice = fields.Integer(string='Cap QTY To Invoice')
    cap_product_uom_qty = fields.Integer(string='Cap Product uom qty')
    cap_product_uom = fields.Char(string='Cap Product Uom')
    cap_qty_delivered = fields.Integer(string='Cap QTY Delivered')
    cap_qty_invoiced = fields.Integer(string='Cap QTY Invoice')
    cap_price_unit = fields.Integer(string='Cap Price Unit')
    cap_tax_id = fields.Char(string='Cap Tax ID')
    cap_discount = fields.Integer(string='Cap Discount')
    cap_customer_lead = fields.Char(string='Cap Customer Lead')
    cap_analytic_tag_ids = fields.Integer(string='Cap Analytic tag id')
    cap_name = fields.Char(string='Cap Name')
    cap_last_name = fields.Char(string='Cap Last Name')
    cap_invoice_lines = fields.Char(string='Cap Invoice Lines')
    cap_state = fields.Integer(string='Cap State')
    cap_company_id = fields.Char(string='Cap Company ID')
    cap_product_packaging_id = fields.Char(string='Cap Product Packaging ID')
    cap_selection_field = fields.Selection([('knowledge', 'Knowledge'),('wisdom', 'Wisdom'),('understanding', 'Understanding')], string='Cap Selection Field')
    cap_four_math = fields.Selection([('freedom', 'Freedom'),('culture', 'Culture'),('power', 'Power'),('refinement', 'Refinement')], string='Todays Mathmatics')
    cap_ayo = fields.Many2one('res.partner', string='Call these folk')
    #@api.onchange('cap_year')
    #def calculate_age(cap_year):
        #cap_year = 2023
        #cap_customer_age = cap_year

        #return cap_customer_age