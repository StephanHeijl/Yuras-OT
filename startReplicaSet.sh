export LC_ALL=C
sudo -H -u mongodb mongod --port 27017 --dbpath /data/db/rs0 --replSet rs0 --fork --syslog
