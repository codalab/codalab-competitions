import hashlib
import json

import requests
from django.contrib import messages
from django.contrib.sites.models import Site
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template

from codalab import settings
from .models import NewsletterUser
from .forms import NewsletterUserSignUpForm


def newsletter_signup(request):
    form = NewsletterUserSignUpForm(request.POST or None)

    if form.is_valid():
        instance = form.save(commit=False)
        if NewsletterUser.objects.filter(email=instance.email).exists():
            messages.warning(request, 'This email already signed up for newsletters',
                             'alert alert-warning alert-dismissible')
        else:
            context = {
                "site": Site.objects.get_current(),
                "user": request.user,
            }

            data = {
                "email_address": instance.email,
                "status": "subscribed",
            }

            requests.post(
                settings.MAILCHIMP_MEMBERS_ENDPOINT,
                auth=("", settings.MAILCHIMP_API_KEY),
                data=json.dumps(data)
            )

            instance.save()
            messages.success(request, 'You have been added to the Codalab newsletter',
                             'alert alert-success alert-dismissible')
            subject = "Thank you for joining the Codalab newsletter"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [instance.email]
            with open(settings.PROJECT_DIR + '/apps/newsletter/templates/newsletter/signup_email.txt') as f:
                signup_message = f.read()
            message = EmailMultiAlternatives(subject=subject, body=signup_message, from_email=from_email, to=to_email)
            context = Context(context)
            html_template = get_template('newsletter/signup_email.html').render(context)
            message.attach_alternative(html_template, 'text/html')
            message.send()

    context = {
        'form': form,
    }

    template = "newsletter/signup.html"
    return render(request, template, context)


def newsletter_unsubscribe(request):
    form = NewsletterUserSignUpForm(request.POST or None)

    if form.is_valid():
        instance = form.save(commit=False)
        if NewsletterUser.objects.filter(email=instance.email).exists():
            data = {
                "status": "unsubscribed",
            }

            user_hash = hashlib.md5(str.lower(instance.email.encode()))

            requests.patch(
                settings.MAILCHIMP_MEMBERS_ENDPOINT + '/' + user_hash.hexdigest(),
                auth=("", settings.MAILCHIMP_API_KEY),
                data=json.dumps(data)
            )

            NewsletterUser.objects.filter(email=instance.email).delete()
            messages.success(request, 'You have been removed from the Codalab newsletter',
                             'alert alert-success alert-dismissible')
            subject = "You have been unsubscribed from the Codalab newsletter"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [instance.email]
            with open(settings.PROJECT_DIR + '/apps/newsletter/templates/newsletter/unsubscribe_email.txt') as f:
                email_message = f.read()
            message = EmailMultiAlternatives(subject=subject, body=email_message, from_email=from_email, to=to_email)
            context = {
                "site": Site.objects.get_current(),
                "user": request.user,
            }
            context = Context(context)
            html_template = get_template('newsletter/unsubscribe_email.html').render(context)
            message.attach_alternative(html_template, 'text/html')
            message.send()

        else:
            messages.warning(request, 'Your email was not found. We cannot remove that email from the newsletter',
                             'alert alert-warning alert-dismissible')

    context = {
        'form': form,
    }

    template = "newsletter/unsubscribe.html"
    return render(request, template, context)
