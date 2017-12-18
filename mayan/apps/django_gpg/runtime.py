from django.utils.module_loading import import_string

from .settings import setting_gpg_path

# TODO: This will become an setting option in 2.2
SETTING_GPG_BACKEND = 'django_gpg.classes.PythonGNUPGBackend'

gpg_backend = import_string(SETTING_GPG_BACKEND)(
    binary_path=setting_gpg_path.value
)
