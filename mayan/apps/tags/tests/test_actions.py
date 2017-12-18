from __future__ import unicode_literals

from document_states.tests.test_actions import ActionTestCase

from ..models import Tag
from ..workflow_actions import AttachTagAction, RemoveTagAction

from .literals import TEST_TAG_COLOR, TEST_TAG_LABEL


class TagActionTestCase(ActionTestCase):
    def setUp(self):
        super(TagActionTestCase, self).setUp()
        self.tag = Tag.objects.create(
            color=TEST_TAG_COLOR, label=TEST_TAG_LABEL
        )

    def test_tag_attach_action(self):
        action = AttachTagAction(form_data={'tags': Tag.objects.all()})
        action.execute(context={'entry_log': self.entry_log})

        self.assertEqual(self.tag.documents.count(), 1)
        self.assertEqual(list(self.tag.documents.all()), [self.document])

    def test_tag_remove_action(self):
        self.tag.attach_to(document=self.document)

        action = RemoveTagAction(form_data={'tags': Tag.objects.all()})
        action.execute(context={'entry_log': self.entry_log})

        self.assertEqual(self.tag.documents.count(), 0)
