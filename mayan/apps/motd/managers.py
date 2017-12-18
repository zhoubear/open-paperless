from django.db import models
from django.db.models import Q
from django.utils import timezone


class MessageManager(models.Manager):
    def get_for_now(self):
        now = timezone.now()
        return self.filter(enabled=True).filter(
            Q(start_datetime__isnull=True) | Q(start_datetime__lte=now)
        ).filter(Q(end_datetime__isnull=True) | Q(end_datetime__gte=now))
