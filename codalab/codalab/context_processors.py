from django.conf import settings

def app_version_proc(request):
    "A context processor that provides 'app_version'."
    return {
        'app_version': settings.CODALAB_VERSION,
        'last_commit': settings.CODALAB_LAST_COMMIT
    }