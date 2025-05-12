import re
import json
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
from apps.stb.models import Language, NatCo, STBManufacture, NatcoRelease
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from django.db.models import Max
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from apps.core.managers import TestCaseManager
from django.contrib import admin
from django.core import serializers
from ckeditor.fields import RichTextField


# Create your models here.

User = get_user_model()

# ------------------------ Choices Enum ------------------------


class PriorityChoice(models.TextChoices):
    CLASS_ONE = 'class_1', _('Class 1')
    CLASS_TWO = 'class_2', _('Class 2')
    CLASS_THREE = 'class_3', _('Class 3')


class StatusChoices(models.TextChoices):
    TODO = 'todo', _('Todo')
    ONGOING = 'ongoing', _('Ongoing')
    COMPLETED = 'completed', _('Completed')


class AutomationChoices(models.TextChoices):
    AUTOMATABLE = 'automatable', _('Automatable')
    NOT_AUTOMATABLE = 'not-automatable', _('Not-Automatable')
    IN_DEVELOPMENT = 'in-development', _('In-Development')
    REVIEW = 'review', _('Review')
    READY = 'ready', _('Ready')
    COMPLETE = StatusChoices.COMPLETED


class TestCaseChoices(models.TextChoices):

    PERFORMANCE = 'performance', _('Performance')
    SOAK = 'soak', _('Soak')
    SMOKE = 'smoke', _('Smoke')

# ----------------------------------------------------


class Tag(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class TestCaseScript(TimeStampedModel):

    testcase = models.ForeignKey('TestCaseModel', on_delete=models.SET_NULL, blank=True, null=True,
                                 related_name='testcase_script')
    script_name = models.CharField(max_length=200, default='',)
    script_location = models.URLField(max_length=400)
    script_type = models.CharField(choices=TestCaseChoices.choices, max_length=20)
    natCo = models.ForeignKey(NatCo, on_delete=models.SET_NULL, null=True, blank=True, related_name='natCo_script')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='script_language')
    device = models.ForeignKey(STBManufacture, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='device_supported')
    developed_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=True, null=True,
                                     related_name='script_developed', to_field='email')
    reviewed_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name='script_reviewed', to_field='email')
    modified_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name='script_modified', to_field='email')
    description = models.TextField(default='')

    def __str__(self):
        return f"{self.testcase.id} - {self.testcase.name}: {self.script_name}"

    class Meta:
        verbose_name = 'TestCase Script'
        verbose_name_plural = 'TestCase Script'

    def save(self, **kwargs):
        if self.testcase:
            instance = TestCaseModel.objects.get(id=self.testcase.id)
            self.script_type = instance.testcase_type
        super().save(**kwargs)

class TestCaseModel(TimeStampedModel):

    jira_id = models.IntegerField(_("Jira Id"), unique=True, help_text="Jira Id", blank=True, null=True)
    name = models.CharField(_("Test Report Name"), max_length=255,
                            help_text="Please Enter the TestCase Name")
    priority = models.CharField(max_length=20, choices=PriorityChoice.choices, default=PriorityChoice.CLASS_THREE,
                                blank=True, null=True)
    summary = models.TextField(_("Jira Summary"), default='')
    description = RichTextField(default='', help_text=(_("Text Description")))
    testcase_type = models.CharField(max_length=20, choices=TestCaseChoices.choices,  default=TestCaseChoices.SMOKE)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.TODO)
    automation_status = models.CharField(max_length=100, choices=AutomationChoices.choices,
                                         default=AutomationChoices.NOT_AUTOMATABLE)
    tags = models.ManyToManyField(Tag, blank=True)
    comments = GenericRelation("Comment", related_name='core')
    steps = models.JSONField(default="", blank=True, null=True, help_text=(_('This is a Field to store all the Step Related to TestCase')))
    reporter = models.CharField(max_length=200, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                   to_field='email', related_name='user_testcase')
    assigned = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                 to_field="email", related_name="assigned_testcase"
                                 )
    objects = TestCaseManager()

    class Meta:
        verbose_name = 'TestCase'
        verbose_name_plural = 'TestCases'
        ordering = ['-id', ]
        permissions = (
            ('can_change_status_to_review', "Can Change Status to Review"),
            ('can_change_status_to_ready', "Can Change Status to Ready")
        )

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self) -> str:
        return '%s' % self.name

    @admin.display(description="Jira Id")
    def get_jira_id(self) -> str:
        return 'TTVTM-%s' % self.jira_id
    
    def get_status(self) -> str:
        return '%s' % self.status

    def get_short_descript(self) -> str:
        return "%s" % self.description

    def save(self, **kwargs):
        if not self.pk:
            get_current_id = TestCaseModel.objects.aggregate(max_id=Max('id'))['max_id']
            if get_current_id is None:
                self.id = 13000
            else:
                self.id = get_current_id + 1
        super().save(**kwargs)


