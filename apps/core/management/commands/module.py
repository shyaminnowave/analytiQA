import logging
from django.core.management.base import BaseCommand, CommandError
from apps.core.models import TestCaseModel, Module
from apps.core.utlity import get_testcase_module

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    help = 'Command to Add Module to Testcases'

    def handle(self, *args, **options):
        try:
            testcases = TestCaseModel.objects.all()
            lst = []
            for testcase in testcases:
                if not testcase.module:
                    module = get_testcase_module(testcase.name)
                    instance, created = Module.objects.get_or_create(name=module)
                    testcase.module = instance
                    lst.append(testcase)
            TestCaseModel.objects.bulk_update(lst, fields=['module'])
        except Exception as e:
            logging.error(e)



