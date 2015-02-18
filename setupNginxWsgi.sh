mkdir /tmp/$1/
rm /tmp/$1/uwsgi.sock
chmod 777 /tmp/$1/uwsgi.sock
sudo ln -s yuras.nginx.conf /etc/nginx/sites-enabled/yuras.$1.nginx.conf
sudo service nginx restart