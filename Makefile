.PHONY: clean-pyc clean-build


help:
	@echo
	@echo "clean-build - Remove build artifacts."
	@echo "clean-pyc - Remove Python artifacts."
	@echo "clean - Remove Python and build artifacts."
	@echo "generate_setup - Create and updated setup.py"

	@echo "test-all - Run all tests."
	@echo "test MODULE=<python module name> - Run tests for a single app, module or test class."
	@echo "test-with-postgres-all - Run all tests against a Postgres database container."
	@echo "test-postgres MODULE=<python module name> - Run tests for a single app, module or test class against a Postgres database container."
	@echo "test-with-mysql-all - Run all tests against a MySQL database container."
	@echo "test-mysql MODULE=<python module name> - Run tests for a single app, module or test class against a MySQL database container."
	@echo "test-with-oracle-all - Run all tests against a Oracle database container."
	@echo "test-oracle MODULE=<python module name> - Run tests for a single app, module or test class against a Oracle database container."

	@echo "docs_serve - Run the livehtml documentation generator."

	@echo "translations_make - Refresh all translation files."
	@echo "translations_compile - Compile all translation files."
	@echo "translations_push - Upload all translation files to Transifex."
	@echo "translations_pull - Download all translation files from Transifex."

	@echo "requirements_dev - Install development requirements."
	@echo "requirements_docs - Install documentation requirements."
	@echo "requirements_testing - Install testing requirements."

	@echo "sdist - Build the source distribution package."
	@echo "wheel - Build the wheel distribution package."
	@echo "release - Package (sdist and wheel) and upload a release."
	@echo "test_release - Package (sdist and wheel) and upload to the PyPI test server."
	@echo "release_test_via_docker_ubuntu - Package (sdist and wheel) and upload to the PyPI test server using an Ubuntu Docker builder."
	@echo "release_test_via_docker_alpine - Package (sdist and wheel) and upload to the PyPI test server using an Alpine Docker builder."
	@echo "release_via_docker_ubuntu - Package (sdist and wheel) and upload to PyPI using an Ubuntu Docker builder."
	@echo "release_via_docker_alpine - Package (sdist and wheel) and upload to PyPI using an Alpine Docker builder."
	@echo "test_sdist_via_docker_ubuntu - Make an sdist packange and test it using an Ubuntu Docker container."
	@echo "test_wheel_via_docker_ubuntu - Make a wheel package and test it using an Ubuntu Docker container."

	@echo "runserver - Run the development server."
	@echo "runserver_plus - Run the Django extension's development server."
	@echo "shell_plus - Run the shell_plus command."

	@echo "docker_services_on - Launch and initialize production-like services using Docker (Postgres and Redis)."
	@echo "docker_services_off - Stop and delete the Docker production-like services."
	@echo "docker_services_frontend - Launch a front end instance that uses the production-like services."
	@echo "docker_services_worker - Launch a worker instance that uses the production-like services."
	@echo "docker_service_mysql_on - Launch and initialize a MySQL Docker container."
	@echo "docker_service_mysql_off - Stop and delete the MySQL Docker container."
	@echo "docker_service_postgres_on - Launch and initialize a PostgreSQL Docker container."
	@echo "docker_service_postgres_off - Stop and delete the PostgreSQL Docker container."

	@echo "safety_check - Run a package safety check."


# Cleaning

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +


# Testing

test:
	./manage.py test $(MODULE) --settings=mayan.settings.testing --nomigrations

test-all:
	./manage.py test --mayan-apps --settings=mayan.settings.testing --nomigrations

test-launch-postgres:
	@docker rm -f test-postgres || true
	@docker volume rm test-postgres || true
	docker run -d --name test-postgres -p 5432:5432 -v test-postgres:/var/lib/postgresql/data healthcheck/postgres
	sudo apt-get install -qq libpq-dev
	pip install psycopg2
	while ! docker inspect --format='{{json .State.Health}}' test-postgres|grep 'Status":"healthy"'; do sleep 1; done

test-with-postgres: test-launch-postgres
	./manage.py test $(MODULE) --settings=mayan.settings.testing.docker.db_postgres --nomigrations
	@docker rm -f test-postgres || true
	@docker volume rm test-postgres || true

test-with-postgres-all: test-launch-postgres
	./manage.py test --mayan-apps --settings=mayan.settings.testing.docker.db_postgres --nomigrations
	@docker rm -f test-postgres || true
	@docker volume rm test-postgres || true

