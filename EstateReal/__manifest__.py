{
    'name': 'Real Estate',
    'version': '1.0',
    'author': 'Ann.akkm',
    'category': 'Real Estate/Brokerage',
                'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/menu.xml',
        'views/views_menu.xml',
        'views/property_types.xml',
        'views/property_tags.xml',
        'views/property_offers.xml',
        'views/view_users.xml',
        'report/property_offer_report_template.xml',
        'report/property_offer_report_views.xml',
        'report/property_offer_report_inherit_template.xml',
    ],
    'demo': [
        'demo/real_estate_demo_data.xml',
    ],
    'application': True
}

#  -d Odoo_DB -u EstateReal,Account_estate
