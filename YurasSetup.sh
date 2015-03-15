# MongoDB 3.0.0 prerequisites
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get update
sudo apt-get install python python-dev python-pip python-nose haskell-platform texlive python-scipy python-numpy libssl-dev mongodb-org libffi-dev openssl openjdk-7-jre swig libssl-dev -y
# install pandoc
sudo cabal update
sudo cabal install pandoc

# add pandoc dir to path
export PATH=$PATH:~/.cabal/bin

# Add TokuMX directories
sudo mkdir /data
sudo mkdir /data/db
sudo chown -R vagrant /data 

# Start MongoDB database
sudo service mongodb stop
sudo bash startReplicaSet.sh
sleep 5
mongo localhost:27017 --eval "database='Yuras1'" setupDatabase.js

# Install ElasticSearch
wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.4.2.deb
sudo dpkg -i elasticsearch-1.4.2.deb

sudo /usr/share/elasticsearch/bin/plugin --install com.github.richardwilly98.elasticsearch/elasticsearch-river-mongodb/2.0.6
sudo /usr/share/elasticsearch/bin/plugin --install mobz/elasticsearch-head

# Configure index on document_contents
curl -XPUT '127.0.0.1:9200/_river/mongodb/_meta' '{"type":"mongodb","mongodb":{"db":"Yuras1","collection":"documents"},"index":{"name":"document_contents","type":"document"}}'

find -name "requirements.txt" | xargs -i sudo pip install -r {}
