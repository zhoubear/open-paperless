from __future__ import unicode_literals

import logging
import os
import shutil
import tempfile
import types

from django.conf import settings
from django.urls import resolve as django_resolve
from django.urls.base import get_script_prefix
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import force_text
from django.utils.http import (
    urlencode as django_urlencode, urlquote as django_urlquote
)
from django.utils.six.moves import reduce as reduce_function, xmlrpc_client

from common.compat import dict_type, dictionary_type
import mayan

from .exceptions import NotLatestVersion
from .literals import MAYAN_PYPI_NAME, PYPI_URL
from .settings import setting_temporary_directory

logger = logging.getLogger(__name__)


def check_version():
    pypi = xmlrpc_client.ServerProxy(PYPI_URL)
    versions = pypi.package_releases(MAYAN_PYPI_NAME)

    if versions[0] != mayan.__version__:
        raise NotLatestVersion(upstream_version=versions[0])
    else:
        return True


# http://stackoverflow.com/questions/123198/how-do-i-copy-a-file-in-python
def copyfile(source, destination, buffer_size=1024 * 1024):
    """
    Copy a file from source to dest. source and dest
    can either be strings or any object with a read or
    write method, like StringIO for example.
    """
    source_descriptor = get_descriptor(source)
    destination_descriptor = get_descriptor(destination, read=False)

    while True:
        copy_buffer = source_descriptor.read(buffer_size)
        if copy_buffer:
            destination_descriptor.write(copy_buffer)
        else:
            break

    source_descriptor.close()
    destination_descriptor.close()


def encapsulate(function):
    # Workaround Django ticket 15791
    # Changeset 16045
    # http://stackoverflow.com/questions/6861601/
    # cannot-resolve-callable-context-variable/6955045#6955045
    return lambda: function


def fs_cleanup(filename, file_descriptor=None, suppress_exceptions=True):
    """
    Tries to remove the given filename. Ignores non-existent files
    """
    if file_descriptor:
        os.close(file_descriptor)

    try:
        os.remove(filename)
    except OSError:
        try:
            shutil.rmtree(filename)
        except OSError:
            if suppress_exceptions:
                pass
            else:
                raise


def get_descriptor(file_input, read=True):
    try:
        # Is it a file like object?
        file_input.seek(0)
    except AttributeError:
        # If not, try open it.
        if read:
            return open(file_input, 'rb')
        else:
            return open(file_input, 'wb')
    else:
        return file_input


def index_or_default(instance, index, default):
    try:
        return instance[index]
    except IndexError:
        return default


def TemporaryFile(*args, **kwargs):
    kwargs.update({'dir': setting_temporary_directory.value})
    return tempfile.TemporaryFile(*args, **kwargs)


def mkdtemp(*args, **kwargs):
    kwargs.update({'dir': setting_temporary_directory.value})
    return tempfile.mkdtemp(*args, **kwargs)


def mkstemp(*args, **kwargs):
    kwargs.update({'dir': setting_temporary_directory.value})
    return tempfile.mkstemp(*args, **kwargs)


def resolve(path, urlconf=None):
    path = '/{}'.format(path.replace(get_script_prefix(), '', 1))
    return django_resolve(path=path, urlconf=urlconf)


def return_attrib(obj, attrib, arguments=None):
    try:
        if isinstance(attrib, types.FunctionType):
            return attrib(obj)
        elif isinstance(
            obj, dict_type
        ) or isinstance(obj, dictionary_type):
            return obj[attrib]
        else:
            result = reduce_function(getattr, attrib.split('.'), obj)
            if isinstance(result, types.MethodType):
                if arguments:
                    return result(**arguments)
                else:
                    return result()
            else:
                return result
    except Exception as exception:
        if settings.DEBUG:
            return 'Attribute error: %s; %s' % (attrib, exception)
        else:
            return force_text(exception)


def urlquote(link=None, get=None):
    """
    This method does both: urlquote() and urlencode()

    urlqoute(): Quote special characters in 'link'

    urlencode(): Map dictionary to query string key=value&...

    HTML escaping is not done.

    Example:

    urlquote('/wiki/Python_(programming_language)')
        --> '/wiki/Python_%28programming_language%29'
    urlquote('/mypath/', {'key': 'value'})
        --> '/mypath/?key=value'
    urlquote('/mypath/', {'key': ['value1', 'value2']})
        --> '/mypath/?key=value1&key=value2'
    urlquote({'key': ['value1', 'value2']})
        --> 'key=value1&key=value2'
    """
    if get is None:
        get = []

    assert link or get
    if isinstance(link, dict):
        # urlqoute({'key': 'value', 'key2': 'value2'}) -->
        # key=value&key2=value2
        assert not get, get
        get = link
        link = ''
    assert isinstance(get, dict), 'wrong type "%s", dict required' % type(get)
    # assert not (link.startswith('http://') or link.startswith('https://')),
    #    'This method should only quote the url path.
    #    It should not start with http(s)://  (%s)' % (
    #    link)
    if get:
        # http://code.djangoproject.com/ticket/9089
        if isinstance(get, MultiValueDict):
            get = get.lists()
        if link:
            link = '%s?' % django_urlquote(link)
        return '%s%s' % (link, django_urlencode(get, doseq=True))
    else:
        return django_urlquote(link)


def validate_path(path):
    if not os.path.exists(path):
        # If doesn't exist try to create it
        try:
            os.mkdir(path)
        except Exception as exception:
            logger.debug('unhandled exception: %s', exception)
            return False

    # Check if it is writable
    try:
        fd, test_filepath = tempfile.mkstemp(dir=path)
        os.close(fd)
        os.unlink(test_filepath)
    except Exception as exception:
        logger.debug('unhandled exception: %s', exception)
        return False

    return True
