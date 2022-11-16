#! /usr/bin/env sh
set -e

if [ -f /app/memos/static/config/resolv.conf ]; then
    cp /app/memos/static/config/resolv.conf /etc/
fi

if [ -f /app/memos/static/config/nginx.conf ]; then
    cp /app/memos/static/config/nginx.conf /etc/nginx
fi

if [ -f /app/memos/static/config/settings_local.py ]; then
    cp /app/memos/static/config/settings_local.py /app
fi
