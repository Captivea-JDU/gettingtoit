from odoo import api, fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'
    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        vals['freightquote_package_ids'] = [(6,0,self.sale_line_id.order_id.freightquote_package_ids.ids)]
        return vals