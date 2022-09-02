from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.addons.freightquote_shipping_integration.models.freightquote_response import Response
import xml.etree.ElementTree as etree
import requests
import logging

_logger = logging.getLogger("Freightquote")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    freightquote_bol_url = fields.Char(string="Freightquote Bill Of Loading", help="bill of loading url", copy=False)
    freightquote_shipping_charge_ids = fields.One2many("freightquote.shipping.charge", "picking_id")
    freightquote_shipping_charge_id = fields.Many2one("freightquote.shipping.charge", string="Freightquote Service",
                                                      help="This Method Is Use Full For Generating The Label",
                                                      copy=False)
    freightquote_package_ids = fields.One2many("freightquote.package", "picking_id",
                                               string="Freightquote Package")
    quote_id = fields.Char(string="Quote ID", help="Freightquote Quote ID", readonly=True, copy=False)

    def get_freightquote_rate(self):
        freightquote_shipping_charege_obj = self.env['freightquote.shipping.charge']
        shipper_address = self.picking_type_id.warehouse_id.partner_id
        recipient_address = self.partner_id

        # Master Node
        master_node = etree.Element("soap:Envelope")
        master_node.attrib['xmlns:soap'] = "http://schemas.xmlsoap.org/soap/envelope/"
        master_node.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        master_node.attrib['xmlns:xsd'] = "http://www.w3.org/2001/XMLSchema"

        # Body Node
        body_node = etree.SubElement(master_node, "soap:Body")
        get_ratingengine_quote = etree.SubElement(body_node, "GetRatingEngineQuote")
        get_ratingengine_quote.attrib['xmlns'] = "http://tempuri.org/"

        # Request Node
        request_node = etree.SubElement(get_ratingengine_quote, "request")
        etree.SubElement(request_node, 'QuoteType').text = self.carrier_id.quote_type or ""
        etree.SubElement(request_node, 'ServiceType').text = self.carrier_id.service_type or ""

        quote_shipment = etree.SubElement(request_node, "QuoteShipment")
        etree.SubElement(quote_shipment, 'PickupDate').text = str(self.scheduled_date).split()[0]

        shipment_locations = etree.SubElement(quote_shipment, "ShipmentLocations")

        location = etree.SubElement(shipment_locations, "Location")
        etree.SubElement(location, 'LocationType').text = "Origin"
        location_address = etree.SubElement(location, "LocationAddress")
        etree.SubElement(location_address, 'PostalCode').text = shipper_address.zip or ""
        etree.SubElement(location_address,
                         'CountryCode').text = shipper_address.country_id and shipper_address.country_id.code or ""

        location = etree.SubElement(shipment_locations, "Location")
        etree.SubElement(location, 'LocationType').text = "Destination"
        location_address = etree.SubElement(location, "LocationAddress")
        etree.SubElement(location_address, 'PostalCode').text = recipient_address.zip or ""
        etree.SubElement(location_address,
                         'CountryCode').text = recipient_address.country_id and recipient_address.country_id.code or ""

        shipment_products = etree.SubElement(quote_shipment, "ShipmentProducts")
        counter = 0
        for package in self.freightquote_package_ids:
            counter = counter + 1
            product_node = etree.SubElement(shipment_products, "Product")
            etree.SubElement(product_node, 'Class').text = package.freight_class
            etree.SubElement(product_node, 'Weight').text = package.weight
            etree.SubElement(product_node, 'Length').text = package.length
            etree.SubElement(product_node, 'Width').text = package.width
            etree.SubElement(product_node, 'Height').text = package.height
            etree.SubElement(product_node,
                             'ProductDescription').text = package.product_description.name
            etree.SubElement(product_node, 'PackageType').text = package.package_type
            etree.SubElement(product_node, 'CommodityType').text = package.commodity_type
            etree.SubElement(product_node, 'ContentType').text = package.content_type
            etree.SubElement(product_node,
                             'IsHazardousMaterial').text = "false"  # (str(order.is_hazardous_material)).lower()
            etree.SubElement(product_node, 'PieceCount').text = package.piece_count
            etree.SubElement(product_node, 'ItemNumber').text = str(counter)

        user_node = etree.SubElement(get_ratingengine_quote, "user")
        etree.SubElement(user_node, 'Name').text = self.company_id.freightquote_username or ""
        etree.SubElement(user_node, 'Password').text = self.company_id.freightquote_password or ""
        etree.SubElement(user_node, 'CredentialType').text = self.company_id.freightquote_credential_type or ""

        try:
            headers = {
                'SOAPAction': 'http://tempuri.org/GetRatingEngineQuote',
                'Content-Type': 'text/xml; charset=utf-8'
            }
            url = self.company_id and self.company_id.freightquote_api_url
            _logger.info(master_node)
            response_data = requests.request(method="POST", url=url, headers=headers,
                                             data=etree.tostring(master_node))
            _logger.info(response_data)
            if response_data.status_code in [200, 201]:
                api = Response(response_data)
                response_data = api.dict()
                existing_records = freightquote_shipping_charege_obj.search(
                    [('picking_id', '=', self and self.id)])
                existing_records.sudo().unlink()
                carrier_options = response_data.get('Envelope') and response_data.get('Envelope').get('Body') and \
                                  response_data.get('Envelope').get('Body').get('GetRatingEngineQuoteResponse') and \
                                  response_data.get('Envelope').get('Body').get('GetRatingEngineQuoteResponse').get(
                                      'GetRatingEngineQuoteResult') and \
                                  response_data.get('Envelope').get('Body').get('GetRatingEngineQuoteResponse').get(
                                      'GetRatingEngineQuoteResult').get('QuoteCarrierOptions')
                if carrier_options:
                    response_dicts = response_data.get('Envelope') and response_data.get('Envelope').get('Body') and \
                                     response_data.get('Envelope').get('Body').get(
                                         'GetRatingEngineQuoteResponse') and response_data.get('Envelope').get(
                        'Body').get('GetRatingEngineQuoteResponse').get('GetRatingEngineQuoteResult') and \
                                     response_data.get('Envelope').get('Body').get('GetRatingEngineQuoteResponse').get(
                                         'GetRatingEngineQuoteResult').get('QuoteCarrierOptions') and \
                                     response_data.get('Envelope').get('Body').get('GetRatingEngineQuoteResponse').get(
                                         'GetRatingEngineQuoteResult').get('QuoteCarrierOptions').get('CarrierOption')
                else:
                    raise ValidationError("Response Data : %s" % (response_data))
                if isinstance(response_dicts, dict):
                    response_dicts = [response_dicts]
                self.quote_id = response_data.get('Envelope') and \
                                  response_data.get('Envelope').get('Body') and \
                                  response_data.get('Envelope').get('Body').get('GetRatingEngineQuoteResponse') and \
                                  response_data.get('Envelope').get('Body').get('GetRatingEngineQuoteResponse').get(
                                      'GetRatingEngineQuoteResult') and \
                                  response_data.get('Envelope').get('Body').get('GetRatingEngineQuoteResponse').get(
                                      'GetRatingEngineQuoteResult').get('QuoteId')
                for response_dict in response_dicts:
                    freightquote_shipping_charege_obj.sudo().create(
                        {
                            'freightquote_carrier_id': response_dict.get('CarrierOptionId'),
                            'freightquote_carrier_name': response_dict.get('CarrierName'),
                            'estimated_delivery_time': response_dict.get('Transit'),
                            'freightquote_total_charge': response_dict.get('QuoteAmount'),
                            'picking_id': self and self.id
                        }
                    )
                freightquote_charge_id = freightquote_shipping_charege_obj.search(
                    [('picking_id', '=', self and self.id)], order='freightquote_total_charge', limit=1)
                self.freightquote_shipping_charge_id = freightquote_charge_id and freightquote_charge_id.id
                return {'success': True,
                        'price': freightquote_charge_id and freightquote_charge_id.freightquote_total_charge or 0.0,
                        'error_message': False, 'warning_message': False}
            else:
                return {'success': False, 'price': 0.0, 'error_message': "%s %s" % (response_data, response_data.text),
                        'warning_message': False}
        except Exception as e:
            raise ValidationError(e)
