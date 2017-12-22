FROM python:2.7
MAINTAINER Tina Zhou "littlezhoubear@gmail.com"

# Install base libraries
RUN apt-get update && \
apt-get install -y -q --no-install-recommends \
    sudo \
    netcat-openbsd \
    python-dev \
    python-pip \
    graphviz \
    redis-server \
    libjpeg-dev \
    libmagic1 \
    libpng-dev \
    libreoffice \
    libpq-dev \
    git-core \
    libtiff-dev \
    gcc \
    ghostscript \
    python-dev \
    python-virtualenv \
    tesseract-ocr \
    poppler-utils && \
apt-get clean autoclean && \
apt-get autoremove -y && \
rm -rf /var/lib/apt/lists/* && \
rm -f /var/cache/apt/archives/*.deb

# Clone and install mayan edms
ENV MAYAN_VERSION v1.0
RUN mkdir -p /usr/src/mayan && \
    git clone https://github.com/zhoubear/open-paperless.git /usr/src/mayan && \
    (cd /usr/src/mayan && virtualenv venv && . venv/bin/activate)
    (cd /usr/src/mayan && . venv/bin/activate && pip install --no-cache-dir -r requirements/production.txt)

#        (cd /usr/src/mayan && git checkout -q tags/$MAYAN_VERSION) && \

# Create directories
RUN mkdir -p /usr/src/mayan/mayan/media/document_cache
RUN mkdir -p /usr/src/mayan/mayan/media/document_storage

# Set working dir
WORKDIR /usr/src/mayan

# Create user
RUN groupadd -g 1000 mayan \
    && useradd -u 1000 -g 1000 -d /usr/src/mayan mayan \
    && chown -Rh mayan:mayan /usr/src/mayan

# Setup entrypoint
COPY entrypoint.sh /sbin/entrypoint.sh
RUN chmod 755 /sbin/entrypoint.sh

# Mount volume
VOLUME ["/usr/src/mayan/mayan/media", "/tmp/settings.conf"]
EXPOSE 8000

ENTRYPOINT ["/sbin/entrypoint.sh"]
CMD ["runserver", "--insecure", "0.0.0.0:8000"]

