# -*- coding: utf-8 -*-
"""For Odoo Magento2 Connector Module"""
from odoo import models, fields, api, _
MAGENTO_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

import json

class SaleOrderLine(models.Model):
    """
    Describes Sale order line
    """
    _inherit = 'sale.order.line'
    _description = 'Sale Order Line'

    magento_sale_order_line_ref = fields.Char(
        string="Magento Sale Order Line Reference",
        help="Magento Sale Order Line Reference"
    )

    @api.model
    def magento_create_sale_order_line(self, magento_instance, order_response, magento_order, job, order_dict):
        """
        This method used for create a sale order line.
        :param magento_instance: Instance of Magento
        :param order_response: Order response received from Magento
        :param magento_order: Order Id
        :return: Sale order Lines
        """
        magento_product = self.env['magento.product.product']
        sale_lines_response = order_response.get('items')
        sale_order_lines = []
        skip_order = False
        store_id = order_response.get('store_id')
        store_view = magento_instance.website_ids.store_view_ids.filtered(
            lambda x: x.magento_storeview__id == str(store_id)
        )
        tax_calculation_method = store_view and store_view.magento_website_id.tax_calculation_method
        for item in sale_lines_response:
            if item.get('product_type') in ['bundle', 'configurable']:
                continue
            product_id = item.get('product_id')
            product_sku = item.get('sku')
            order_item_id = item.get('item_id')
            # add below line for
            # if product is simple and item having parent_item
            # (it means that product is child product of any configurable product) then get the price from the parent_item
            # other wise take the price from the items dict.

            # Start the code to get the custom option title and custom option value title from the Extension attribute.
            description = self.get_custom_option_title(order_item_id, order_response)
            # Over the code to get the custom option title and custom option value title from the Extension attribute.
            if tax_calculation_method == 'excluding_tax':
                price = item.get('parent_item').get('price') if "parent_item" in item else item.get(
                    'price')
            else:
                price = item.get('parent_item').get('price_incl_tax') if "parent_item" in item else item.get(
                    'price_incl_tax')
            original_price = item.get('parent_item').get('original_price') if "parent_item" in item else item.get(
                'original_price')
            if price != original_price:
                item_price = price
            else:
                item_price = original_price
            magento_product = magento_product.search([
                ('magento_sku', '=', product_sku),
                ('magento_instance_id', '=', magento_instance.id)
            ], limit=1)
            if not magento_product:
                magento_product = magento_product.search([
                    ('magento_product_id', '=', product_id),
                    ('magento_instance_id', '=', magento_instance.id)
                ], limit=1)
            if not magento_product:
                product_obj = self.env['product.product'].search([('default_code', '=', product_sku)])
                if not product_obj:
                    continue
                elif len(product_obj) > 1:
                    skip_order = True
                    message = _("An order {} was skipped because the ordered product {} exists multiple "
                                "times in Odoo.".format(order_response['increment_id'], product_sku))
                    job.add_log_line(message, order_response['increment_id'],
                                     order_dict.id, "magento_order_data_queue_line_id")
                    return skip_order, []
                odoo_product = product_obj
            else:
                odoo_product = magento_product.odoo_product_id
            sale_order_line = self.create_sale_order_line_vals(
                item,
                item_price,
                odoo_product,
                magento_order,
            )
            if order_response.get(f'order_tax_{item.get("item_id")}'):
                sale_order_line.update({'tax_id': [(6, 0, order_response.get(f'order_tax_{item.get("item_id")}'))]})
            order_line = self.create(sale_order_line)
            order_line.write({
                'name': description if description else order_line.name
            })
            sale_order_lines.append(order_line)
        return skip_order, sale_order_lines

    def get_custom_option_title(self,order_item_id,order_response):
        """
        :param product_id: Product ID
        :param order_response: Order REST API response
        :return: Merge all the custom option value and prepare the string per
         order item if the item having the custom option in sale order.
        Set that string in the sale order line.
        """
        description = ""
        extension_attributes = order_response.get("extension_attributes")
        ept_option_title = extension_attributes.get('ept_option_title')
        if ept_option_title:
            for custom_opt_itm in ept_option_title:
                custom_opt = json.loads(custom_opt_itm)
                if order_item_id == int(custom_opt.get('order_item_id')):
                    for option_data in custom_opt.get('option_data'):
                        description += option_data.get('label') + " : " + option_data.get('value') + "\n"
        return description

    def create_sale_order_line_vals(
            self,
            order_line_dict,
            price_unit,
            odoo_product = False,
            magento_order=False,
    ):
        """
        Create Sale Order Line Values
        :param order_line_dict:  Magento sale order line object
        :param price_unit: price unit object
        :param odoo_product: odoo product object
        :param magento_order: Magento order object
        :return:
        """
        order_qty = float(order_line_dict.get('qty_ordered', 1.0))
        magento_sale_order_line_ref = order_line_dict.get('parent_item_id') or order_line_dict.get('item_id')
        tag_ids = magento_order.magento_instance_id.magento_analytic_tag_ids and magento_order.magento_instance_id.magento_analytic_tag_ids.ids or []
        if not tag_ids:
            tag_ids = magento_order.magento_website_id.m_website_analytic_tag_ids and magento_order.magento_website_id.m_website_analytic_tag_ids.ids or []
        uom_id = False
        if odoo_product and odoo_product.uom_id.id:
            uom_id = odoo_product and odoo_product.uom_id.id
        order_line_vals = {
            'order_id': magento_order.id,
            'product_id': odoo_product and odoo_product.id or False,
            'company_id': magento_order.company_id.id,
            'name': order_line_dict.get('name'),
            'description': odoo_product.name or (magento_order and magento_order.name),
            'product_uom': uom_id,
            'order_qty': order_qty,
            'price_unit': price_unit,
        }
        order_line_vals = self.create_sale_order_line_ept(order_line_vals)
        order_line_vals.update({
            'magento_sale_order_line_ref': magento_sale_order_line_ref,
            "analytic_tag_ids": [(6, 0, tag_ids)],
        })
        return order_line_vals

    def find_order_tax(self, item, instance, log, line_id):
        order_line = self.env['sale.order.line']
        account_tax_obj = self.env['account.tax']
        tax_details = self.__find_tax_percent_title(item, instance)
        tax_id_list = []
        for tax in tax_details:
            tax_id = account_tax_obj.get_tax_from_rate(
                float(tax.get('tax_percent')), tax.get('tax_title'), tax.get('tax_type'))
            if tax_id and not tax_id.active:
                message = _(f"""
                Order {item['increment_id']} was skipped because the tax {tax_id.name}% was not found. 
                The connector is unable to create new tax {tax_id.name}%, kindly check the tax 
                {tax_id.name}% has been archived? 
                """)
                log.write({'log_lines': [(0, 0, {
                    'message': message, 'order_ref': item['increment_id'],
                    'magento_order_data_queue_line_id': line_id
                })]})
                return [], True
            if not tax_id:
                tax_vals = order_line.prepare_tax_dict(tax, instance)
                tax_id = account_tax_obj.sudo().create(tax_vals)
            if tax.get('line_tax') != 'shipping_tax':
                item.update({tax.get('line_tax'): tax_id.ids})
            else:
                tax_id_list.append(tax_id.id)
        if tax_id_list:
            item.update({'shipping_tax': tax_id_list})
        return False

    def __find_shipping_tax_percent(self, tax_details, ext_attrs):
        if "item_applied_taxes" in ext_attrs:
            tax_type = self.__find_tax_type(ext_attrs, 'apply_shipping_on_prices')
            for order_res in ext_attrs.get("item_applied_taxes"):
                if order_res.get('type') == "shipping" and order_res.get('applied_taxes'):
                    for tax in order_res.get('applied_taxes', list()):
                        tax_details.append({
                            'line_tax': 'shipping_tax', 'tax_type': tax_type, 'tax_title': tax.get('title'),
                            'tax_percent': tax.get('percent', 0)})
        return tax_details

    def __find_tax_percent_title(self, item, instance):
        tax_details = []
        if instance.magento_apply_tax_in_order == 'create_magento_tax':
            if 'apply_discount_on_prices' in item.get('extension_attributes'):
                tax_type = self.__find_tax_type(item.get('extension_attributes'),
                                                'apply_discount_on_prices')
                tax_percent = self.__find_discount_tax_percent(item.get('items'))
                tax_name = '%s %% ' % tax_percent
                tax_details.append(
                    {'line_tax': 'discount_tax', 'tax_type': tax_type, 'tax_title': tax_name, 'tax_percent': tax_percent})
            if 'apply_shipping_on_prices' in item.get('extension_attributes'):
                ext_attrs = item.get('extension_attributes')
                tax_details = self.__find_shipping_tax_percent(tax_details, ext_attrs)
            else:
                for line in item.get('items'):
                    tax_percent = line.get('tax_percent', 0.0)
                    parent_item = line.get('parent_item', {})
                    if parent_item and parent_item.get('product_type') != 'bundle':
                        tax_percent = line.get('parent_item', {}).get('tax_percent', 0.0)
                    if tax_percent:
                        tax_name = '%s %% ' % tax_percent
                        tax_type = (item.get('website').tax_calculation_method == 'included_tax')
                        tax_details.append(
                            {'line_tax': f'order_tax_{line.get("item_id")}', 'tax_type': tax_type, 'tax_title': tax_name, 'tax_percent': tax_percent})
        return tax_details

    @staticmethod
    def __find_tax_type(ext_attrs, tax):
        tax_type = False
        if tax in ext_attrs:
            tax_price = ext_attrs.get(tax)
            if tax_price == 'including_tax':
                tax_type = True
        return tax_type

    @staticmethod
    def __find_discount_tax_percent(items):
        percent = False
        for item in items:
            percent = item.get('tax_percent') if 'tax_percent' in item.keys() and item.get('tax_percent') > 0 else False
            if percent:
                break
        return percent
