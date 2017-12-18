#!/usr/bin/env python

from __future__ import unicode_literals

import os

import django
from django.conf import settings
from django.template import Template, Context

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REQUIREMENTS_FILE = 'requirements.txt'
SETUP_TEMPLATE = 'setup.py.tmpl'


def get_requirements(base_directory, filename):
    result = []

    with open(os.path.join(base_directory, filename)) as file_object:
        for line in file_object:
            if line.startswith('-r'):
                line = line.split('\n')[0][3:]
                directory, filename = os.path.split(line)
                result.extend(
                    get_requirements(
                        base_directory=os.path.join(base_directory, directory), filename=filename
                    )
                )
            elif not line.startswith('\n'):
                result.append(line.split('\n')[0])

    return result


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
    django.setup()

    requirements = get_requirements(
        base_directory=BASE_DIR, filename=REQUIREMENTS_FILE
    )

    with open(SETUP_TEMPLATE) as file_object:
        template = file_object.read()
        result = Template(template).render(
            context=Context({'requirements': requirements})
        )

    with open('setup.py', 'w') as file_object:
        file_object.write(result)
