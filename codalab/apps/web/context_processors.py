from django.conf import settings

def beta(request):
    return {'BETA' : settings.SHOW_BETA_FEATURES }