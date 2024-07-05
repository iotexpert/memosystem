#!/usr/bin/env python

import os
from flask import Flask


try:
    import settings_local
except ImportError:
    print("Settings_local.py missing")

from memos import db,create_app
#from memos.extensions import ldap
from flask_simpleldap import LDAP

app = create_app()
app.app_context().push()
db.init_app(app)
    
# LDAP

print(settings_local.SL_LDAP_HOST)
ldap = LDAP()
ldap_user = ldap.get_object_details("arh")
print("--------------")
print(ldap_user)
result = ldap.bind_user("arh", "arh123")
print(result)


# SQL

# Files

# NGINX
# nginx.conf has to exist and be located in /etc/nginx
# server name
# certificates
