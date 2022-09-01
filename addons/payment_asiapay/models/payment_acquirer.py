# Part of Odoo. See LICENSE file for full copyright and licensing details.

from hashlib import new as hashnew

from odoo import api, fields, models

from odoo.addons.payment_asiapay import const


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    def _domain_asiapay_currency_id(self):
        currency_xmlids = [f'base.{key}' for key in const.CURRENCY_MAPPING]
        return [('id', 'in', [self.env.ref(xmlid).id for xmlid in currency_xmlids])]

    provider = fields.Selection(
        selection_add=[('asiapay', "AsiaPay")], ondelete={'asiapay': 'set default'}
    )
    asiapay_merchant_id = fields.Char(
        string="AsiaPay Merchant ID",
        help="The Merchant ID solely used to identify your AsiaPay account.",
        required_if_provider='asiapay',
    )
    asiapay_currency_id = fields.Many2one(
        string="AsiaPay Currency",
        help="The currency associated to your AsiaPay account.",
        comodel_name='res.currency',
        domain=_domain_asiapay_currency_id,
        required_if_provider='asiapay',
    )
    asiapay_secure_hash_secret = fields.Char(
        string="AsiaPay Secure Hash Secret",
        required_if_provider='asiapay',
        groups='base.group_system',
    )
    asiapay_secure_hash_function = fields.Selection(
        string="AsiaPay Secure Hash Function",
        help="The secure hash function associated to your AsiaPay account.",
        selection=[('sha1', "SHA1"), ('sha256', "SHA256"), ('sha512', 'SHA512')],
        default='sha1',
        required_if_provider='asiapay',
    )

    # === BUSINESS METHODS ===#

    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        """ Override of `payment` to filter out AsiaPay acquirers for unsupported currencies. """
        acquirers = super()._get_compatible_acquirers(*args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency:
            acquirers = acquirers.filtered(
                lambda a: a.provider != 'asiapay' or currency == a.asiapay_currency_id
            )

        return acquirers

    def _asiapay_get_api_url(self):
        """ Return the URL of the API corresponding to the acquirer's state.

        :return: The API URL.
        :rtype: str
        """
        self.ensure_one()

        if self.state == 'enabled':
            return 'https://www.paydollar.com/b2c2/eng/payment/payForm.jsp'
        else:  # 'test'
            return 'https://test.paydollar.com/b2cDemo/eng/payment/payForm.jsp'

    def _asiapay_calculate_signature(self, data, incoming=True):
        """ Compute the signature for the provided data according to the AsiaPay documentation.

        :param dict data: The data to sign.
        :param bool incoming: Whether the signature must be generated for an incoming (AsiaPay to
                              Odoo) or outgoing (Odoo to AsiaPay) communication.
        :return: The calculated signature.
        :rtype: str
        """
        signature_keys = const.SIGNATURE_KEYS['incoming' if incoming else 'outgoing']
        data_to_sign = [str(data[k]) for k in signature_keys] + [self.asiapay_secure_hash_secret]
        signing_string = '|'.join(data_to_sign)
        shasign = hashnew(self.asiapay_secure_hash_function)
        shasign.update(signing_string.encode())
        return shasign.hexdigest()

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'asiapay':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_asiapay.payment_method_asiapay').id

    def _neutralize(self):
        super()._neutralize()
        self._neutralize_fields('asiapay', [
            'asiapay_merchant_id',
            'asiapay_currency_id',
            'asiapay_secure_hash_secret',
            'asiapay_secure_hash_function',
        ])
