#!/usr/bin/env python3

"""
    Smithproxy- transparent proxy with SSL inspection capabilities.
    Copyright (c) 2014, Ales Stibal <astib@mag0.net>, All rights reserved.

    Smithproxy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Smithproxy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Smithproxy.  If not, see <http://www.gnu.org/licenses/>.


    Linking Smithproxy statically or dynamically with other modules is
    making a combined work based on Smithproxy. Thus, the terms and
    conditions of the GNU General Public License cover the whole combination.

    In addition, as a special exception, the copyright holders of Smithproxy
    give you permission to combine Smithproxy with free software programs
    or libraries that are released under the GNU LGPL and with code
    included in the standard release of OpenSSL under the OpenSSL's license
    (or modified versions of such code, with unchanged license).
    You may copy and distribute such a system following the terms
    of the GNU GPL for Smithproxy and the licenses of the other code
    concerned, provided that you include the source code of that other code
    when and as the GNU GPL requires distribution of source code.

    Note that people who make modified versions of Smithproxy are not
    obligated to grant this special exception for their modified versions;
    it is their choice whether to do so. The GNU General Public License
    gives permission to release a modified version without this exception;
    this exception also makes it possible to release a modified version
    which carries forward this exception.
    """

import logging
import string
import sys

import ldap

# Some favorite LDAP search queries. 
# $cnid -- attribute which represents logon name (openldap: uid, windows AD: sAMAccountName)
# $user -- enter username you would like to search.
LDAP_SEARCH_USER = '(&(objectClass=person)(${cnid}=${user}))'

# Distinguishing names: used in CryptoCache as the recognition entry,
# which must be unique.
#

LDAP_MS_DSTN = "sAMAccountName"
LDAP_UX_DSTN = "uid"

flog = logging.getLogger('bend')


# Some printinng useful for debugging, nothing more.
def pprint_result(r):

    for cn, attributes in r:

        if cn is None:
            continue

        print("RESULT: %s" % cn)
        for k in attributes.keys():
            print("\tAttribute \'%s\': %s" % (k, str(attributes[k])))


# Used profile entries:
# crypto_atts: attributes which are known to be encrypted
# crypto_dstn: key used to distinguish between particular result queries. Usually kind of username attribute.
#
# network_timeout: how long we should wait until some response arrives
# bind_dn:  bind using some specific account
# bind_pw: bind_dn password
# bind_uri: URI for the connection


class LdapCon(object):

    # allow to create LdapCon without cryptocache
    def __init__(self):
        self._ldapcon = None
        self.network_timeout = 2

        self.flushProfile()

    @staticmethod
    def empty_profile():

        profile = {"network_timeout": 2, "bind_dn": 'dc=', "bind_pw": '', "bind_uri": '', "cnid": 'uid'}

        return profile

    def flushProfile(self):
        self.profile = LdapCon.empty_profile()

    def updateProfile(self, u):
        self.profile.update(u)

    # initialize internal ldap connection
    def init(self):
        self._ldapcon = None

        flog.debug("ldapcon.init:")

        if self.profile["bind_uri"] == '' and "ip" in self.profile.keys():
            self.profile["bind_uri"] = "ldap://" + self.profile["ip"]
            flog.debug("ldapcon.init: specifying uri using ip key")

            if "port" in self.profile:
                if self.profile["port"] != '' or not self.profile["port"]:
                    self.profile["bind_uri"] += ":" + str(self.profile["port"])

        flog.debug("ldapcon.init: uri: " + self.profile["bind_uri"])

        self._ldapcon = ldap.initialize(self.profile["bind_uri"])

        try:
            self.network_timeout = self.profile["network_timeout"]
        except KeyError:
            pass

        self._ldapcon.set_option(ldap.OPT_NETWORK_TIMEOUT, self.network_timeout)

        flog.debug("ldapcon.init: ok")

    def bind(self, custom_u=None, custom_p=None):

        flog.debug("ldapcon.bind:")
        u = self.profile["bind_dn"]
        p = self.profile["bind_pw"]

        if custom_u:
            u = custom_u
        if custom_p:
            p = custom_p

        # flog.debug("ldapcon.bind: about to bind with user '%s' and password '%s'" % (u,p)) # :->
        flog.debug("ldapcon.bind: about to bind with user '%s' " % (u,))

        r = ''
        try:
            r = self._ldapcon.bind(u, p)
        except ldap.LDAPError as e:
            flog.error("ldap.bind failure: %s" % (str(e),))
            return r

        flog.debug("ldapcon.bind: bind result: '%s'" % (str(r),))

        rr = self._ldapcon.whoami_s()
        flog.debug("ldapcon.bind: whoami test result '" + str(rr) + "'")

        if rr == '':
            flog.info(self.profile["bind_uri"] + ": invalid credentials check for user '%s'" % (str(u),))
            r = ''

        flog.debug("ldapcon.bind: result: '%s'" % (str(r),))
        return r

    def raw_query(self, base, query, xfilter=None, scope=ldap.SCOPE_SUBTREE):

        r = self._ldapcon.search_s(base, scope, query, xfilter)
        nr = []

        for cn, atts in r:
            dstn = None

            if not cn:
                # We don't want to return LDAP Referrals. Skip it.
                continue

            nr.append((cn, atts))

        return nr


