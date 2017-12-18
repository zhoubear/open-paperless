Use Ubuntu version 16.10 or newer only:

    apt-get install graphviz nginx supervisor redis-server postgresql \
    libpq-dev libjpeg-dev libmagic1 libpng-dev libreoffice \
    libtiff-dev gcc ghostscript gnupg python-dev python-virtualenv \
    tesseract-ocr poppler-utils gnupg1 -y


    sudo -i

    cd /usr/share

    virtualenv open-paperless

    source open-paperless/bin/activate

    pip install open-paperless

    pip install psycopg2 redis uwsgi

    sudo -u postgres createuser -P open-paperless  (provide password)
    sudo -u postgres createdb -O open-paperless open-paperless

    mkdir /var/log/open-paperless

    cd open-paperless

    ln -s lib/python2.7/site-packages/mayan .

    open-paperless.py createsettings

Append the following to the ``mayan/settings/local.py`` file, paying attention to replace the ``PASSWORD`` value::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'open-paperless',
            'USER': 'open-paperless',
            'PASSWORD': '<password used when creating postgreSQL user>',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

    BROKER_URL = 'redis://127.0.0.1:6379/0'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
    SIGNATURES_GPG_PATH = '/usr/bin/gpg1'

    mayan-edms.py initialsetup

