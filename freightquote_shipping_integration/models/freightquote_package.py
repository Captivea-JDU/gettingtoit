from odoo import models, fields, api, _


class FreightQuotePackage(models.Model):
    _name = "freightquote.package"

    picking_id = fields.Many2one("stock.picking", string="Delivery Order")
    sale_order_id = fields.Many2one("sale.order", string="sales order")
    freight_class = fields.Selection([('50', '50'),
                                      ('55', '55'),
                                      ('60', '60'),
                                      ('65', '65'),
                                      ('70', '70'),
                                      ('77.5', '77.5'),
                                      ('85', '85'),
                                      ('92.5', '92.5'),
                                      ('100', '100'),
                                      ('110', '110'),
                                      ('125', '125'),
                                      ('150', '150'),
                                      ('175', '175'),
                                      ('200', '200'),
                                      ('250', '250'),
                                      ('300', '300'),
                                      ('400', '400'),
                                      ('500', '500'),
                                      ],help="Products Freight classes")
    weight = fields.Char(string="Weight", help="Please Enter Weight Of Package")
    length = fields.Char(string="Length", help="Please Enter Length Of Package")
    width = fields.Char(string="Width", help="Please Enter Width Of Package")
    height = fields.Char(string="Height", help="Please Enter Height Of Package")

    package_type = fields.Selection([('Unknown', 'Unknown'),
                                     ('Pallets_48x40', 'Pallets_48x40'),
                                     ('Pallets_other', 'Pallets_other'),
                                     ('Bags', 'Bags'),
                                     ('Bales', 'Bales'),
                                     ('Boxes', 'Boxes'),
                                     ('Bundles', 'Bundles'),
                                     ('Carpets', 'Carpets'),
                                     ('Coils', 'Coils'),
                                     ('Crates', 'Crates'),
                                     ('Cylinders', 'Cylinders'),
                                     ('Drums', 'Drums'),
                                     ('Pails', 'Pails'),
                                     ('Reels', 'Reels'),
                                     ('Rolls', 'Rolls'),
                                     ('TubesPipes', 'TubesPipes'),
                                     ('Motorcycle', 'Motorcycle'),
                                     ('ATV', 'ATV'),
                                     ('Pallets_120x120', 'Pallets_120x120'),
                                     ('Pallets_120x100', 'Pallets_120x100'),
                                     ('Pallets_120x80', 'Pallets_120x80'),
                                     ('Pallets_europe', 'Pallets_europe'),
                                     ('Pallets_48x48', 'Pallets_48x48'),
                                     ('Pallets_60x48', 'Pallets_60x48'),
                                     ('Slipsheets', 'Slipsheets'),
                                     ('Unit', 'Unit'),
                                     ], help="Product’s packaging type.")
    commodity_type = fields.Selection([('GeneralMerchandise', 'GeneralMerchandise'),
                                       ('Alcohol', 'Alcohol'),
                                       ('Appliances', 'Appliances'),
                                       ('AutomobileParts', 'AutomobileParts'),
                                       ('ComputerEquipment', 'ComputerEquipment'),
                                       ('ConsumerCareProductsPerfume', 'ConsumerCareProductsPerfume'),
                                       ('ConsumerElectronicsIncludingCellPhonesAndTelevisions',
                                        'ConsumerElectronicsIncludingCellPhonesAndTelevisions'),
                                       ('FoodAndBeverages', 'FoodAndBeverages'),
                                       ('GeneralMerch', 'GeneralMerch'),
                                       ('Metals', 'Metals'),
                                       ('Pharmaceuticals', 'Pharmaceuticals'),
                                       ('Tobacco', 'Tobacco')
                                       ], help="Product’s commodity type")
    content_type = fields.Selection([('NewCommercialGoods', 'NewCommercialGoods'),
                                     ('UsedCommercialGoods', 'UsedCommercialGoods')], help="Product’s content type")
    is_hazardous_material = fields.Boolean(string='IsHazardousMaterial',
                                           help="Determines if product is classified as a hazardous material")
    piece_count = fields.Char(string="Package Piece", help="Number of packaged pieces")
    product_description = fields.Many2one('product.product')
    # item_number = fields.Char(string="ItemNumber")

