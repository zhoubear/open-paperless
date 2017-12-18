from __future__ import unicode_literals

import hashlib
import logging
import time

from django.core.files import File
from django.test import override_settings

from common.tests import BaseTestCase
from django_gpg.models import Key
from django_gpg.tests.literals import TEST_KEY_DATA, TEST_KEY_PASSPHRASE
from documents.models import DocumentType, DocumentVersion
from documents.tests import TEST_DOCUMENT_PATH, TEST_DOCUMENT_TYPE_LABEL

from ..models import DetachedSignature, EmbeddedSignature
from ..tasks import task_verify_missing_embedded_signature

from .literals import (
    TEST_SIGNED_DOCUMENT_PATH, TEST_SIGNATURE_FILE_PATH, TEST_KEY_FILE,
    TEST_KEY_ID, TEST_SIGNATURE_ID
)


@override_settings(OCR_AUTO_OCR=False)
class DocumentSignaturesTestCase(BaseTestCase):
    def setUp(self):
        super(DocumentSignaturesTestCase, self).setUp()
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

    def tearDown(self):
        self.document_type.delete()
        super(DocumentSignaturesTestCase, self).tearDown()

    def test_embedded_signature_no_key(self):
        with open(TEST_SIGNED_DOCUMENT_PATH) as file_object:
            signed_document = self.document_type.new_document(
                file_object=file_object
            )

        self.assertEqual(EmbeddedSignature.objects.count(), 1)

        signature = EmbeddedSignature.objects.first()

        self.assertEqual(
            signature.document_version, signed_document.latest_version
        )
        self.assertEqual(signature.key_id, TEST_KEY_ID)
        self.assertEqual(signature.signature_id, None)

    def test_embedded_signature_post_key_verify(self):
        with open(TEST_SIGNED_DOCUMENT_PATH) as file_object:
            signed_document = self.document_type.new_document(
                file_object=file_object
            )

        self.assertEqual(EmbeddedSignature.objects.count(), 1)

        signature = EmbeddedSignature.objects.first()

        self.assertEqual(
            signature.document_version, signed_document.latest_version
        )
        self.assertEqual(signature.key_id, TEST_KEY_ID)
        self.assertEqual(signature.signature_id, None)

        with open(TEST_KEY_FILE) as file_object:
            Key.objects.create(key_data=file_object.read())

        signature = EmbeddedSignature.objects.first()

        self.assertEqual(signature.signature_id, TEST_SIGNATURE_ID)

    def test_embedded_signature_post_no_key_verify(self):
        with open(TEST_KEY_FILE) as file_object:
            key = Key.objects.create(key_data=file_object.read())

        with open(TEST_SIGNED_DOCUMENT_PATH) as file_object:
            signed_document = self.document_type.new_document(
                file_object=file_object
            )

        self.assertEqual(EmbeddedSignature.objects.count(), 1)

        signature = EmbeddedSignature.objects.first()

        self.assertEqual(
            signature.document_version, signed_document.latest_version
        )
        self.assertEqual(signature.key_id, TEST_KEY_ID)
        self.assertEqual(signature.signature_id, TEST_SIGNATURE_ID)

        key.delete()

        signature = EmbeddedSignature.objects.first()

        self.assertEqual(signature.signature_id, None)

    def test_embedded_signature_with_key(self):
        with open(TEST_KEY_FILE) as file_object:
            key = Key.objects.create(key_data=file_object.read())

        with open(TEST_SIGNED_DOCUMENT_PATH) as file_object:
            self.signed_document = self.document_type.new_document(
                file_object=file_object
            )

        self.assertEqual(EmbeddedSignature.objects.count(), 1)

        signature = EmbeddedSignature.objects.first()

        self.assertEqual(
            signature.document_version,
            self.signed_document.latest_version
        )
        self.assertEqual(signature.key_id, TEST_KEY_ID)
        self.assertEqual(signature.public_key_fingerprint, key.fingerprint)
        self.assertEqual(signature.signature_id, TEST_SIGNATURE_ID)

    def test_detached_signature_no_key(self):
        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            DetachedSignature.objects.create(
                document_version=document.latest_version,
                signature_file=File(file_object)
            )

        self.assertEqual(DetachedSignature.objects.count(), 1)

        signature = DetachedSignature.objects.first()

        self.assertEqual(signature.document_version, document.latest_version)
        self.assertEqual(signature.key_id, TEST_KEY_ID)
        self.assertEqual(signature.public_key_fingerprint, None)

    def test_detached_signature_with_key(self):
        with open(TEST_KEY_FILE) as file_object:
            key = Key.objects.create(key_data=file_object.read())

        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            DetachedSignature.objects.create(
                document_version=document.latest_version,
                signature_file=File(file_object)
            )

        self.assertEqual(DetachedSignature.objects.count(), 1)

        signature = DetachedSignature.objects.first()

        self.assertEqual(signature.document_version, document.latest_version)
        self.assertEqual(signature.key_id, TEST_KEY_ID)
        self.assertEqual(signature.public_key_fingerprint, key.fingerprint)

    def test_detached_signature_post_key_verify(self):
        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            DetachedSignature.objects.create(
                document_version=document.latest_version,
                signature_file=File(file_object)
            )

        self.assertEqual(DetachedSignature.objects.count(), 1)

        signature = DetachedSignature.objects.first()

        self.assertEqual(signature.document_version, document.latest_version)
        self.assertEqual(signature.key_id, TEST_KEY_ID)
        self.assertEqual(signature.public_key_fingerprint, None)

        with open(TEST_KEY_FILE) as file_object:
            key = Key.objects.create(key_data=file_object.read())

        signature = DetachedSignature.objects.first()

        self.assertEqual(signature.public_key_fingerprint, key.fingerprint)

    def test_detached_signature_post_no_key_verify(self):
        with open(TEST_KEY_FILE) as file_object:
            key = Key.objects.create(key_data=file_object.read())

        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            DetachedSignature.objects.create(
                document_version=document.latest_version,
                signature_file=File(file_object)
            )

        self.assertEqual(DetachedSignature.objects.count(), 1)

        signature = DetachedSignature.objects.first()

        self.assertEqual(signature.document_version, document.latest_version)
        self.assertEqual(signature.key_id, TEST_KEY_ID)
        self.assertEqual(signature.public_key_fingerprint, key.fingerprint)

        key.delete()

        signature = DetachedSignature.objects.first()

        self.assertEqual(signature.public_key_fingerprint, None)

    def test_document_no_signature(self):
        with open(TEST_DOCUMENT_PATH) as file_object:
            self.document_type.new_document(
                file_object=file_object
            )

        self.assertEqual(EmbeddedSignature.objects.count(), 0)

    def test_new_signed_version(self):
        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNED_DOCUMENT_PATH) as file_object:
            signed_version = document.new_version(
                file_object=file_object, comment='test comment 1'
            )

        # Artifical delay since MySQL doesn't store microsecond data in
        # timestamps. Version timestamp is used to determine which version
        # is the latest.
        time.sleep(2)

        self.assertEqual(EmbeddedSignature.objects.count(), 1)

        signature = EmbeddedSignature.objects.first()

        self.assertEqual(signature.document_version, signed_version)
        self.assertEqual(signature.key_id, TEST_KEY_ID)


