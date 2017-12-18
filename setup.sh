#!/bin/sh

sudo apt-get install virtualenvwrapper graphviz redis-server \
libpq-dev libjpeg-dev libmagic1 libpng-dev libreoffice \
libtiff-dev gcc ghostscript gnupg python-dev python-virtualenv \
tesseract-ocr poppler-utils -y

virtualenv venv
. venv/bin/activate

pip install -r requirements/production.txt
./manage.py initialsetup
./manage.py collectstatic --noinput
