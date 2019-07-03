import hashlib
import json

import requests
from django.contrib import messages
from django.contrib.sites.models import Site
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template import Context
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import get_template

from codalab import settings
from .models import NewsletterUser, Newsletter
from .forms import NewsletterUserSignUpForm, NewsletterForm


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


def newsletter_create(request):
    form = NewsletterForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        newsletter = Newsletter.objects.get(id=instance.id)
        if newsletter.status == 'Draft':
            subject = newsletter.subject
            body = newsletter.body
            from_email = settings.DEFAULT_FROM_EMAIL
            for user in NewsletterUser.objects.all():
                print([user.email])
                send_mail(subject=subject, from_email=from_email, recipient_list=[user.email], message=body,
                          fail_silently=False)
            newsletter.save()
            messages.success(request, 'Saved newsletter as draft',
                             'alert alert-success alert-dismissible')

        if newsletter.status == 'Published':
            newsletter.save()
            messages.success(request, 'Publishing newsletter',
                             'alert alert-success alert-dismissible')

    context = {
        'form': form,
    }

    template = "newsletter/create_newsletter.html"
    return render(request, template, context)


def newsletter_index(request):
    newsletters = Newsletter.objects.all()

    paginator = Paginator(newsletters, 2)
    page = request.GET.get('page')

    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    index = items.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]

    context = {
        "items": items,
        "page_range": page_range,
    }

    template = 'newsletter/newsletter_index.html'
    return render(request, template, context)


def newsletter_detail(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)

    context = {
        'newsletter': newsletter,
    }

    template = 'newsletter/newsletter_detail.html'
    return render(request, template, context)


def newsletter_edit(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)

        if form.is_valid():
            newsletter = form.save()

            if newsletter.status == 'Published':
                subject = newsletter.subject
                body = newsletter.body
                from_email = settings.DEFAULT_FROM_EMAIL
                for user in NewsletterUser.objects.all():
                    send_mail(subject=subject, from_email=from_email, recipient_list=[user.email], message=body,
                              fail_silently=False)
                newsletter.save()
                messages.success(request, 'Your newsletter has been published!',
                                 'alert alert-success alert-dismissible')

            return redirect('newsletter:newsletter_detail', pk=newsletter.pk)

    else:
        form = NewsletterForm(instance=newsletter)

    context = {
        'form': form,
    }

    template = 'newsletter/create_newsletter.html'
    return render(request, template, context)


def newsletter_delete(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)

        if form.is_valid():
            newsletter.delete()
            return redirect('newsletter:newsletter_index')

    else:
        form = NewsletterForm(instance=newsletter)

    context = {
        'form': form,
    }

    template = 'newsletter/delete_newsletter.html'
    return render(request, template, context)
