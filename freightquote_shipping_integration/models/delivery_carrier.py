import logging
import time
import requests
import xml.etree.ElementTree as etree
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError, UserError
from odoo.addons.freightquote_shipping_integration.models.freightquote_response import Response

_logger = logging.getLogger("Freightquote")


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("freightquote", "Freightquote")],
                                     ondelete={'freightquote': 'set default'})
    package_id = fields.Many2one('stock.package.type', string="package", help="please select package type")

    quote_type = fields.Selection([('B2B', 'B2B'),
                                   ('Freightview', 'Freight view')], string="Quote Type")
    service_type = fields.Selection([('LTL', 'LTL'),
                                     ('Truckload', 'Truckload'),
                                     ('All', 'All')], string="Service Type")

    def freightquote_rate_shipment(self, orders):
        "This Method Is Used For Get Rate"


        freightquote_shipping_charege_obj = self.env['freightquote.shipping.charge']
        shipper_address = orders.warehouse_id and orders.warehouse_id.partner_id
        recipient_address = orders.partner_shipping_id

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
        etree.SubElement(request_node, 'QuoteType').text = self.quote_type or ""
        etree.SubElement(request_node, 'ServiceType').text = self.service_type or ""

        # Quote Shipment Node
        quote_shipment = etree.SubElement(request_node, "QuoteShipment")
        etree.SubElement(quote_shipment, 'PickupDate').text = str(orders.date_order).split()[0]

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
        for order in orders.freightquote_package_ids:
            counter = counter + 1
            product_node = etree.SubElement(shipment_products, "Product")
            etree.SubElement(product_node, 'Class').text = order.freight_class
            etree.SubElement(product_node, 'Weight').text = order.weight
            etree.SubElement(product_node, 'Length').text = order.length
            etree.SubElement(product_node, 'Width').text = order.width
            etree.SubElement(product_node, 'Height').text = order.height
            etree.SubElement(product_node,
                             'ProductDescription').text = order.product_description.name
            etree.SubElement(product_node, 'PackageType').text = order.package_type
            etree.SubElement(product_node, 'CommodityType').text = order.commodity_type
            etree.SubElement(product_node, 'ContentType').text = order.content_type
            etree.SubElement(product_node,
                             'IsHazardousMaterial').text = "false"  # (str(order.is_hazardous_material)).lower()
            etree.SubElement(product_node, 'PieceCount').text = order.piece_count
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
            _logger.info(etree.tostring(master_node))
            response_data = requests.request(method="POST", url=url, headers=headers,
                                             data=etree.tostring(master_node))
            _logger.info(response_data)
            if response_data.status_code in [200, 201]:
                api = Response(response_data)
                response_data = api.dict()
                existing_records = freightquote_shipping_charege_obj.search(
                    [('sale_order_id', '=', orders and orders.id)])
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
                orders.quote_id = response_data.get('Envelope') and \
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
                            'sale_order_id': orders and orders.id
                        }
                    )
                freightquote_charge_id = freightquote_shipping_charege_obj.search(
                    [('sale_order_id', '=', orders and orders.id)], order='freightquote_total_charge', limit=1)
                orders.freightquote_shipping_charge_id = freightquote_charge_id and freightquote_charge_id.id
                return {'success': True,
                        'price': freightquote_charge_id and freightquote_charge_id.freightquote_total_charge or 0.0,
                        'error_message': False, 'warning_message': False}
            else:
                return {'success': False, 'price': 0.0, 'error_message': "%s %s" % (response_data, response_data.text),
                        'warning_message': False}
        except Exception as e:
            raise ValidationError(e)



    def freightquote_send_shipping(self, pickings):
        """This Method Is Used For Send The Shipping Request To Shipper"""
        response = []
        for picking in pickings:
            recipient_address = picking.partner_id
            shipper_address = picking.picking_type_id.warehouse_id.partner_id

            master_node = etree.Element("soap:Envelope")
            master_node.attrib['xmlns:soap'] = "http://schemas.xmlsoap.org/soap/envelope/"
            master_node.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
            master_node.attrib['xmlns:xsd'] = "http://www.w3.org/2001/XMLSchema"

            body_node = etree.SubElement(master_node, "soap:Body")
            request_shipment_pickup = etree.SubElement(body_node, "RequestShipmentPickup")
            request_shipment_pickup.attrib['xmlns'] = "http://tempuri.org/"

            request_node = etree.SubElement(request_shipment_pickup, "request")
            etree.SubElement(request_node,
                             'CustomerId').text = self.company_id and self.company_id.\
                freightquote_customer_id or ""
            if picking.quote_id:
                etree.SubElement(request_node, 'QuoteId').text = pickings and picking.quote_id or ""
                etree.SubElement(request_node,
                                 'OptionId').text = pickings and pickings.freightquote_shipping_charge_id.freightquote_carrier_id or ""
            else:
                etree.SubElement(request_node, 'QuoteId').text = pickings and pickings.sale_id.quote_id or ""
                etree.SubElement(request_node,
                                 'OptionId').text = pickings and pickings.sale_id and pickings.sale_id.freightquote_shipping_charge_id.freightquote_carrier_id or ""

            quote_shipment = etree.SubElement(request_node, "QuoteShipment")
            etree.SubElement(quote_shipment, 'PickupDate').text = str(picking.scheduled_date).split()[0]

            shipment_locations = etree.SubElement(quote_shipment, "ShipmentLocations")
            location = etree.SubElement(shipment_locations, "Location")
            etree.SubElement(location, 'LocationType').text = "Origin"
            etree.SubElement(location, 'ContactName').text = shipper_address.name or ""
            etree.SubElement(location, 'ContactPhone').text = shipper_address.phone or ""
            etree.SubElement(location, 'ContactEmail').text = shipper_address.email or ""

            location_address = etree.SubElement(location, "LocationAddress")
            etree.SubElement(location_address, 'AddressName').text = shipper_address.name or ""
            etree.SubElement(location_address, 'StreetAddress').text = shipper_address.street or ""
            etree.SubElement(location_address, 'City').text = shipper_address.city or ""
            etree.SubElement(location_address,
                             'StateCode').text = shipper_address.state_id and shipper_address.state_id.code or ""
            etree.SubElement(location_address, 'PostalCode').text = shipper_address.zip or ""
            etree.SubElement(location_address,
                             'PostalCode').text = shipper_address.country_id and shipper_address.country_id.code or ""

            # shipment_locations = etree.SubElement(quote_shipment, "ShipmentLocations")
            location = etree.SubElement(shipment_locations, "Location")
            etree.SubElement(location, 'LocationType').text = "Destination"
            etree.SubElement(location, 'ContactName').text = recipient_address.name or ""
            etree.SubElement(location, 'ContactPhone').text = recipient_address.phone or ""
            etree.SubElement(location, 'ContactEmail').text = recipient_address.email or ""

            location_address = etree.SubElement(location, "LocationAddress")
            etree.SubElement(location_address, 'AddressName').text = recipient_address.name or ""
            etree.SubElement(location_address, 'StreetAddress').text = recipient_address.street or ""
            etree.SubElement(location_address, 'City').text = recipient_address.city or ""
            etree.SubElement(location_address,
                             'StateCode').text = recipient_address.state_id and shipper_address.state_id.code or ""
            etree.SubElement(location_address, 'PostalCode').text = recipient_address.zip or ""
            etree.SubElement(location_address,
                             'PostalCode').text = recipient_address.country_id and recipient_address.country_id.code or ""

            shipment_products = etree.SubElement(quote_shipment, "ShipmentProducts")
            counter = 0
            # if pickings.freightquote_package_ids:
            for product_id in pickings.freightquote_package_ids:
                counter = counter + 1
                product_node = etree.SubElement(shipment_products, "Product")
                etree.SubElement(product_node, 'Class').text = product_id.freight_class
                etree.SubElement(product_node, 'Weight').text = product_id.weight
                etree.SubElement(product_node, 'Length').text = product_id.length
                etree.SubElement(product_node, 'Width').text = product_id.width
                etree.SubElement(product_node, 'Height').text = product_id.height
                etree.SubElement(product_node,
                                 'ProductDescription').text = product_id.product_description.name
                etree.SubElement(product_node, 'PackageType').text = product_id.package_type
                etree.SubElement(product_node, 'CommodityType').text = product_id.commodity_type
                etree.SubElement(product_node, 'ContentType').text = product_id.content_type
                etree.SubElement(product_node,
                                 'IsHazardousMaterial').text = "false"  # (str(order.is_hazardous_material)).lower()
                etree.SubElement(product_node, 'PieceCount').text = product_id.piece_count
                etree.SubElement(product_node, 'ItemNumber').text = str(counter)

            user_node = etree.SubElement(request_shipment_pickup, "user")
            etree.SubElement(user_node, 'Name').text = self.company_id.freightquote_username or ""
            etree.SubElement(user_node, 'Password').text = self.company_id.freightquote_password or ""
            etree.SubElement(user_node, 'CredentialType').text = self.company_id.freightquote_credential_type or ""
            _logger.info("====>Request Data Of Shipment Request%s" % etree.tostring(master_node))
            try:
                headers = {
                    'SOAPAction': 'http://tempuri.org/RequestShipmentPickup',
                    'Content-Type': 'text/xml; charset=utf-8'
                }
                url = self.company_id and self.company_id.freightquote_api_url

                response_data = requests.request("POST", url=url, headers=headers,
                                                 data=etree.tostring(master_node))
                _logger.info("=====>XML Response Of Shipping Request%s" % response_data.content)
                time.sleep(15)
                if response_data.status_code in [200, 201]:
                    api = Response(response_data)
                    response_data = api.dict()
                    _logger.info("=====>Json Response Of Shipping Request%s" % response_data)
                    check_error = response_data.get('Envelope') and response_data.get('Envelope').get('Body') and \
                                  response_data.get('Envelope').get('Body').get('RequestShipmentPickupResponse') and \
                                  response_data.get('Envelope').get('Body').get('RequestShipmentPickupResponse').get(
                                      'RequestShipmentPickupResult') and \
                                  response_data.get('Envelope').get('Body').get('RequestShipmentPickupResponse').get(
                                      'RequestShipmentPickupResult').get('ValidationErrors') and \
                                  response_data.get('Envelope').get('Body').get('RequestShipmentPickupResponse').get(
                                      'RequestShipmentPickupResult').get('ValidationErrors').get('B2BError')
                    error_ls = []
                    if check_error:
                        if isinstance(check_error, dict):
                            check_error = [check_error]
                        for error in check_error:
                            error_ls.append(error.get('ErrorMessage'))
                        raise ValidationError(','.join(error_ls))

                    bill_of_loading_url = response_data.get('Envelope') and response_data.get('Envelope').get('Body') and \
                                          response_data.get('Envelope').get('Body').get('RequestShipmentPickupResponse') and \
                                          response_data.get('Envelope').get('Body').get('RequestShipmentPickupResponse').get('RequestShipmentPickupResult') and \
                                          response_data.get('Envelope').get('Body').get('RequestShipmentPickupResponse').get('RequestShipmentPickupResult').get('BillOfLadingURL')
                    picking.freightquote_bol_url = bill_of_loading_url
                    headers = {'Content-Type': "application/x-www-form-urlencoded", 'Accept': "application/pdf"}
                    pdf_response = requests.get(url=bill_of_loading_url)
                    picking.carrier_tracking_ref = response_data.get('Envelope') and response_data.get('Envelope').get('Body') and\
                                                response_data.get('Envelope').get('Body').get('RequestShipmentPickupResponse') and\
                                                response_data.get('Envelope').get('Body').get('RequestShipmentPickupResponse').get('RequestShipmentPickupResult') and\
                                                response_data.get('Envelope').get('Body').get('RequestShipmentPickupResponse').get('RequestShipmentPickupResult').get('QuoteId')
                    logmessage = ("<b>Tracking Numbers:</b> %s") % (picking.carrier_tracking_ref)
                    picking.message_post(body=logmessage,
                                         attachments=[("%s.pdf" % (pickings.id), pdf_response.content)])
                    shipping_data = {'exact_price': 0.0, 'tracking_number': picking.carrier_tracking_ref}
                    response += [shipping_data]
                    return response
                else:
                    raise ValidationError(response_data.content)

            except Exception as e:
                raise ValidationError(e)

    def freightquote_cancel_shipment(self, picking):
        """This Method Used For Cancel The Shipment"""
        master_node = etree.Element("soap:Envelope")
        master_node.attrib['xmlns:soap'] = "http://schemas.xmlsoap.org/soap/envelope/"
        master_node.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        master_node.attrib['xmlns:xsd'] = "http://www.w3.org/2001/XMLSchema"

        body_node = etree.SubElement(master_node, "soap:Body")
        request_shipment_cancellation = etree.SubElement(body_node, "RequestShipmentCancellation")
        request_shipment_cancellation.attrib['xmlns'] = "http://tempuri.org/"
        request_node = etree.SubElement(request_shipment_cancellation, "request")
        etree.SubElement(request_node, 'QuoteId').text = picking.carrier_tracking_ref or ""

        user_node = etree.SubElement(request_shipment_cancellation, "user")
        etree.SubElement(user_node, 'Name').text = self.company_id.freightquote_username or ""
        etree.SubElement(user_node, 'Password').text = self.company_id.freightquote_password or ""
        etree.SubElement(user_node, 'CredentialType').text = self.company_id.freightquote_credential_type or ""
        _logger.info("====>Request Data Of Cancel Shipment Request%s" % etree.tostring(master_node))

        try:
            headers = {
                'SOAPAction': 'http://tempuri.org/RequestShipmentCancellation',
                'Content-Type': 'text/xml; charset=utf-8'
            }
            url = self.company_id and self.company_id.freightquote_api_url

            response_data = requests.request("POST", url=url, headers=headers,
                                             data=etree.tostring(master_node))
            _logger.info("=====>XML Response Of Cancel Shipping Request%s" % response_data.content)
            if response_data.status_code in [200, 201]:
                _logger.info("Order Cancel Successfully")
                return True
            else:
                raise ValidationError(response_data.content)
        except Exception as e:
            raise ValidationError(e)

    def freightquote_get_tracking_link(self, picking):
        """This Method Is Used For Tracking Order"""
        return "https://www.freightquote.com/track-shipment/"
