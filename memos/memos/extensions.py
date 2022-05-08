import os
from flask_simpleldap import LDAP

if os.getenv('LDAP_HOST') and len(os.getenv('LDAP_HOST')) > 0:
    ldap = LDAP()
else:
    ldap = None