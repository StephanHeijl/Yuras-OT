sudo uwsgi -s /tmp/uwsgi.sock --module Yuras.webapp.app --callable app  --http :5000