class TestCaseHistoryModel(TimeStampedModel):

    class Meta:
        verbose_name = "TestCase History"

    testcase = models.ForeignKey(TestCaseModel, on_delete=models.CASCADE, blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PriorityChoice.choices, default=PriorityChoice.CLASS_THREE,
                                blank=True, null=True)
    testcase_type = models.CharField(max_length=20, choices=TestCaseChoices.choices,  default=TestCaseChoices.SMOKE)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.TODO)
    automation_status = models.CharField(max_length=100, choices=AutomationChoices.choices,
                                         default=AutomationChoices.NOT_AUTOMATABLE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    change_reason = models.CharField(max_length=200, blank=True, null=True)
    changed_fields = models.JSONField(max_length=200, default='')
    other_changes = models.JSONField(default="", blank=True, null=True, help_text=(_('This is a Field to store all the Step Related to TestCase')))
    
    def __str__(self):
        return self.testcase.name
    
    def save_history(self, testcase, user, change_reason, changed_fields):
        self.testcase = testcase
        self.user = user
        self.priority = testcase.priority
        self.testcase_type = testcase.testcase_type
        self.status = testcase.status
        self.automation_status = testcase.automation_status
        self.change_reason = change_reason
        self.changed_fields = changed_fields
        array_result = serializers.serialize('json', [testcase], ensure_ascii=False)
        self.other_changes = json.loads(array_result[1:-1])
        self.save()
        return self.testcase.name
    
    class Meta:
        ordering = ('-created',)


class NatcoStatus(TimeStampedModel):

    class NatcoStatusChoice(models.TextChoices):
        AUTOMATABLE = AutomationChoices.AUTOMATABLE
        NOT_AUTOMATABLE = AutomationChoices.NOT_AUTOMATABLE
        IN_DEVELOPMENT = AutomationChoices.IN_DEVELOPMENT
        REVIEW = AutomationChoices.REVIEW
        READY = AutomationChoices.READY
        MANUAL = 'manual', _('Manual')

    natco = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    device = models.CharField(max_length=100, blank=True, null=True)
    test_case = models.ForeignKey(TestCaseModel, on_delete=models.CASCADE, related_name='natco_status')
    status = models.CharField(max_length=100, choices=NatcoStatusChoice.choices, default=NatcoStatusChoice.MANUAL)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_natcostatus', blank=True, null=True,
                             to_field='email')
    modified = models.ForeignKey(User, on_delete=models.CASCADE, related_name='natcostatus_modified', blank=True,
                                 null=True, to_field='email')
    applicable = models.BooleanField(default=False)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Natco Status'
        verbose_name_plural = 'Natco Status'
        ordering = ['-created']

    def __str__(self):
        return '%s' % self.test_case

    def save(self, **kwargs):
        status = self.status
        test_case = TestCaseModel.objects.filter(jira_id=self.test_case.jira_id).first()
        if status == 'in_development':
            test_case.automation_status = 'in-development'
        elif status == 'review':
            test_case.automation_status = 'review'
        elif status == 'ready':
            test_case.automation_status = 'ready'
        test_case.save()
        super(NatcoStatus, self).save(**kwargs)


class TestCaseStep(TimeStampedModel):

    testcase = models.ForeignKey(TestCaseModel, on_delete=models.CASCADE, related_name='test_steps', blank=True,
                                 null=True)
    step_number = models.IntegerField(_("step number"), blank=True, null=True)
    step_data = models.TextField(_('Testing Parameters'), blank=True, null=True)
    step_action = models.TextField(blank=True, null=True)
    expected_result = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.TODO)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "TestCase Step"
        verbose_name_plural = "TestCase Steps"


class ScriptIssue(TimeStampedModel):

    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        UNDER_REVIEW = 'under_review', _('Under Review')
        CLOSED = 'closed', _('Closed')

    script = models.ForeignKey(TestCaseScript, on_delete=models.CASCADE, related_name='scripts_issues', to_field='id', null=True,
                               blank=True)
    summary = models.TextField(default='')
    description = models.TextField(default='')
    result = models.CharField(max_length=255, default='')
    status = models.CharField(choices=Status.choices, default=Status.OPEN, max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='created_issues', to_field='email')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name='resolved_issues', to_field='email')
    comment = GenericRelation("Comment", related_name='issues_comment')

    def __str__(self):
        return self.summary

    class Meta:
        ordering = ('-created',)

    @classmethod
    def check_open_issues(cls, instance):
        _issues = cls.objects.filter(testcase=instance, status=cls.Status.OPEN).only('status')
        return True if _issues else False

    def save(self, **kwargs):
        if not self.id:
            get_current_id = ScriptIssue.objects.aggregate(max_id=Max('id'))['max_id']
            if get_current_id is None:
                self.id = 101
            else:
                self.id = get_current_id + 1
        super().save(**kwargs)


class Comment(TimeStampedModel):

    comments = RichTextField(default='')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='created_comments', to_field='email')

    def __str__(self):
        return f"{self.comments[:20]}..."


class TestCaseJobId(TimeStampedModel):

    job_id = models.CharField(max_length=255)
    testscript = models.ForeignKey(TestCaseScript, on_delete=models.CASCADE, related_name='job_id')
    comments = GenericRelation("Comment", related_name='job_comments')

    def __str__(self):
        return self.job_id
    
    
class TestPlan(TimeStampedModel):

    name = models.CharField(_("name"), max_length=255, help_text=(_('Name of TestPlan')))
    description = models.TextField(_("Description"))
    testcases = models.ManyToManyField(TestCaseModel, related_name='test_plan_tests')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = 'Test Plan'
        verbose_name_plural = 'Test Plans'

    def __str__(self):
        return self.name

    def testcase_count(self):
        return self.testcases.count()
