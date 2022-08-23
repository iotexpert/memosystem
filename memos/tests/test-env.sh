#!/bin/bash
export FLASK_APP=app.py
export FLASK_DEBUG=True

export SQLALCHEMY_DATABASE_URI='sqlite:///test.db'
#export DOCMGR__DATABASE_URI='mysql+pymysql://docmgr:docmgr@linux.local/docmgr'
#export SQLALCHEMY_TRACK_MODIFICATIONS=False

export DOCMGR_SECRET_KEY='5791628bb0b13ce0c676dfde280ba245'

export DOCMGR_EMAIL_SERVER='smtp.google.com'
export DOCMGR_EMAIL_PORT=587
export DOCMGR_EMAIL_USER=''
export DOCMGR_EMAIL_PASS=''

export DOCMGR_ADMIN_USER='admin'
export DOCMGR_ADMIN_PASSWORD='admin'
export DOCMGR_ADMIN_EMAIL='admin@admin.local'
