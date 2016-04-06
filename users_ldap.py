##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

import ldap
import logging
from ldap.filter import filter_format

import openerp.exceptions
from openerp import tools
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
_logger = logging.getLogger(__name__)

class CompanyLDAP(osv.osv):
    _name = 'res.company.ldap'

    def get_ldap_dicts(self, cr, ids=None):
        """ 
        Retrieve res_company_ldap resources from the database in dictionary
        format.
        :param list ids: Valid ids of model res_company_ldap. If not \
        specified, process all resources (unlike other ORM methods).
        :return: ldap configurations
        :rtype: list of dictionaries
        """

        if ids:
            id_clause = 'AND id IN (%s)'
            args = [tuple(ids)]
        else:
            id_clause = ''
            args = []
        cr.execute("""
            SELECT id, company,ldap_protocol, ldap_server, ldap_server_port, ldap_binddn,
                   ldap_password, ldap_filter, ldap_base, "user", create_user,
                   ldap_tls
            FROM res_company_ldap
            WHERE ldap_server != '' """ + id_clause + """ ORDER BY sequence
        """, args)
        return cr.dictfetchall()

    def connect(self, conf):
        """ 
        Connect to an LDAP server specified by an ldap
        configuration dictionary.
        :param dict conf: LDAP configuration
        :return: an LDAP object
        """

        uri = '%s://%s:%d' % (conf['ldap_protocol'],conf['ldap_server'],
                                conf['ldap_server_port'])

        connection = ldap.initialize(uri)
        if conf['ldap_tls']:
            connection.start_tls_s()
        return connection

    def authenticate(self, conf, login, password):
        """
        Authenticate a user against the specified LDAP server.
        In order to prevent an unintended 'unauthenticated authentication',
        which is an anonymous bind with a valid dn and a blank password,
        check for empty passwords explicitely (:rfc:`4513#section-6.3.1`)
        
        :param dict conf: LDAP configuration
        :param login: username
        :param password: Password for the LDAP user
        :return: LDAP entry of authenticated user or False
        :rtype: dictionary of attributes
        """

        if not password:
            return False

        entry = False
        filter = filter_format(conf['ldap_filter'], (login,))
        try:
            results = self.query(conf, filter)

            # Get rid of (None, attrs) for searchResultReference replies
            results = [i for i in results if i[0]]
            if results and len(results) >= 1:
                dn = results[0][0]
                conn = self.connect(conf)
                conn.simple_bind_s(dn, password)
                conn.unbind()
                entry = results[0]
        except ldap.INVALID_CREDENTIALS:
            return False
        except ldap.LDAPError, e:
            _logger.error('An LDAP exception occurred: %s', e)
        return entry

    _columns = {
        'ldap_protocol':fields.selection([('ldap','ldap'),('ldaps','ldaps')], string='Protocol', help=("Select regular or secure ldap (ldaps)")),
    }

    _defaults = {
        'ldap_protocol': 'ldaps', 
        'ldap_server_port': 636,
    }

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'ldaps': fields.one2many(
            'res.company.ldap', 'company', 'LDAP Parameters', copy=True, groups="base.group_system"),
    }

