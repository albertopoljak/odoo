# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Adyen Payment Provider',
    'version': '2.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 340,
    'summary': 'Payment Provider: Adyen Implementation',
    'description': """Adyen Payment Provider""",
    'depends': ['payment'],
    'data': [
        'views/payment_adyen_templates.xml',
        'views/payment_views.xml',
        'views/payment_templates.xml',  # Only load the SDK on pages with a payment form.
        'data/payment_provider_data.xml',  # Depends on views/payment_adyen_templates.xml
    ],
    'application': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_frontend': [
            'payment_adyen/static/src/js/payment_form.js',
            'payment_adyen/static/src/scss/dropin.scss',
        ],
    },
    'license': 'LGPL-3',
}
