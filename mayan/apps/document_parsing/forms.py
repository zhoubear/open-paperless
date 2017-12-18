from __future__ import unicode_literals

from django import forms
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext

from acls.models import AccessControlList
from common.widgets import TextAreaDiv
from documents.models import DocumentType

from .models import DocumentPageContent
from .permissions import permission_parse_document


class DocumentContentForm(forms.Form):
    """
    Form that concatenates all of a document pages' text content into a
    single textarea widget
    """
    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('instance', None)
        super(DocumentContentForm, self).__init__(*args, **kwargs)
        content = []
        self.fields['contents'].initial = ''
        try:
            document_pages = self.document.pages.all()
        except AttributeError:
            document_pages = []

        for page in document_pages:
            try:
                page_content = page.content.content
            except DocumentPageContent.DoesNotExist:
                pass
            else:
                content.append(conditional_escape(force_text(page_content)))
                content.append(
                    '\n\n\n<hr/><div class="document-page-content-divider">- %s -</div><hr/>\n\n\n' % (
                        ugettext(
                            'Page %(page_number)d'
                        ) % {'page_number': page.page_number}
                    )
                )

        self.fields['contents'].initial = mark_safe(''.join(content))

    contents = forms.CharField(
        label=_('Contents'),
        widget=TextAreaDiv(
            attrs={
                'class': 'text_area_div full-height',
                'data-height-difference': 360
            }
        )
    )


class DocumentTypeSelectForm(forms.Form):
    document_type = forms.ModelChoiceField(
        queryset=DocumentType.objects.none(), label=('Document type')
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(DocumentTypeSelectForm, self).__init__(*args, **kwargs)
        queryset = AccessControlList.objects.filter_by_access(
            permission=permission_parse_document,
            queryset=DocumentType.objects.all(), user=user,
        )
        self.fields['document_type'].queryset = queryset
