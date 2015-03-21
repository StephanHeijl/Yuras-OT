# MongoDB 3.0.0 prerequisites
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get update
sudo apt-get install python python-dev python-pip python-nose haskell-platform texlive python-scipy python-numpy libssl-dev mongodb-org libffi-dev openssl openjdk-7-jre swig libssl-dev -y

# Install Pandoc
sudo cabal update
sleep 3
sudo cabal install pandoc

# Add pandoc dir to path
export PATH=$PATH:~/.cabal/bin

# Add MongoDB directories
sudo mkdir /data
sudo mkdir /data/db
mkdir /data/db/rs0
mkdir /data/db/rs1
sudo chown -R mongodb /data

# Stop MongoDB database
sudo service mongodb stop
sudo service mongod stop
# Set MongoDB to manual startup
echo manual | sudo tee /etc/init/mongod.override
echo manual | sudo tee /etc/init/mongodb.override

# Start the replicaset for elasticsearch.
sudo bash startReplicaSet.sh
sleep 5

# Initiate replicaset
echo ''{ \\\"_id\\\" : \\\"rs0\\\", \\\"members\\\" : [ {\\\"_id\\\" : 0, \\\"host\\\" : \\\"$HOSTNAME:27017\\\", \\\"priority\\\" : 1 }, {\\\"_id\\\" : 1, \\\"host\\\" : \\\"$HOSTNAME:27018\\\", \\\"priority\\\" : 0.5 } ] }'' | xargs -i mongo --eval "rs.initiate({})"

mongo localhost:27017 --eval "database='Yuras1'" setupDatabase.js

# Install ElasticSearch
wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.4.2.deb
sudo dpkg -i elasticsearch-1.4.2.deb
rm https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.4.2.deb
sleep 5

# Install elasticsearch River plugin for MongoDB and Head Frontend
sudo /usr/share/elasticsearch/bin/plugin --install com.github.richardwilly98.elasticsearch/elasticsearch-river-mongodb/2.0.6
sudo /usr/share/elasticsearch/bin/plugin --install mobz/elasticsearch-head

sudo service elasticsearch restart

sleep 10

# Configure index on document contents
curl -XPUT '127.0.0.1:9200/_river/mongodb/_meta' '{"type":"mongodb","mongodb":{"db":"Yuras1","collection":"documents"},"index":{"name":"document_contents","type":"document"}}'

# Install Python requirements

find -name "requirements.txt" | xargs -i sudo pip install -r {}
