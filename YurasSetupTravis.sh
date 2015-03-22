# Add pandoc dir to path
export PATH=$PATH:~/.cabal/bin

# Add MongoDB directories
mkdir data
mkdir data/db
mkdir data/db/rs0
mkdir data/db/rs1

# Stop MongoDB database
sudo service mongodb stop
sudo service mongod stop

# Start the replicaset for elasticsearch.
export LC_ALL=C
mongod --port 27017 --dbpath data/db/rs0 --replSet rs0 --fork --syslog
mongod --port 27018 --dbpath data/db/rs1 --replSet rs0 --fork --syslog
sleep 5

# Initiate replicaset
echo ''{ \\\"_id\\\" : \\\"rs0\\\", \\\"members\\\" : [ {\\\"_id\\\" : 0, \\\"host\\\" : \\\"$HOSTNAME:27017\\\", \\\"priority\\\" : 1 }, {\\\"_id\\\" : 1, \\\"host\\\" : \\\"$HOSTNAME:27018\\\", \\\"priority\\\" : 0.5 } ] }'' | xargs -i mongo --eval "rs.initiate({})"

mongo localhost:27017 --eval "database='Yuras1'" setupDatabase.js

# Install elasticsearch River plugin for MongoDB and Head Frontend
sudo /usr/share/elasticsearch/bin/plugin --install com.github.richardwilly98.elasticsearch/elasticsearch-river-mongodb/2.0.6

service elasticsearch restart

# Configure index on document contents
curl -XPUT '127.0.0.1:9200/_river/mongodb/_meta' '{"type":"mongodb","mongodb":{"db":"Yuras1","collection":"documents"},"index":{"name":"document_contents","type":"document"}}'

# Install Python requirements
find -name "requirements.txt" | xargs -i sudo pip install -r {}
