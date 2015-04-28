sudo uwsgi -s /tmp/$1/uwsgi.sock --module Yuras.webapp.app --callable app --enable-threads --daemonize /tmp/yuras.log
chmod -R 777 /tmp/$1/uwsgi.sock
