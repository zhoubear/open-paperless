from __future__ import unicode_literals

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from formtools.wizard.views import SessionWizardView

from common.mixins import ViewPermissionCheckMixin
from documents.forms import DocumentTypeSelectForm
from metadata.forms import DocumentMetadataFormSet
from tags.forms import TagMultipleSelectionForm

from .literals import STEP_DOCUMENT_TYPE, STEP_METADATA, STEP_TAGS
from .models import InteractiveSource


def has_metadata_types(wizard):
    """
    Skip the 2nd step if document type has no associated metadata
    """

    cleaned_data = wizard.get_cleaned_data_for_step(STEP_DOCUMENT_TYPE) or {}

    document_type = cleaned_data.get('document_type')

    if document_type:
        return document_type.metadata.exists()


class DocumentCreateWizard(ViewPermissionCheckMixin, SessionWizardView):
    condition_dict = {STEP_METADATA: has_metadata_types}
    extra_context = {}
    form_list = (
        DocumentTypeSelectForm, DocumentMetadataFormSet,
        TagMultipleSelectionForm
    )
    form_titles = {
        DocumentTypeSelectForm: _('Step 1 of 3: Select document type'),
        DocumentMetadataFormSet: _('Step 2 of 3: Enter document metadata'),
        TagMultipleSelectionForm: _('Step 3 of 3: Select tags'),
    }
    template_name = 'appearance/generic_wizard.html'

    def dispatch(self, request, *args, **kwargs):
        if not InteractiveSource.objects.filter(enabled=True).exists():
            messages.error(
                request,
                _(
                    'No interactive document sources have been defined or '
                    'none have been enabled, create one before proceeding.'
                )
            )
            return HttpResponseRedirect(reverse('sources:setup_source_list'))

        return super(
            DocumentCreateWizard, self
        ).dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super(
            DocumentCreateWizard, self
        ).get_context_data(form=form, **kwargs)

        context.update({
            'step_title': self.form_titles[form.__class__],
            'submit_label': _('Next step'),
            'submit_icon': 'fa fa-arrow-right',
            'title': _('Document upload wizard'),
        })
        return context

    def get_form_initial(self, step):
        if step == STEP_METADATA:
            initial = []

            for document_type_metadata_type in self.get_cleaned_data_for_step(STEP_DOCUMENT_TYPE)['document_type'].metadata.all():
                initial.append(
                    {
                        'document_type': self.get_cleaned_data_for_step(STEP_DOCUMENT_TYPE)['document_type'],
                        'metadata_type': document_type_metadata_type.metadata_type,
                    }
                )

            return initial
        return self.initial_dict.get(step, {})

    def get_form_kwargs(self, step):
        # Tags form needs the user instance to determine which tags to
        # display
        if step == STEP_DOCUMENT_TYPE:
            return {'user': self.request.user}

        if step == STEP_TAGS:
            return {
                'help_text': _('Tags to be attached.'),
                'user': self.request.user
            }

        return {}

    def done(self, *args, **kwargs):
        query_dict = {}

        try:
            query_dict['document_type_id'] = self.get_cleaned_data_for_step(STEP_DOCUMENT_TYPE)['document_type'].pk
        except AttributeError:
            pass

        try:
            for identifier, metadata in enumerate(self.get_cleaned_data_for_step(STEP_METADATA)):
                if metadata.get('update'):
                    query_dict['metadata%s_id' % identifier] = metadata['id']
                    query_dict['metadata%s_value' % identifier] = metadata['value']
        except TypeError:
            pass

        try:
            query_dict['tags'] = ([force_text(tag.pk) for tag in self.get_cleaned_data_for_step(STEP_TAGS)['tags']])

        except AttributeError:
            pass

        url = '?'.join(
            [
                reverse('sources:upload_interactive'),
                urlencode(query_dict, doseq=True)
            ]
        )
        return HttpResponseRedirect(url)
