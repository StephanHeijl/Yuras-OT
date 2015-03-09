# MongoDB 3.0.0 prerequisites
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get update
sudo apt-get install python python-dev python-pip python-nose haskell-platform texlive python-scipy python-numpy libssl-dev mongodb-org libffi-dev openssl swig libssl-dev -y
# install pandoc
sudo cabal update
sudo cabal install pandoc

# add pandoc dir to path
export PATH=$PATH:~/.cabal/bin

# Add TokuMX directories
sudo mkdir /data
sudo mkdir /data/db
sudo chown -R vagrant /data 

# Start TokuMX database
sudo service mongodb start
sleep 5
mongo localhost:27017 --eval "database='Yuras1'" setupDatabase.js

find -name "requirements.txt" | xargs -i sudo pip install -r {}
