from odoo import models, fields

class freightquoteshippingcharge(models.Model):
    _name = "freightquote.shipping.charge"
    _rec_name = "freightquote_carrier_name"

    freightquote_carrier_id = fields.Char(string="Carrier ID",help="Freightquote carrier id")
    freightquote_carrier_name = fields.Char(string="Carrier Name", help="Freightquote courier name")
    estimated_delivery_time = fields.Char(string="Estimated Days",help="Freightquote Estimated DeliveryTime")
    freightquote_total_charge = fields.Float(string="Total Charge", help="rate given by Freightquote")
    sale_order_id = fields.Many2one("sale.order", string="sales order")
    picking_id = fields.Many2one("stock.picking", string="Delivery Order")


    def set_service(self):
        self.ensure_one()
        if self.sale_order_id:
            carrier = self.sale_order_id.carrier_id
            self.sale_order_id.freightquote_shipping_charge_id = self.id
            self.sale_order_id.carrier_id = carrier.id
            self.sale_order_id.set_delivery_line(carrier, self.freightquote_total_charge)#this line used for set updated rate in sale order line
        if self.picking_id:
            carrier = self.picking_id.carrier_id
            self.picking_id.freightquote_shipping_charge_id = self.id
            self.picking_id.carrier_id = carrier.id
