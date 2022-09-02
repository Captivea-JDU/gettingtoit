from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_freightquote_shipping_provider = fields.Boolean(string="Is Use Freightquote Shipping Provider?",
                                                        help="True when we need to use Freightquote shipping provider",
                                                        default=False, copy=False)
    freightquote_username = fields.Char(string="Freightquote Username", help="Username provided by Freightquote",
                                        required=True)
    freightquote_password = fields.Char(string="Freightquote Password", help="Password provided by Freightquote",
                                        required=True)
    freightquote_credential_type = fields.Selection([('Default', 'Default'),
                                                     ('Application', 'Application')], default="Default",
                                                    string="Credential Type",
                                                    help="Type of credentials you are providing Freightquote , Note: Application credential is not supported for B2B customers")
    freightquote_customer_id = fields.Char(string="Freightquote CustomerId",
                                           help="Identifier for customer provided by Freightquote")
    freightquote_api_url = fields.Char(string="Freightquote API url")
