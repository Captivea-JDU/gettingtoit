from odoo import models, fields, api, _
import logging

_logger = logging.getLogger("Freightquote")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    quote_id = fields.Char(string="Quote ID", help="Freightquote Quote ID", readonly=True,copy=False)

    freightquote_package_ids = fields.One2many("freightquote.package", "sale_order_id",
                                               string="Freightquote Package")
    freightquote_shipping_charge_ids = fields.One2many("freightquote.shipping.charge", "sale_order_id",
                                                       string="Freightquote Rate ")
    freightquote_shipping_charge_id = fields.Many2one("freightquote.shipping.charge", string="Freightquote Service",
                                                      help="This Method Is Use Full For Generating The Label",
                                                      copy=False)


    # def set_delivery_line(self, carrier, amount):
    #     # Remove delivery products from the sales order
    #     self._remove_delivery_line()
    #     for order in self:
    #         if order.state not in ('draft', 'sent'):
    #             raise UserError(_('You can add delivery price only on unconfirmed quotations.'))
    #         elif not carrier:
    #             raise UserError(_('No carrier set for this order.'))
    #         else:
    #             price_unit = amount
    #             # TODO check whether it is safe to use delivery_price here
    #             order._create_delivery_line(carrier, price_unit)
    #     return True