test-launch-mysql:
	@docker rm -f test-mysql || true
	@docker volume rm test-mysql || true
	docker run -d --name test-mysql -p 3306:3306 -e MYSQL_ALLOW_EMPTY_PASSWORD=True -e MYSQL_DATABASE=mayan -v test-mysql:/var/lib/mysql healthcheck/mysql
	sudo apt-get install -qq libmysqlclient-dev mysql-client
	pip install mysql-python
	while ! docker inspect --format='{{json .State.Health}}' test-mysql|grep 'Status":"healthy"'; do sleep 1; done
	mysql -h 127.0.0.1 -P 3306 -uroot  -e "set global character_set_server=utf8mb4;"

test-with-mysql: test-launch-mysql
	./manage.py test $(MODULE) --settings=mayan.settings.testing.docker.db_mysql --nomigrations
	@docker rm -f test-mysql || true
	@docker volume rm test-mysql || true

test-with-mysql-all: test-launch-mysql
	./manage.py test --mayan-apps --settings=mayan.settings.testing.docker.db_mysql --nomigrations
	@docker rm -f test-mysql || true
	@docker volume rm test-mysql || true

test-launch-oracle:
	@docker rm -f test-oracle || true
	@docker volume rm test-oracle || true
	docker run -d --name test-oracle -p 49160:22 -p 49161:1521 -e ORACLE_ALLOW_REMOTE=true -v test-oracle:/u01/app/oracle wnameless/oracle-xe-11g
	# https://gist.github.com/kimus/10012910
	pip install cx_Oracle
	while ! nc -z 127.0.0.1 49161; do sleep 1; done
	sleep 10

test-with-oracle: test-launch-oracle
	./manage.py test $(MODULE) --settings=mayan.settings.testing.docker.db_oracle --nomigrations
	@docker rm -f test-oracle || true
	@docker volume rm test-oracle || true

test-with-oracle-all: test-launch-oracle
	./manage.py test --mayan-apps --settings=mayan.settings.testing.docker.db_oracle --nomigrations
	@docker rm -f test-oracle || true
	@docker volume rm test-oracle || true

# Documentation

docs_serve:
	cd docs;make livehtml


# Translations

translations_make:
	contrib/scripts/process_messages.py -m

translations_compile:
	contrib/scripts/process_messages.py -c

translations_push:
	tx push -s

translations_pull:
	tx pull -f


# Requirements

requirements_dev:
	pip install -r requirements/development.txt

requirements_docs:
	pip install -r requirements/documentation.txt

requirements_testing:
	pip install -r requirements/testing.txt

generate_setup:
	@./generate_setup.py
	@echo "Complete."

# Releases


