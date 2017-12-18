#!/usr/bin/env bash

INSTALLATION_DIRECTORY=/home/vagrant/mayan-edms/
DB_NAME=mayan_edms
DB_PASSWORD=test123

cat << EOF | sudo tee -a /etc/motd.tail
**********************************sudo apt

Mayan EDMS Vagrant Development Box

**********************************
EOF

# Update sources
echo -e "\n -> Running apt-get update & upgrade \n"
sudo apt-get -qq update
sudo apt-get -y upgrade

echo -e "\n -> Installing core binaries \n"
sudo apt-get -y install git-core python-virtualenv gcc python-dev libjpeg-dev libpng-dev libtiff-dev tesseract-ocr poppler-utils libreoffice

echo -e "\n -> Cloning development branch of repository \n"
git clone /mayan-edms-repository/ $INSTALLATION_DIRECTORY
cd $INSTALLATION_DIRECTORY
git checkout development
git reset HEAD --hard

echo -e "\n -> Setting up virtual env \n"
virtualenv venv
source venv/bin/activate

echo -e "\n -> Installing python dependencies \n"
pip install -r requirements.txt

echo -e "\n -> Running Mayan EDMS initial setup \n"
./manage.py initialsetup

echo -e "\n -> Installing Redis server \n"
sudo apt-get install -y redis-server
pip install redis

echo -e "\n -> Installing testing software \n"
pip install coverage

echo -e "\n -> Installing MySQL \n"
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password '$DB_PASSWORD
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password '$DB_PASSWORD
sudo apt-get install -y mysql-server libmysqlclient-dev
# Create a passwordless root and travis users
mysql -u root -p$DB_PASSWORD -e "SET PASSWORD = PASSWORD('');"
mysql -u root -e "CREATE USER 'travis'@'localhost' IDENTIFIED BY '';GRANT ALL PRIVILEGES ON * . * TO 'travis'@'localhost';FLUSH PRIVILEGES;"
mysql -u travis -e "CREATE DATABASE $DB_NAME;"
pip install mysql-python

echo -e "\n -> Installing PostgreSQL \n"
sudo apt-get install -y postgresql postgresql-server-dev-all
sudo -u postgres psql -c 'create database mayan_edms;' -U postgres
sudo cat > /etc/postgresql/9.3/main/pg_hba.conf << EOF
local   all             postgres                                trust

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     peer
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
EOF

pip install -q psycopg2
