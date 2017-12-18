from __future__ import unicode_literals

from django.db import models


class DocumentIndexInstanceNodeManager(models.Manager):
    def get_for(self, document):
        return self.filter(documents=document)


class IndexManager(models.Manager):
    def index_document(self, document):
        for index in self.filter(enabled=True, document_types=document.document_type):
            index.index_document(document=document)

    def get_by_natural_key(self, name):
        return self.get(name=name)

    def rebuild(self):
        for index in self.all():
            index.rebuild()


class IndexInstanceNodeManager(models.Manager):
    def delete_empty(self):
        # Select leaf nodes only because .delete_empty() bubbles up
        for root_nodes in self.filter(parent=None):
            for index_instance_node in root_nodes.get_leafnodes():
                index_instance_node.delete_empty()

    def remove_document(self, document):
        for index_instance_node in self.filter(documents=document):
            index_instance_node.remove_document(document=document)
