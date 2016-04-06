# -*- coding: utf-8 -*-
{
    'name': "auth_ldaps",

    'summary': """
        Extend LDAP by allowing for protocol choice.""",

    'description': """
        This module extends the existing auth_ldap module. It allows use of LDAPS. It also changes the limit, allowing for more than one valid result from the initial query.
    """,

    'author': "Michael Watchorn",
    'website': "http://www.theWatchornGroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'auth_ldap'],

    # always loaded
    'data': [
        'users_ldap_view.xml',
    ],
}
