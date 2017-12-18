from __future__ import unicode_literals

import StringIO

import gnupg
import mock

from common.tests import BaseTestCase
from common.utils import TemporaryFile

from ..exceptions import (
    DecryptionError, KeyDoesNotExist, NeedPassphrase, PassphraseError,
    VerificationError
)
from ..models import Key

from .literals import (
    TEST_DETACHED_SIGNATURE, TEST_FILE, TEST_KEY_DATA, TEST_KEY_FINGERPRINT,
    TEST_KEY_PASSPHRASE, TEST_RECEIVE_KEY, TEST_SEARCH_FINGERPRINT,
    TEST_SEARCH_UID, TEST_SIGNED_FILE, TEST_SIGNED_FILE_CONTENT
)

MOCK_SEARCH_KEYS_RESPONSE = [
    {
        'algo': u'1',
        'date': u'1311475606',
        'expires': u'1643601600',
        'keyid': u'607138F1AECC5A5CA31CB7715F3F7F75D210724D',
        'length': u'2048',
        'type': u'pub',
        'uids': [u'Roberto Rosario <roberto.rosario.gonzalez@gmail.com>']
    }
]


def mock_recv_keys(self, keyserver, *keyids):
    class ImportResult(object):
        count = 1
        fingerprints = [TEST_SEARCH_FINGERPRINT]

    self.import_keys(TEST_RECEIVE_KEY)

    return ImportResult()


class KeyTestCase(BaseTestCase):
    def test_key_instance_creation(self):
        # Creating a Key instance is analogous to importing a key
        key = Key.objects.create(key_data=TEST_KEY_DATA)

        self.assertEqual(key.fingerprint, TEST_KEY_FINGERPRINT)

    @mock.patch.object(gnupg.GPG, 'search_keys', autospec=True)
    def test_key_search(self, search_keys):
        search_keys.return_value = MOCK_SEARCH_KEYS_RESPONSE

        search_results = Key.objects.search(query=TEST_SEARCH_UID)

        self.assertTrue(
            TEST_SEARCH_FINGERPRINT in [
                key_stub.fingerprint for key_stub in search_results
            ]
        )

    @mock.patch.object(gnupg.GPG, 'recv_keys', autospec=True)
    def test_key_receive(self, recv_keys):
        recv_keys.side_effect = mock_recv_keys

        Key.objects.receive_key(key_id=TEST_SEARCH_FINGERPRINT)

        self.assertEqual(Key.objects.all().count(), 1)
        self.assertEqual(
            Key.objects.first().fingerprint, TEST_SEARCH_FINGERPRINT
        )

    def test_cleartext_file_verification(self):
        cleartext_file = TemporaryFile()
        cleartext_file.write('test')
        cleartext_file.seek(0)

        with self.assertRaises(VerificationError):
            Key.objects.verify_file(file_object=cleartext_file)

        cleartext_file.close()

    def test_embedded_verification_no_key(self):
        with open(TEST_SIGNED_FILE) as signed_file:
            result = Key.objects.verify_file(signed_file)

        self.assertTrue(result.key_id in TEST_KEY_FINGERPRINT)

    def test_embedded_verification_with_key(self):
        Key.objects.create(key_data=TEST_KEY_DATA)

        with open(TEST_SIGNED_FILE) as signed_file:
            result = Key.objects.verify_file(signed_file)

        self.assertEqual(result.fingerprint, TEST_KEY_FINGERPRINT)

    def test_embedded_verification_with_correct_fingerprint(self):
        Key.objects.create(key_data=TEST_KEY_DATA)

        with open(TEST_SIGNED_FILE) as signed_file:
            result = Key.objects.verify_file(
                signed_file, key_fingerprint=TEST_KEY_FINGERPRINT
            )

        self.assertTrue(result.valid)
        self.assertEqual(result.fingerprint, TEST_KEY_FINGERPRINT)

    def test_embedded_verification_with_incorrect_fingerprint(self):
        Key.objects.create(key_data=TEST_KEY_DATA)

        with open(TEST_SIGNED_FILE) as signed_file:
            with self.assertRaises(KeyDoesNotExist):
                Key.objects.verify_file(signed_file, key_fingerprint='999')

    def test_signed_file_decryption(self):
        Key.objects.create(key_data=TEST_KEY_DATA)

        with open(TEST_SIGNED_FILE) as signed_file:
            result = Key.objects.decrypt_file(file_object=signed_file)

        self.assertEqual(result.read(), TEST_SIGNED_FILE_CONTENT)

    def test_cleartext_file_decryption(self):
        cleartext_file = TemporaryFile()
        cleartext_file.write('test')
        cleartext_file.seek(0)

        with self.assertRaises(DecryptionError):
            Key.objects.decrypt_file(file_object=cleartext_file)

        cleartext_file.close()

    def test_detached_verification_no_key(self):
        with open(TEST_DETACHED_SIGNATURE) as signature_file:
            with open(TEST_FILE) as test_file:
                result = Key.objects.verify_file(
                    file_object=test_file, signature_file=signature_file
                )

        self.assertTrue(result.key_id in TEST_KEY_FINGERPRINT)

    def test_detached_verification_with_key(self):
        Key.objects.create(key_data=TEST_KEY_DATA)

        with open(TEST_DETACHED_SIGNATURE) as signature_file:
            with open(TEST_FILE) as test_file:
                result = Key.objects.verify_file(
                    file_object=test_file, signature_file=signature_file
                )

        self.assertTrue(result)
        self.assertEqual(result.fingerprint, TEST_KEY_FINGERPRINT)

    def test_detached_signing_no_passphrase(self):
        key = Key.objects.create(key_data=TEST_KEY_DATA)

        with self.assertRaises(NeedPassphrase):
            with open(TEST_FILE) as test_file:
                key.sign_file(
                    file_object=test_file, detached=True,
                )

    def test_detached_signing_bad_passphrase(self):
        key = Key.objects.create(key_data=TEST_KEY_DATA)

        with self.assertRaises(PassphraseError):
            with open(TEST_FILE) as test_file:
                key.sign_file(
                    file_object=test_file, detached=True,
                    passphrase='bad passphrase'
                )

    def test_detached_signing_with_passphrase(self):
        key = Key.objects.create(key_data=TEST_KEY_DATA)

        with open(TEST_FILE) as test_file:
            detached_signature = key.sign_file(
                file_object=test_file, detached=True,
                passphrase=TEST_KEY_PASSPHRASE
            )

        signature_file = StringIO.StringIO()
        signature_file.write(detached_signature)
        signature_file.seek(0)

        with open(TEST_FILE) as test_file:
            result = Key.objects.verify_file(
                file_object=test_file, signature_file=signature_file
            )

        signature_file.close()
        self.assertTrue(result)
        self.assertEqual(result.fingerprint, TEST_KEY_FINGERPRINT)