test_release: clean wheel
	twine upload dist/* -r testpypi
	@echo "Test with: pip install -i https://testpypi.python.org/pypi mayan-edms"

release: clean wheel
	twine upload dist/* -r pypi

sdist: clean
	python setup.py sdist
	ls -l dist

wheel: clean sdist
	pip wheel --no-index --no-deps --wheel-dir dist dist/*.tar.gz
	ls -l dist

release_test_via_docker_ubuntu:
	docker run --rm --name mayan_release -v $(HOME):/host_home:ro -v `pwd`:/host_source -w /source ubuntu:16.04 /bin/bash -c "\
	echo "LC_ALL=\"en_US.UTF-8\"" >> /etc/default/locale && \
	locale-gen en_US.UTF-8 && \
	update-locale LANG=en_US.UTF-8 && \
	export LC_ALL=en_US.UTF-8 && \
	cp -r /host_source/* . && \
	apt-get update && \
	apt-get install make python-pip -y && \
	pip install -r requirements/build.txt && \
	cp -r /host_home/.pypirc ~/.pypirc && \
	make test_release"

release_via_docker_ubuntu:
	docker run --rm --name mayan_release -v $(HOME):/host_home:ro -v `pwd`:/host_source -w /source ubuntu:16.04 /bin/bash -c "\
	echo "LC_ALL=\"en_US.UTF-8\"" >> /etc/default/locale && \
	locale-gen en_US.UTF-8 && \
	update-locale LANG=en_US.UTF-8 && \
	export LC_ALL=en_US.UTF-8 && \
	cp -r /host_source/* . && \
	apt-get update && \
	apt-get install make python-pip -y && \
	pip install -r requirements/build.txt && \
	cp -r /host_home/.pypirc ~/.pypirc && \
	make release"

release_test_via_docker_alpine:
	docker run --rm --name mayan_release -v $(HOME):/host_home:ro -v `pwd`:/host_source -w /source alpine /bin/busybox sh -c "\
	echo "LC_ALL=\"en_US.UTF-8\"" >> /etc/default/locale && \
	locale-gen en_US.UTF-8 && \
	update-locale LANG=en_US.UTF-8 && \
	export LC_ALL=en_US.UTF-8 && \
	cp -r /host_source/* . && \
	apk update && \
	apk add python2 py2-pip make && \
	pip install -r requirements/build.txt && \
	cp -r /host_home/.pypirc ~/.pypirc && \
	make test_release"

release_via_docker_alpine:
	docker run --rm --name mayan_release -v $(HOME):/host_home:ro -v `pwd`:/host_source -w /source alpine /bin/busybox sh -c "\
	echo "LC_ALL=\"en_US.UTF-8\"" >> /etc/default/locale && \
	locale-gen en_US.UTF-8 && \
	update-locale LANG=en_US.UTF-8 && \
	export LC_ALL=en_US.UTF-8 && \
	cp -r /host_source/* . && \
	apk update && \
	apk add python2 py2-pip make && \
	pip install -r requirements/build.txt && \
	cp -r /host_home/.pypirc ~/.pypirc && \
	make release"

test_sdist_via_docker_ubuntu:
	docker run --rm --name mayan_sdist_test -v $(HOME):/host_home:ro -v `pwd`:/host_source -w /source ubuntu:16.04 /bin/bash -c "\
	cp -r /host_source/* . && \
	echo "LC_ALL=\"en_US.UTF-8\"" >> /etc/default/locale && \
	locale-gen en_US.UTF-8 && \
	update-locale LANG=en_US.UTF-8 && \
	export LC_ALL=en_US.UTF-8 && \
	apt-get update && \
	apt-get install make python-pip libreoffice tesseract-ocr tesseract-ocr-deu poppler-utils -y && \
	pip install -r requirements/development.txt && \
	make sdist_test_suit \
	"

test_wheel_via_docker_ubuntu:
	docker run --rm --name mayan_wheel_test -v $(HOME):/host_home:ro -v `pwd`:/host_source -w /source ubuntu:16.04 /bin/bash -c "\
	cp -r /host_source/* . && \
	echo "LC_ALL=\"en_US.UTF-8\"" >> /etc/default/locale && \
	locale-gen en_US.UTF-8 && \
	update-locale LANG=en_US.UTF-8 && \
	export LC_ALL=en_US.UTF-8 && \
	apt-get update && \
	apt-get install make python-pip libreoffice tesseract-ocr tesseract-ocr-deu poppler-utils -y && \
	pip install -r requirements/development.txt && \
	make wheel_test_suit \
	"

sdist_test_suit: sdist
	rm -f -R _virtualenv
	virtualenv _virtualenv
	sh -c '\
	. _virtualenv/bin/activate; \
	pip install `ls dist/*.gz`; \
	_virtualenv/bin/mayan-edms.py initialsetup; \
	pip install mock==2.0.0; \
	_virtualenv/bin/mayan-edms.py test --mayan-apps \
	'

wheel_test_suit: wheel
	rm -f -R _virtualenv
	virtualenv _virtualenv
	sh -c '\
	. _virtualenv/bin/activate; \
	pip install `ls dist/*.whl`; \
	_virtualenv/bin/mayan-edms.py initialsetup; \
	pip install mock==2.0.0; \
	_virtualenv/bin/mayan-edms.py test --mayan-apps \
	'

# Dev server

runserver:
	./manage.py runserver --settings=mayan.settings.development

runserver_plus:
	./manage.py runserver_plus --settings=mayan.settings.development

shell_plus:
	./manage.py shell_plus --settings=mayan.settings.development

docker_services_on:
	docker run -d --name redis -p 6379:6379 redis
	docker run -d --name postgres -p 5432:5432 postgres
	while ! nc -z 127.0.0.1 6379; do sleep 1; done
	while ! nc -z 127.0.0.1 5432; do sleep 1; done
	sleep 2
	./manage.py initialsetup --settings=mayan.settings.staging.docker

docker_services_off:
	docker stop postgres redis
	docker rm postgres redis

docker_services_frontend:
	./manage.py runserver --settings=mayan.settings.staging.docker

docker_services_worker:
	./manage.py celery worker --settings=mayan.settings.staging.docker -B -l INFO -O fair

docker_service_mysql_on:
	docker run -d --name mysql -p 3306:3306 -e MYSQL_ALLOW_EMPTY_PASSWORD=True -e MYSQL_DATABASE=mayan_edms mysql
	while ! nc -z 127.0.0.1 3306; do sleep 1; done

docker_service_mysql_off:
	docker stop mysql
	docker rm mysql

docker_service_postgres_on:
	docker run -d --name postgres -p 5432:5432 postgres
	while ! nc -z 127.0.0.1 5432; do sleep 1; done

docker_service_postgres_off:
	docker stop postgres
	docker rm postgres


# Security

safety_check:
	safety check
