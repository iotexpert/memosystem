import os
from flask_simpleldap import LDAP

if os.getenv('LDAP_HOST') and len(os.getenv('LDAP_HOST')) > 0: #pragma nocover  -- testing ldap is very environment centric.
    ldap = LDAP()
else:
    ldap = None