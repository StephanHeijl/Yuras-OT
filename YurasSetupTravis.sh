# Install Pandoc
sudo cabal update
sleep 3
sudo cabal install pandoc

# Add pandoc dir to path
export PATH=$PATH:~/.cabal/bin

# Add MongoDB directories
mkdir data
mkdir data/db
mkdir data/db/rs0
mkdir data/db/rs1

# Start the replicaset for elasticsearch.
export LC_ALL=C
mongod --port 27017 --dbpath data/db/rs0 --replSet rs0 --fork --syslog
mongod --port 27018 --dbpath data/db/rs1 --replSet rs0 --fork --syslog
sleep 5

# Initiate replicaset
echo ''{ \\\"_id\\\" : \\\"rs0\\\", \\\"members\\\" : [ {\\\"_id\\\" : 0, \\\"host\\\" : \\\"$HOSTNAME:27017\\\", \\\"priority\\\" : 1 }, {\\\"_id\\\" : 1, \\\"host\\\" : \\\"$HOSTNAME:27018\\\", \\\"priority\\\" : 0.5 } ] }'' | xargs -i mongo --eval "rs.initiate({})"

mongo localhost:27017 --eval "database='Yuras1'" setupDatabase.js

# Install Python requirements
find -name "requirements.txt" | xargs -i pip install -r {}