from django.contrib.contenttypes.models import ContentType
from openpyxl import load_workbook
from apps.core.models import (
    TestCaseModel,
    TestCaseChoices,
    TestCaseStep,
    Tag
)
from apps.core.utlity import QuerySetEntry
from abc import ABC, abstractmethod
from django.db.models import Model
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.db import transaction
from apps.general.models import Notification


class FileFactory(ABC):

    @abstractmethod
    def import_data(self):
        pass

class ExcelFileFactory(FileFactory):
    """Base factory class to handle Excel file operations."""

    def __init__(self, file, request):
        self.response_format = {
            "status": True,
            "status_code": HTTP_200_OK,
            "data": "",
            "message": ""
        }
        self.file = file
        self.request = request

    def _init_workbook(self):
        """Initialize the workbook and return the active sheet."""
        workbook = load_workbook(self.file)
        return workbook.active

    def import_data(self):
        pass

class TestCaseExl(ExcelFileFactory):

    def __init__(self, file, request):
        super(TestCaseExl, self).__init__(file, request)
        self.ws = self._init_workbook()

    def get_tag(self, tags):
        _ins = []
        for tg in tags:
            tag_instance, created = Tag.objects.get_or_create(name=tg)
            _ins.append(tag_instance)
        return _ins
    
    def _build_error_response(self, error):
        self.response_format.update({
            "status": False,
            "status_code": HTTP_400_BAD_REQUEST,
            "message": str(error),
        })
        return self.response_format

    def _build_success_response(self, message):
        self.response_format.update({
            "data": "Success",
            "message": message,
        })
        return self.response_format


    def import_data(self):
        """
        Import TestCase and Its Related Data from the Excel
        """
        testcase_list = set(TestCaseModel.objects.values_list('jira_id', flat=True))
        testcases_with_tags = []
        tests = []
        _step = dict()
        status = {
            "To Do": "todo",
            "Completed": "completed",
            "Ongoing": "ongoing"
        }
        types = {
            "Performance": "performance",
            "Soak": "soak",
            "Smoke": "smoke"
        }
        priority = {
            "Class 1": "class_1",
            "Class 2": "class_2",
            "Class 3": "class_3"
        }
        try:
            for row in self.ws.iter_rows(min_row=2, values_only=True):
                print('one', row[0])
                jira_id = str(row[0]).split("-")[1] if row[0] else None
                if row[0] and int(jira_id) not in testcase_list:
                    tag_names = [tag.strip() for tag in row[6].split(",")] if row[6] else []
                    _data = {
                        "jira_id": int(jira_id),
                        "name": row[1],
                        "summary": row[1],
                        "description": row[1],
                        "priority": priority.get(row[3], 'class_3'),
                        "testcase_type": types.get(row[4], 'performance'),
                        "status": status.get(row[5], 'todo'),
                        "created_by": self.request.user,
                        "steps": {}
                    }
                    tests.append(_data)
                    testcases_with_tags.append({int(str(row[0]).split("-")[1]): tag_names})
                    if row[0] and row[9]:
                        _step[int(row[9])] = {
                            "step_action": row[10],
                            "step_data": row[11],
                            "expected_result": row[12]
                        }
                        tests[-1]["steps"].update(_step)
                elif row[0] is None and row[9] is not None:
                    if _step:
                        _step[int(row[9])] = {
                            "step_action": row[10],
                            "step_data": row[11],
                            "expected_result": row[12]
                        }
                        tests[-1]["steps"].update(_step) if tests[-1]["steps"] else None
                        _step = dict()
            if tests:
                QuerySetEntry.bulk_create_entries(TestCaseModel, [TestCaseModel(**i) for i in tests])
                for i in testcases_with_tags:
                    for instance, tag in i.items():
                        _instance = TestCaseModel.objects.get(jira_id=instance)
                        tags = self.get_tag(tag)
                        _instance.tags.set(tags)
                Notification.objects.create(
                    message=f"Testcases Uploaded Successfully!",
                    user=self.request.user if self.request.user else None,
                    assigned_to=self.request.user if self.request.user else None,
                    content_type=ContentType.objects.get_for_model(TestCaseModel),
                    status=True
                )
            else:
                return self._build_success_response("TestCases Already Present in the DataBase")
        except Exception as e:
            Notification.objects.create(
                message=f"Testcases Uploaded Failed!",
                user=self.request.user if self.request.user else None,
                assigned_to=self.request.user if self.request.user else None,
                content_type=ContentType.objects.get_for_model(TestCaseModel),
                status=False
            )
            return self._build_error_response(e)
        return self._build_success_response("TestCase Uploaded Successfully")

