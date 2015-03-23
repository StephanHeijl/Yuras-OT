screen -S -d sudo uwsgi -s /tmp/$1/uwsgi.sock --module Yuras.webapp.app --callable app
chmod -R 777 /tmp/$1/uwsgi.sock