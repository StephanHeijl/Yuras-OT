# tokumx prerequisites
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key 505A7412
echo "deb [arch=amd64] http://s3.amazonaws.com/tokumx-debs $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/tokumx.list
sudo apt-get update
sudo apt-get install python python-dev python-pip python-nose haskell-platform texlive python-scipy python-numpy libssl-dev tokumx libffi-dev openssl swig libssl-dev -y
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
sudo service tokumx start
sleep 5
mongo localhost:27017 --eval "database='Yuras1'" setupDatabase.js

find -name "requirements.txt" | xargs -i sudo pip install -r {}
