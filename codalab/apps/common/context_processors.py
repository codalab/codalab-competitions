from django.conf import settings

def app_version_proc(request):
    "A context processor that provides 'app_version'."
    print "Running context processor: " + settings.CODALAB_VERSION
    return {
        'app_version': settings.CODALAB_VERSION
    }