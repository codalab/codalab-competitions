from allauth.socialaccount import providers


def socialaccount(request):
    return {
        "socialaccount": {
            'providers': providers.registry.get_list()
        }
    }