# Used profile entries:
#   user: user query string _template_ with $user variable (can be for example '*', or username)
#   base: LDAP base DN
#  scope: LDAP scope constant (see LDAP module docs)
# filter: list of attributes we are interested in

class LdapSearch(LdapCon):

    def __init__(self):
        LdapCon.__init__(self)
        self.profile = LdapSearch.empty_profile()

    @staticmethod
    def empty_profile():

        d = LdapCon.empty_profile()

        e = {"user": LDAP_SEARCH_USER,
             "base_dn": "",
             "filter": [],
             "scope": ldap.SCOPE_SUBTREE,
             "recursive_member_attr": "uniqueMember"
             }

        d.update(e)

        return d

    def search_user_dn(self, username, query_dict=None):

        r = None
        flog.debug("ldapsearch.search_user_dn: ")

        try:
            flog.debug("ldapsearch.search_user_dn: using template: " + self.profile["user"])
            template = string.Template(self.profile["user"])

            q = template.substitute(cnid=self.profile["cnid"], user=username)
            flog.debug("ldapsearch.search_user_dn: query: " + q)

            r = self.raw_query(self.profile["base_dn"], q,
                               self.profile["filter"],
                               self.profile["scope"])

            flog.debug("ldapsearch.search_user_dn: query result: " + str(r))

        except ldap.error as e:
            flog.debug("ldapsearch.search_user_dn: query exception caught: " + str(e))

        except KeyError as e:
            flog.debug("ldapsearch.search_user_dn: query exception caught: " + str(e))

        flog.debug("ldapsearch.search_user_dn: returning %d objects" % (len(r),))
        return r

    def authenticate_user(self, username, password, lookup_only=False):

        flog.debug("ldapsearch.authenticate_user: FIND")
        r = self.search_user_dn(username)

        if r:
            flog.debug("ldapsearch.authenticate_user: BIND")

            self.init()
            res = self.bind(r[0][0], password)

            if res == '' and not lookup_only:
                flog.debug("ldapsearch.authenticate_user: FAILED")
                return None, None

            flog.debug("ldapsearch.authenticate_user: GROUPS")
            groups = self.groups_user_dn(r[0][0])
            flog.debug("ldapsearch.authenticate_user: %d group(s) found" % (len(groups),))

            return r[0][0], groups

        flog.debug("ldapsearch.authenticate_user: NOT FOUND")
        return None, None

    def groups_user_dn(self, user_dn):
        ret = []

        self.init()
        res = self.raw_query(self.profile["base_dn"], "%s=%s" % (self.profile["recursive_member_attr"], user_dn))
        if res:
            for r in res:
                ret.append(r[0])

        return ret

    # test cases, examples


# Test:
# ldapsearch -h 192.168.254.1 -x -b dc=nodomain -D cn=admin,dc=nodomain -w smithproxy 'uid=astib'
# ldapsearch -h 192.168.254.1 -x -b dc=nodomain -D cn=admin,dc=nodomain -w smithproxy
#       'uniqueMember=cn=Ales Stibal,cn=users, dc=nodomain

def test_LdapSearch(ip):
    myldap = LdapSearch()
    myldap.profile["bind_uri"] += ip
    myldap.profile["bind_dn"] = 'cn=admin,dc=nodomain'
    myldap.profile["bind_pw"] = 'smithproxy'
    myldap.profile["base_dn"] = 'dc=nodomain'
    myldap.profile["filter"] = ['uid', 'info', 'mobile', 'email', 'memberOf']

    try:
        myldap.init()
        myldap.bind()
        dn = myldap.search_user_dn('astib')
        if dn:
            print("DN found: " + dn[0][0])

        myldap.init()
        r = myldap.authenticate_user('astib', 'smithproxy')
        if r:
            rr = myldap.groups_user_dn(r)
            print(rr)

    except ldap.LDAPError as e:
        print("LDAP ERROR: %s" % str(e))

    else:
        print("OK: All LDAP operations returned sucessfully.")

    # print out whole profile
    # pprint.pprint(myldap.profile)


if __name__ == "__main__":
    test_LdapSearch(sys.argv[1])
