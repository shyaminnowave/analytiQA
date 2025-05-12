import logging
from celery import shared_task

from apps.account.models import Account
from apps.core.excel import TestCaseExl


logger = logging.getLogger(__name__)

@shared_task
def process_excel(file, user):
    try:
        user = Account.objects.get(email=user)
        instance = TestCaseExl(
            file=file,
            user=user,
        ).import_data()
        return True
    except Exception as e:
        logger.error(str(e))
        return False