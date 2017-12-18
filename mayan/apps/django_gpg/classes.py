from __future__ import absolute_import, unicode_literals

from datetime import date
import os
import shutil

import gnupg

from common.utils import mkdtemp


class GPGBackend(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class PythonGNUPGBackend(GPGBackend):
    @staticmethod
    def _import_key(gpg, **kwargs):
        return gpg.import_keys(**kwargs)

    @staticmethod
    def _list_keys(gpg, **kwargs):
        return gpg.list_keys(**kwargs)

    @staticmethod
    def _import_and_list_keys(gpg, **kwargs):
        import_results = gpg.import_keys(**kwargs)
        return import_results, gpg.list_keys(
            keys=import_results.fingerprints[0]
        )[0]

    @staticmethod
    def _sign_file(gpg, file_object, key_data, passphrase, clearsign, detached, binary, output):
        import_results = gpg.import_keys(key_data=key_data)

        return gpg.sign_file(
            file=file_object, keyid=import_results.fingerprints[0],
            passphrase=passphrase, clearsign=clearsign, detach=detached,
            binary=binary, output=output
        )

    @staticmethod
    def _decrypt_file(gpg, file_object, keys):
        for key in keys:
            gpg.import_keys(key_data=key['key_data'])

        return gpg.decrypt_file(file=file_object)

    @staticmethod
    def _verify_file(gpg, file_object, keys, data_filename=None):
        for key in keys:
            gpg.import_keys(key_data=key['key_data'])

        return gpg.verify_file(
            file=file_object, data_filename=data_filename
        )

    @staticmethod
    def _recv_keys(gpg, keyserver, key_id):
        import_results = gpg.recv_keys(keyserver, key_id)
        if import_results.count:
            key_data = gpg.export_keys(import_results.fingerprints[0])
        else:
            key_data = None
        return key_data

    @staticmethod
    def _search_keys(gpg, keyserver, query):
        return gpg.search_keys(
            keyserver=keyserver, query=query
        )

    def gpg_command(self, function, **kwargs):
        temporary_directory = mkdtemp()
        os.chmod(temporary_directory, 0x1C0)

        gpg = gnupg.GPG(
            gnupghome=temporary_directory, gpgbinary=self.kwargs['binary_path']
        )

        result = function(gpg=gpg, **kwargs)

        shutil.rmtree(temporary_directory)

        return result

    def import_key(self, key_data):
        return self.gpg_command(
            function=PythonGNUPGBackend._import_key, key_data=key_data
        )

    def list_keys(self, keys):
        return self.gpg_command(
            function=PythonGNUPGBackend._list_keys, keys=keys
        )

    def import_and_list_keys(self, key_data):
        return self.gpg_command(
            function=PythonGNUPGBackend._import_and_list_keys,
            key_data=key_data
        )

    def sign_file(self, file_object, key_data, passphrase, clearsign, detached, binary, output):
        return self.gpg_command(
            function=PythonGNUPGBackend._sign_file, file_object=file_object,
            key_data=key_data, passphrase=passphrase, clearsign=clearsign,
            detached=detached, binary=binary, output=output
        )

    def decrypt_file(self, file_object, keys):
        return self.gpg_command(
            function=PythonGNUPGBackend._decrypt_file, file_object=file_object,
            keys=keys
        )

    def verify_file(self, file_object, keys, data_filename=None):
        return self.gpg_command(
            function=PythonGNUPGBackend._verify_file, file_object=file_object,
            keys=keys, data_filename=data_filename
        )

    def recv_keys(self, keyserver, key_id):
        return self.gpg_command(
            function=PythonGNUPGBackend._recv_keys, keyserver=keyserver,
            key_id=key_id
        )

    def search_keys(self, keyserver, query):
        return self.gpg_command(
            function=PythonGNUPGBackend._search_keys, keyserver=keyserver,
            query=query
        )


class KeyStub(object):
    def __init__(self, raw):
        self.fingerprint = raw['keyid']
        self.key_type = raw['type']
        self.date = date.fromtimestamp(int(raw['date']))
        if raw['expires']:
            self.expires = date.fromtimestamp(int(raw['expires']))
        else:
            self.expires = None
        self.length = raw['length']
        self.user_id = raw['uids']

    @property
    def key_id(self):
        return self.fingerprint[-8:]


class SignatureVerification(object):
    def __init__(self, raw):
        self.user_id = raw['username']
        self.status = raw['status']
        self.key_id = raw['key_id']
        self.pubkey_fingerprint = raw['pubkey_fingerprint']
        self.date = date.fromtimestamp(int(raw['timestamp']))
        if raw['expire_timestamp']:
            self.expires = date.fromtimestamp(int(raw['expire_timestamp']))
        else:
            self.expires = None
        self.trust_text = raw['trust_text']
        self.valid = raw['valid']
        self.stderr = raw['stderr']
        self.fingerprint = raw['fingerprint']
        self.signature_id = raw['signature_id']
        self.trust_level = raw['trust_level']
