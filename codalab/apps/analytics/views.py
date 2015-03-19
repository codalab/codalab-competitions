from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render

from apps.web.models import Competition


User = get_user_model()


@login_required
def analytics_detail(request):
    if not request.user.is_staff:
        return HttpResponse(status=404)

    monthly_total_users_joined = {}
    for date in User.objects.all().dates('date_joined', 'month'):
        if date.year not in monthly_total_users_joined:
            monthly_total_users_joined[date.year] = {}
        users_joined_this_month = User.objects.filter(date_joined__month=date.month,
                                                      date_joined__year=date.year).aggregate(Count('pk'))
        monthly_total_users_joined[date.year][date.strftime("%B")] = users_joined_this_month['pk__count']

    return render(request, "analytics/analytics.html", {
        'registered_user_count': User.objects.all().count(),
        'competition_count': Competition.objects.all().count(),
        'competitions_published_count': Competition.objects.filter(published=True).count(),
        'monthly_total_users_joined': monthly_total_users_joined,
    })
