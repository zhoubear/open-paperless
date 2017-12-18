from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

namespace = Namespace(name='mirroring', label=_('Mirroring'))

setting_document_lookup_cache_timeout = namespace.add_setting(
    global_name='MIRRORING_DOCUMENT_CACHE_LOOKUP_TIMEOUT', default=10,
    help_text=_('Time in seconds to cache the path lookup to a document.'),
)
setting_node_lookup_cache_timeout = namespace.add_setting(
    global_name='MIRRORING_NODE_CACHE_LOOKUP_TIMEOUT', default=10,
    help_text=_('Time in seconds to cache the path lookup to an index node.'),
)
