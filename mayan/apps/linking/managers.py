from django.db import models


class SmartLinkManager(models.Manager):
    def get_for(self, document):
        return self.filter(
            document_types=document.document_type, enabled=True
        )
