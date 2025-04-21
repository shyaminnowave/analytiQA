from django.test import TestCase
from apps.core.models import TestCaseModel, NatcoStatus, AutomationChoices, StatusChoices, TestCaseScript, ScriptIssue
from apps.stb.models import STBManufacture, Language, Natco, NactoManufacturesLanguage
from rest_framework.test import APIClient as Client
from django.db.models import Max
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.core.models import NatcoStatus
from rest_framework import status
from apps.core.signals import script_natcostatus
# Create your tests here.



class TestTestCaseScriptModel(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = get_user_model().objects.create(
            email='developer@example.com',
            password='password123',
        )
        
        cls.reviewer = get_user_model().objects.create(
            email='reviewer@example.com',
            password='password123',
        )
        
        cls.testcase = TestCaseModel.objects.create(
            test_name='Sample Test Case'
        )

        cls.natco = Natco.objects.create(
            country='United States',
            natco='USA'
        )

        cls.language = Language.objects.create(
            language_name='English'
        )

        cls.device = STBManufacture.objects.create(
            name='STB Device'
        )

    def test_field_defaults(self):
        script = TestCaseScript.objects.create(
            testcase=self.testcase,
            script_name='Test Script',
            script_location='http://example.com/script',
            script_type='automated',
            natco=self.natco,
            language=self.language,
            device=self.device,
            developed_by=self.user,
            reviewed_by=self.reviewer,
            description='This is a test script.',
        )
        self.assertEqual(script.script_name, 'Test Script')
        self.assertEqual(script.script_type, 'automated')
        self.assertEqual(script.description, 'This is a test script.')


    def test_foreign_key_relationships(self):
        script = TestCaseScript.objects.create(
            testcase=self.testcase,
            script_name='Script with Relationships',
            script_location='http://example.com/script',
            script_type='manual',
            natco=self.natco,
            language=self.language,
            device=self.device,
            developed_by=self.user,
            reviewed_by=self.reviewer,
        )
        self.assertEqual(script.developed_by, self.user)
        self.assertEqual(script.reviewed_by, self.reviewer)
        self.assertEqual(script.testcase, self.testcase)


class TestNatcoStatusModel(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a test user
        cls.user = get_user_model().objects.create(
            email="testuser@example.com",
            password="password123"
        )

        # Create Languages
        cls.language1 = Language.objects.create(language_name="English")
        cls.language2 = Language.objects.create(language_name="German")

        # Create STB Manufactures
        cls.manufacture1 = STBManufacture.objects.create(name="Skyworth")
        cls.manufacture2 = STBManufacture.objects.create(name="Sei")

        # Create Natco with relationships
        cls.natco = Natco.objects.create(natco="TestNatco")
        cls.natco.language.add(cls.language1, cls.language2)
        cls.natco.manufacture.add(cls.manufacture1, cls.manufacture2)

    def setUp(self):
        # Disable the signal temporarily for setup
        post_save.disconnect(script_natcostatus, sender=TestCaseModel)

        # Create a test case model
        self.test_case = TestCaseModel.objects.create(
            test_name="Sample Test Case",
             # Trigger condition
        )

        # Reconnect the signal
        post_save.connect(script_natcostatus, sender=TestCaseModel)

    def test_natco_status_creation(self):
        # Save the test case model to trigger the signal
        self.test_case.automation_status = 'automatable'
        self.test_case.save()

        # Assert NatcoStatus records are created
        self.assertEqual(NatcoStatus.objects.count(), 4)  # 2 languages x 2 manufactures

        # Check details of the created NatcoStatus
        natco_statuses = NatcoStatus.objects.all()
        self.assertTrue(all(status.test_case == self.test_case for status in natco_statuses))


class TestTestCaseModel(TestCase):

    def test_create_test_case(self):
        test_case = TestCaseModel.objects.create(
            test_name="Test Case 1",
            summary="Summary",
            description="Description",
            status=StatusChoices.ONGOING,
            automation_status=AutomationChoices.IN_DEVELOPMENT,
        )

        self.assertEqual(test_case.test_name, "Test Case 1")
        self.assertEqual(test_case.summary, "Summary")
        self.assertEqual(test_case.description, "Description")
        self.assertEqual(test_case.status, StatusChoices.ONGOING)
        self.assertEqual(test_case.automation_status, AutomationChoices.IN_DEVELOPMENT)

    def test_default_values(self):
        test_case = TestCaseModel.objects.create(
            test_name="Test Case 2",
            summary="Summary 2",
            description="Description 2",
            automation_status=AutomationChoices.NOT_AUTOMATABLE
        )
        self.assertEqual(test_case.status, StatusChoices.TODO)  # default value


class TestScriptIssueModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user
        cls.user = get_user_model().objects.create(
            email="testuser@example.com",
            password="password123"
        )

        # Create a test case
        cls.test_case = TestCaseModel.objects.create(
            test_name="Test Case 1"
        )

        cls.natco = Natco.objects.create(natco="TestNatco")
        cls.language = Language.objects.create(language_name="English")
        cls.device = STBManufacture.objects.create(name="Skyworth")

        # Create a test script
        cls.test_script = TestCaseScript.objects.create(
            testcase=cls.test_case,
            script_name="Test Script 1",
            script_location="http://example.com/script1",
            script_type="automatable",
            natco=cls.natco,
            language=cls.language,
            device=cls.device,
            developed_by=cls.user
        )

    def test_auto_increment_id_on_create(self):
        # Create first ScriptIssue
        issue1 = ScriptIssue.objects.create(
            testcase=self.test_case,
            script_id=self.test_script,
            summary="Issue 1 Summary",
            description="Issue 1 Description",
            result="Failed",
            created_by=self.user
        )
        self.assertEqual(issue1.id, 101)  # First ID should start at 101

        # Create second ScriptIssue
        issue2 = ScriptIssue.objects.create(
            testcase=self.test_case,
            script_id=self.test_script,
            summary="Issue 2 Summary",
            description="Issue 2 Description",
            result="Failed",
            created_by=self.user
        )
        self.assertEqual(issue2.id, 102)  # ID should auto-increment

    def test_check_open_issues_returns_true(self):
        # Create an open issue
        ScriptIssue.objects.create(
            testcase=self.test_case,
            script_id=self.test_script,
            summary="Open Issue",
            description="An open issue",
            status=ScriptIssue.Status.OPEN,
            created_by=self.user
        )
        # Verify the check_open_issues method returns True
        self.assertTrue(ScriptIssue.check_open_issues(self.test_case))

    def test_check_open_issues_returns_false(self):
        # No issues created, check_open_issues should return False
        self.assertFalse(ScriptIssue.check_open_issues(self.test_case))

    def test_status_choices(self):
        # Create an issue with each status
        open_issue = ScriptIssue.objects.create(
            testcase=self.test_case,
            script_id=self.test_script,
            summary="Open Issue",
            description="An open issue",
            status=ScriptIssue.Status.OPEN,
            created_by=self.user
        )
        self.assertEqual(open_issue.status, ScriptIssue.Status.OPEN)

        review_issue = ScriptIssue.objects.create(
            testcase=self.test_case,
            script_id=self.test_script,
            summary="Review Issue",
            description="An issue under review",
            status=ScriptIssue.Status.UNDER_REVIEW,
            created_by=self.user
        )
        self.assertEqual(review_issue.status, ScriptIssue.Status.UNDER_REVIEW)

        closed_issue = ScriptIssue.objects.create(
            testcase=self.test_case,
            script_id=self.test_script,
            summary="Closed Issue",
            description="A closed issue",
            status=ScriptIssue.Status.CLOSED,
            created_by=self.user
        )
        self.assertEqual(closed_issue.status, ScriptIssue.Status.CLOSED)

    def test_save_sets_id_correctly(self):
        # Check current max ID
        max_id = ScriptIssue.objects.aggregate(max_id=Max('id'))['max_id']
        self.assertIsNone(max_id)

        # Create an issue
        issue = ScriptIssue.objects.create(
            testcase=self.test_case,
            script_id=self.test_script,
            summary="Test Issue",
            description="Testing ID auto-assignment",
            result="Pending",
            created_by=self.user
        )
        self.assertEqual(issue.id, 101)  # First issue should have ID 101

class TestNatcoList(TestCase):

    def setUp(self):
        self.client = Client()
        self.natco = Natco.objects.create(country='Poland', natco='PL')
        self.device = STBManufacture.objects.create(name="SDMC")
        self.language = Language.objects.create(language_name="English")
        self.data = NactoManufacturesLanguage.objects.create(
            natco=self.natco,
            device_name=self.device,
            language_name=self.language
        )
        self.test_case = TestCaseModel.objects.create(
            test_name="Test Case 1",
            summary="Summary",
            description="Description",
            status=StatusChoices.ONGOING,
            automation_status=AutomationChoices.IN_DEVELOPMENT,
        )

    def test_view_data(self):
        url = reverse('core:testcase-natco', kwargs={'id': self.test_case.id})
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response_data['count'], 1)

class TestNatcoStatus(TestCase):

    def setUp(self):
        self.client = Client()
        self.natco = Natco.objects.create(country='Poland', natco='PL')
        self.device = STBManufacture.objects.create(name="SDMC")
        self.language = Language.objects.create(language_name="English")
        self.data = NactoManufacturesLanguage.objects.create(
            natco=self.natco,
            device_name=self.device,
            language_name=self.language
        )
        self.test_case = TestCaseModel.objects.create(
            test_name="Test Case 1",
            summary="Summary",
            description="Description",
            status=StatusChoices.ONGOING,
            automation_status=AutomationChoices.IN_DEVELOPMENT,
        )
        self.url = reverse('core:natco-list')

    def test_view_data(self):
        response = self.client.get(self.url)
        response_data = response.json()
        self.assertEqual(response_data['count'], 1)

    def test_natco_status_update(self):
        data = {
            "status": NatcoStatus.NatcoStatusChoice.IN_DEVELOPMENT,
            "applicable": "False"
        }
        natco = NatcoStatus.objects.create(test_case=self.test_case,
                                           natco = self.natco, language=self.language, device=self.device,
                                           status=NatcoStatus.NatcoStatusChoice.NOT_AUTOMATABLE)
        url = reverse('core:natco-details', kwargs={'pk': natco.id})
        response = self.client.patch(url, data, content_type='application/json')
        testcase_instance = TestCaseModel.objects.get(id=self.test_case.id)
        self.assertEqual(testcase_instance.automation_status, 'in-development')
#
#
