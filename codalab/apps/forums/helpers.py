from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string


def send_mail(context_data=None, from_email=None, html_file=None, text_file=None, subject=None, to_email=None):
    from_email = from_email if from_email else settings.DEFAULT_FROM_EMAIL

    context_data["site"] = Site.objects.get_current()

    context = Context(context_data)
    text = render_to_string(text_file, context)
    html = render_to_string(html_file, context)

    message = EmailMultiAlternatives(subject, text, from_email, [to_email])
    message.attach_alternative(html, 'text/html')
    message.send()
