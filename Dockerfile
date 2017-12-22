FROM python:2-alpine3.7

ENV ALPINE_VERSION 3.7

WORKDIR /usr/src/app

COPY ./requirements ./requirements/

RUN echo "http://dl-cdn.alpinelinux.org/alpine/v$ALPINE_VERSION/community" >> /etc/apk/repositories \
	&& apk add --no-cache graphviz postgresql-dev libjpeg libmagic libpng-dev musl-dev linux-headers \
	libreoffice tiff-dev gcc ghostscript gnupg poppler-utils tesseract-ocr tesseract-ocr-data-fra g++ libzmq \
    && pip install --no-cache-dir -r requirements/production.txt \
	&& pip install psycopg2 \
	&& apk del --purge --no-cache musl-dev linux-headers gcc g++

ENV DATABASE_NAME postgres
ENV DATABASE_USER postgres
ENV DATABASE_HOST localhost
ENV DATABASE_PORT "5432"
ENV REDIS_URL "redis://127.0.0.1:6379/0"
ENV DJANGO_SETTINGS_MODULE "mayan.settings.staging.docker"

COPY . .

RUN ./manage.py collectstatic --noinput

EXPOSE 8000

CMD ./manage.py initialsetup \
	&& circusd circus-docker.ini