@override_settings(OCR_AUTO_OCR=False)
class EmbeddedSignaturesTestCase(BaseTestCase):
    def setUp(self):
        super(EmbeddedSignaturesTestCase, self).setUp()

        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

    def tearDown(self):
        self.document_type.delete()
        super(EmbeddedSignaturesTestCase, self).tearDown()

    def test_unsigned_document_version_method(self):
        TEST_UNSIGNED_DOCUMENT_COUNT = 3
        TEST_SIGNED_DOCUMENT_COUNT = 3

        for count in range(TEST_UNSIGNED_DOCUMENT_COUNT):
            with open(TEST_DOCUMENT_PATH) as file_object:
                self.document_type.new_document(
                    file_object=file_object
                )

        for count in range(TEST_SIGNED_DOCUMENT_COUNT):
            with open(TEST_SIGNED_DOCUMENT_PATH) as file_object:
                self.document_type.new_document(
                    file_object=file_object
                )

        self.assertEqual(
            EmbeddedSignature.objects.unsigned_document_versions().count(),
            TEST_UNSIGNED_DOCUMENT_COUNT
        )

    def test_task_verify_missing_embedded_signature(self):
        # Silence converter logging
        logging.getLogger('converter.backends').setLevel(logging.CRITICAL)

        old_hooks = DocumentVersion._post_save_hooks

        DocumentVersion._post_save_hooks = {}

        TEST_UNSIGNED_DOCUMENT_COUNT = 4
        TEST_SIGNED_DOCUMENT_COUNT = 2

        for count in range(TEST_UNSIGNED_DOCUMENT_COUNT):
            with open(TEST_DOCUMENT_PATH) as file_object:
                self.document_type.new_document(
                    file_object=file_object
                )

        for count in range(TEST_SIGNED_DOCUMENT_COUNT):
            with open(TEST_SIGNED_DOCUMENT_PATH) as file_object:
                self.document_type.new_document(
                    file_object=file_object
                )

        self.assertEqual(
            EmbeddedSignature.objects.unsigned_document_versions().count(),
            TEST_UNSIGNED_DOCUMENT_COUNT + TEST_SIGNED_DOCUMENT_COUNT
        )

        DocumentVersion._post_save_hooks = old_hooks

        task_verify_missing_embedded_signature.delay()

        self.assertEqual(
            EmbeddedSignature.objects.unsigned_document_versions().count(),
            TEST_UNSIGNED_DOCUMENT_COUNT
        )

    def test_signing(self):
        key = Key.objects.create(key_data=TEST_KEY_DATA)

        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with document.latest_version.open() as file_object:
            file_object.seek(0, 2)
            original_size = file_object.tell()
            file_object.seek(0)
            original_hash = hashlib.sha256(file_object.read()).hexdigest()

        new_version = EmbeddedSignature.objects.sign_document_version(
            document_version=document.latest_version, key=key,
            passphrase=TEST_KEY_PASSPHRASE
        )

        self.assertEqual(EmbeddedSignature.objects.count(), 1)

        with new_version.open() as file_object:
            file_object.seek(0, 2)
            new_size = file_object.tell()
            file_object.seek(0)
            new_hash = hashlib.sha256(file_object.read()).hexdigest()

        self.assertEqual(original_size, new_size)
        self.assertEqual(original_hash, new_hash)
