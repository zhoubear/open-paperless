from __future__ import unicode_literals

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from ..models import Message

from .literals import TEST_LABEL, TEST_MESSAGE


class MOTDTestCase(TestCase):
    def setUp(self):
        self.motd = Message.objects.create(
            label=TEST_LABEL, message=TEST_MESSAGE
        )

    def test_basic(self):
        queryset = Message.objects.get_for_now()

        self.assertEqual(queryset.exists(), True)

    def test_start_datetime(self):
        self.motd.start_datetime = timezone.now() - timedelta(days=1)
        self.motd.save()

        queryset = Message.objects.get_for_now()

        self.assertEqual(queryset.first(), self.motd)

    def test_end_datetime(self):
        self.motd.start_datetime = timezone.now() - timedelta(days=2)
        self.motd.end_datetime = timezone.now() - timedelta(days=1)
        self.motd.save()

        queryset = Message.objects.get_for_now()

        self.assertEqual(queryset.exists(), False)

    def test_enable(self):
        self.motd.enabled = False
        self.motd.save()

        queryset = Message.objects.get_for_now()

        self.assertEqual(queryset.exists(), False)
