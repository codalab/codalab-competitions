from django.conf import settings
from codalab import settings as codalab_settings


def app_version_proc(request):
    "A context processor that provides 'app_version'."
    return {
        'app_version': settings.CODALAB_VERSION,
        'last_commit': settings.CODALAB_LAST_COMMIT
    }

def common_settings(request):
    "A context processor that returns dev settings"
    return {
        'compile_less': codalab_settings.COMPILE_LESS
    }
