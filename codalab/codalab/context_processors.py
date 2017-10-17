from django.conf import settings

from apps.customizer.models import Configuration
from apps.web.models import Competition
from codalab import settings as codalab_settings


def app_version_proc(request):
    "A context processor that provides 'app_version'."
    return {
        'CODALAB_VERSION': settings.CODALAB_VERSION,
    }


def common_settings(request):
    """A context processor that returns dev settings"""
    context = {
        'CUSTOM_HEADER_LOGO': settings.CUSTOM_HEADER_LOGO,
        'compile_less': codalab_settings.COMPILE_LESS,
        'local_mathjax': codalab_settings.LOCAL_MATHJAX,
        'local_ace_editor': codalab_settings.LOCAL_ACE_EDITOR,
        'is_dev': codalab_settings.IS_DEV,
        'USE_AWS': codalab_settings.USE_AWS,
    }

    if settings.SINGLE_COMPETITION_VIEW_PK:
        context['SINGLE_COMPETITION_MODE'] = True

    return context
