from django.shortcuts import render


def health(request):

    return render(request, "health/health.html")
