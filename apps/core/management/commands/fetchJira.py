import logging
from django.core.management.base import BaseCommand, CommandError
from apps.core.models import TestCaseModel
from apps.core.utlity import get_jira_id

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    help = "Command to Extract Jira Id from Testcase"

    def handle(self, *args, **options):
        try:
            testcases = TestCaseModel.objects.all()
            lst = []
            for testcase in testcases:
                jira_id = get_jira_id(testcase.name)
                if jira_id:
                    testcase.jira_id = jira_id.split('-')[1]
                    lst.append(testcase)
            TestCaseModel.objects.bulk_update(lst, fields=['jira_id'])
        except Exception as e:
            logger.error(str(e))
