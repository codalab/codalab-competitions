from django.conf import settings

from codalab import settings as codalab_settings


def app_version_proc(request):
    "A context processor that provides 'app_version'."
    return {
        'CODALAB_VERSION': settings.CODALAB_VERSION,
    }


def common_settings(request):
    """A context processor that returns dev settings"""
    return {
        'SINGLE_COMPETITION_VIEW_PK': settings.SINGLE_COMPETITION_VIEW_PK,
        'CUSTOM_HEADER_LOGO': settings.CUSTOM_HEADER_LOGO,
        'compile_less': codalab_settings.COMPILE_LESS,
        'local_mathjax': codalab_settings.LOCAL_MATHJAX,
        'local_ace_editor': codalab_settings.LOCAL_ACE_EDITOR,
        'is_dev': codalab_settings.IS_DEV,
        'USE_AWS': codalab_settings.USE_AWS,

        # Just get the base of the URL
        'CHAHUB_URL': '//{}'.format(settings.CHAHUB_API_URL.split("//")[-1].split("/")[0].split('?')[0]),
        'CHAHUB_PRODUCER_ID': settings.CHAHUB_PRODUCER_ID,
        'CODALAB_SITE_DOMAIN': codalab_settings.CODALAB_SITE_DOMAIN,
    }
