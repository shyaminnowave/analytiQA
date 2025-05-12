import logging
from celery import shared_task
from django.core import mail
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

@shared_task
def send_verification_mail(email, token):
    try:
        html_template = None
        if email and token:
            html_template = render_to_string(
                'email.html',
                context={
                    "company": "Innowave GDU",
                    "email": email,
                    "token": token,
                }
            )
        with mail.get_connection() as connection:
            instance = mail.EmailMultiAlternatives(
                subject="Account Activation Mail",
                from_email=settings.EMAIL_HOST_USER,
                body='',
                to=[email,],
                connection=connection,
            )
            instance.attach_alternative(html_template, "text/html")
            instance.send()
            print("Email sent successfully")
    except Exception as e:
        logger.error(str(e))

