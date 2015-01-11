#sudo apt-get update
sudo apt-get install python python-dev python-pip python-nose mongodb haskell-platform texlive python-scipy python-numpy libssl-dev -y
# install pandoc
sudo cabal update
sudo cabal install pandoc
# add pandoc dir to path
#export PATH=$PATH:~/.cabal/bin 

sudo mkdir /data
sudo mkdir /data/db
sudo chown -R vagrant /data 
mongod > /dev/null &

find -name "requirements.txt" | xargs -i sudo pip install -r {}
