#sudo apt-get update
sudo apt-get install python python-dev python-pip python-nose mongodb -y
sudo mkdir /data
sudo mkdir /data/db
sudo chown -R vagrant /data 
mongod > /dev/null &

find -name "requirements.txt" | xargs -i sudo pip install -r {}
