import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.account.models import LoginHistory
from django.db.models.signals import Signal
from django.core import mail
from django.conf import settings
from apps.account.token import user_token_generator
from apps.account.tasks import send_verification_mail

User = get_user_model()
user_token_login = Signal()
user_token_logout = Signal()

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    try:
        ip = get_client_ip(request)
        LoginHistory.objects.create(
            user=user,
            ip=ip,
            user_agent=request.META.get('HTTP_USER_AGENT'),
            is_login=True
        )
    except Exception as e:
        logger.error(str(e))


@receiver(user_logged_out)
def post_logout(sender, user, request, **kwargs):
    try:
        if user:
            ip = get_client_ip(request)
            LoginHistory.objects.create(
                user=user,
                ip=ip,
                user_agent=request.META.get('HTTP_USER_AGENT'),
                is_login=False
            )
    except Exception as e:
        logger.error(str(e))


@receiver(user_token_login)
def token_login(sender, user, request, **kwargs):
    try:
        ip = get_client_ip(request)
        LoginHistory.objects.create(
            user=user,
            ip=ip,
            user_agent=request.META.get('HTTP_USER_AGENT'),
            is_login=True
        )
    except Exception as e:
        logger.error(str(e))


@receiver(user_token_logout)
def token_logout(sender, user, request, **kwargs):
    try:
        if user:
            ip = get_client_ip(request)
            LoginHistory.objects.create(
                user=user,
                ip=ip,
                user_agent=request.META.get('HTTP_USER_AGENT'),
                is_login=False
            )
    except Exception as e:
        logger.error(str(e))


@receiver(post_save, sender=User)
def send_mail(sender, instance, created, **kwargs):
    if created:
        email = instance.email if instance.email else None
        token = user_token_generator.make_token(instance)
        try:
            send_verification_mail.delay(email, token)
        except Exception as e:
            logger.error(str(e))
