#!/usr/bin/env bash

# ====== CONFIG ======
INSTALLATION_DIRECTORY=/usr/share/mayan-edms/
DB_NAME=mayan_edms
DB_USERNAME=mayan
DB_PASSWORD=test123
# ==== END CONFIG ====

cat << EOF | tee -a /etc/motd.tail
**********************************

Mayan EDMS Vagrant Production Box

**********************************
EOF

echo -e "\n -> Running apt-get update & upgrade \n"
apt-get -qq update
apt-get -y upgrade

echo -e "\n -> Installing core binaries \n"
apt-get install nginx supervisor redis-server postgresql libpq-dev libjpeg-dev libmagic1 libpng-dev libreoffice libtiff-dev gcc ghostscript gpgv python-dev python-virtualenv tesseract-ocr poppler-utils -y

echo -e "\n -> Setting up virtualenv \n"
rm -f ${INSTALLATION_DIRECTORY}
virtualenv ${INSTALLATION_DIRECTORY}
source ${INSTALLATION_DIRECTORY}bin/activate

echo -e "\n -> Installing Mayan EDMS from PyPI \n"
pip install mayan-edms

echo -e "\n -> Installing Python client for PostgreSQL, Redis, and uWSGI \n"
pip install psycopg2 redis uwsgi

echo -e "\n -> Creating the database for the installation \n"
echo "CREATE USER mayan WITH PASSWORD '$DB_PASSWORD';" | sudo -u postgres psql
sudo -u postgres createdb -O $DB_USERNAME $DB_NAME

echo -e "\n -> Creating the directories for the logs \n"
mkdir /var/log/mayan

echo -e "\n -> Making a convenience symlink \n"
cd ${INSTALLATION_DIRECTORY}
ln -s lib/python2.7/site-packages/mayan .

echo -e "\n -> Creating an initial settings file \n"
mayan-edms.py createsettings

echo -e "\n -> Updating the mayan/settings/local.py file \n"
cat >> mayan/settings/local.py << EOF
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '$DB_NAME',
        'USER': '$DB_USERNAME',
        'PASSWORD': '$DB_PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
EOF

echo -e "\n -> Migrating the database or initialize the project \n"
mayan-edms.py initialsetup

echo -e "\n -> Disabling the default NGINX site \n"
rm -f /etc/nginx/sites-enabled/default

echo -e "\n -> Creating a uwsgi.ini file \n"
cat > uwsgi.ini << EOF
[uwsgi]
chdir = ${INSTALLATION_DIRECTORY}lib/python2.7/site-packages/mayan
chmod-socket = 664
chown-socket = www-data:www-data
env = DJANGO_SETTINGS_MODULE=mayan.settings.production
gid = www-data
logto = /var/log/uwsgi/%n.log
pythonpath = ${INSTALLATION_DIRECTORY}lib/python2.7/site-packages
master = True
max-requests = 5000
socket = ${INSTALLATION_DIRECTORY}uwsgi.sock
uid = www-data
vacuum = True
wsgi-file = ${INSTALLATION_DIRECTORY}lib/python2.7/site-packages/mayan/wsgi.py
EOF

echo -e "\n -> Creating the directory for the uWSGI log files \n"
mkdir -p /var/log/uwsgi

echo -e "\n -> Creating the NGINX site file for Mayan EDMS, /etc/nginx/sites-available/mayan \n"
cat > /etc/nginx/sites-available/mayan << EOF
server {
    listen 80;
    server_name localhost;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:${INSTALLATION_DIRECTORY}uwsgi.sock;

        client_max_body_size 30M;  # Increse if your plan to upload bigger documents
        proxy_read_timeout 30s;  # Increase if your document uploads take more than 30 seconds
    }

    location /static {
        alias ${INSTALLATION_DIRECTORY}mayan/media/static;
        expires 1h;
    }

    location /favicon.ico {
        alias ${INSTALLATION_DIRECTORY}mayan/media/static/appearance/images/favicon.ico;
        expires 1h;
    }
}
EOF

echo -e "\n -> Enabling the NGINX site for Mayan EDMS \n"
ln -s /etc/nginx/sites-available/mayan /etc/nginx/sites-enabled/

echo -e "\n -> Creating the supervisor file for the uWSGI process, /etc/supervisor/conf.d/mayan-uwsgi.conf \n"
cat > /etc/supervisor/conf.d/mayan-uwsgi.conf << EOF
[program:mayan-uwsgi]
command = ${INSTALLATION_DIRECTORY}bin/uwsgi --ini ${INSTALLATION_DIRECTORY}uwsgi.ini
user = root
autostart = true
autorestart = true
redirect_stderr = true
EOF

echo -e "\n -> Creating the supervisor file for the Celery worker, /etc/supervisor/conf.d/mayan-celery.conf \n"
cat > /etc/supervisor/conf.d/mayan-celery.conf << EOF
[program:mayan-worker]
command = ${INSTALLATION_DIRECTORY}bin/python ${INSTALLATION_DIRECTORY}bin/mayan-edms.py celery --settings=mayan.settings.production worker -Ofair -l ERROR
directory = ${INSTALLATION_DIRECTORY}
user = www-data
stdout_logfile = /var/log/mayan/worker-stdout.log
stderr_logfile = /var/log/mayan/worker-stderr.log
autostart = true
autorestart = true
startsecs = 10
stopwaitsecs = 10
killasgroup = true
priority = 998

[program:mayan-beat]
command = ${INSTALLATION_DIRECTORY}bin/python ${INSTALLATION_DIRECTORY}bin/mayan-edms.py celery --settings=mayan.settings.production beat -l ERROR
directory = ${INSTALLATION_DIRECTORY}
user = www-data
numprocs = 1
stdout_logfile = /var/log/mayan/beat-stdout.log
stderr_logfile = /var/log/mayan/beat-stderr.log
autostart = true
autorestart = true
startsecs = 10
stopwaitsecs = 1
killasgroup = true
priority = 998
EOF

echo -e "\n -> Collecting the static files \n"
mayan-edms.py collectstatic --noinput

echo -e "\n -> Making the installation directory readable and writable by the webserver user \n"
chown www-data:www-data ${INSTALLATION_DIRECTORY} -R

echo -e "\n -> Restarting the services \n"
/etc/init.d/nginx restart
/etc/init.d/supervisor restart
