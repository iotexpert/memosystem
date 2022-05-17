import os
from flask_simpleldap import LDAP

if os.getenv('LDAP_HOST') and len(os.getenv('LDAP_HOST')) > 0:
    ldap = LDAP() #pragma nocover  -- testing ldap is very environment centric.
else:
    ldap = None