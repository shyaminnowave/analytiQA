import re
import logging
from django.db import transaction
from rest_framework import serializers
from simple_history.utils import update_change_reason
from apps.account.models import Account
from apps.core.models import TestCaseModel, NatcoStatus, \
    TestCaseChoices, Comment, ScriptIssue, TestCaseScript, Tag, TestCaseHistoryModel, Module, TestcaseTypes
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from apps.core.utlity import generate_history_message, generate_changed_fields
from apps.general.utils import get_status_group
from apps.core.utlity import bulk_filter_update
# from apps.stb_tester.views import BaseAPI


logging = logging.getLogger(__name__)


class BulkFieldUpdateSerializer(serializers.Serializer):
    id_fields = serializers.ListField(child=serializers.IntegerField())
    field = serializers.CharField()

    def update_testcase_status(self, validated_data, instance=None):
        # _testcase = [TestCaseModel.objects.get(id=test_case) for test_case in validated_data.get('id_fields')]
        try:
            bulk_filter = bulk_filter_update(validated_data, context=self.context)
            if bulk_filter: return True
            else:
                return False
        except Exception as e:
            logging.error(str(e))
        # _status = validated_data.get('field', None)
        #
        # for _test in _testcase:
        #     _test.status = _status
        # instance = TestCaseModel.objects.bulk_update(_testcase, fields=['status'])
        # return True if instance else False

    def update_testcase_automation(self, validated_data, instance=None):
        _testcase = [TestCaseModel.objects.get(jira_id=test_case) for test_case in validated_data.get('id_fields')]
        _status = validated_data.get('field', None)
        for _test in _testcase:
            _test.automation_status = _status
        instance = TestCaseModel.objects.bulk_update(_testcase, fields=['automation_status'])
        return True if instance else False

    def update_natco_status(self, validated_data, instance=None):
        _natcos = [NatcoStatus.objects.get(id=i) for i in validated_data.get('id_fields')]
        _status = validated_data.get('field', None)
        for _natco in _natcos:
            _natco.status = _status
        instance = NatcoStatus.objects.bulk_update(_natcos, fields=['status'])
        return True if instance else False
    
    def update_applicable_status(self, validated_data, instance=None):
        _natCo = [NatcoStatus.objects.get(id=i) for i in validated_data.get("id_fields")]
        print('_natCo', _natCo)
        _applicable = validated_data.get('field', None)
        for _status in _natCo:
            _status.applicable = True if _applicable == 'True' else False
        instance = NatcoStatus.objects.bulk_update(_natCo, fields=["applicable"])
        return True if instance else False


class TestCaseSerializerList(serializers.ModelSerializer):

    class Meta:
        model = TestCaseModel
        fields = ('id', 'name', 'jira_id', 'priority', 'testcase_type',
                  'status', 'automation_status')

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['status'] = instance.status.capitalize()
        represent['testcase_type'] = instance.testcase_type.name.capitalize()
        return represent


class NatcoStatusSerializer(serializers.ModelSerializer):

    jira_id = serializers.IntegerField(read_only=True)
    summary = serializers.CharField(read_only=True)
    history_change_reason = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = NatcoStatus
        fields = ['id', 'natco', 'language', 'jira_id', 'summary', 'device', 'test_case', 'status', 'applicable', 'user',
                  'modified', 'history_change_reason']

    def __init__(self, *args, **kwargs):
        request = kwargs['context']['request'] if 'context' in kwargs and 'request' in kwargs['context'] else None
        resolve_match = getattr(request, 'resolver_match', None)
        if resolve_match.url_name == 'natco-details':
            fields = ['user', 'modified']
            self.Meta.fields.extend(fields)
        if resolve_match.url_name == 'testcase-natco':
            self.Meta.fields = ['id', 'natco', 'language', 'jira_id', 'summary', 'device', 'status', 'user',
                                'applicable', 'history_change_reason', 'modified']
        super(NatcoStatusSerializer, self).__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        history_change_reason = validated_data.get('history_change_reason', 'Natco Status Changed')
        instance = super().update(instance, validated_data)
        if history_change_reason:
            update_change_reason(instance, history_change_reason)
        return instance

    def to_representation(self, instance):
        represent = super(NatcoStatusSerializer, self).to_representation(instance)
        represent['test_case'] = instance.test_case.name
        represent['jira_id'] = instance.test_case.jira_id
        represent['summary'] = instance.test_case.summary if instance.test_case.summary else None
        represent['user'] = instance.user.fullname if instance.user else None
        represent['modified'] = instance.modified.fullname if instance.modified else None
        represent['applicable'] = "True" if instance.applicable else "False"
        return represent


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name')


class TestCaseSerializer(serializers.ModelSerializer):

    created = serializers.SerializerMethodField(required=False, read_only=True)
    modified = serializers.SerializerMethodField(required=False, read_only=True)
    # last_fifty_result = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = TestCaseModel
        fields = ('id', 'name', 'jira_id', 'summary', 'description', 'status', 'priority',
                  'automation_status', 'testcase_type', 'created', 'modified', 'steps', 'tags',
                  'created_by')

    def __init__(self, *args, **kwargs):
        request = kwargs['context']['request'] if 'context' in kwargs and 'request' in kwargs['context'] else None
        resolve_match = getattr(kwargs['context']['request'], 'resolver_match', None)
        if request and request.path == '/api/core/testcase':
            self.Meta.fields = ('id', 'name', 'summary', 'description', 'testcase_type', 'created', 'modified', 'tags',
                                'status', 'automation_status', 'steps')
        if resolve_match.url_name == 'testcase-details':
            self.Meta.fields = '__all__'
        super().__init__(*args, **kwargs)

    def validate_test_name(self, value):
        if value is None:
            raise serializers.ValidationError("Test Name Cannot be Empty")
        return value

    def get_created(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y %I:%M %p")

    def get_modified(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y %I:%M %p")

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        created_by = self.context['request'].user
        _instance= TestCaseModel.objects.create(created_by=created_by, **validated_data)
        _instance.tags.set(tags)
        return _instance

    def update(self, instance, validated_data):
        message = None
        history_change_reason = validated_data.get('history_change_reason', message)
        group = get_status_group(validated_data.get('automation_status', None))
        if validated_data.get('assigned') is None and instance.assigned: pass
        if group is not None and instance.automation_status != validated_data.get('automation_status'):
            validated_data['assigned'] = group.owner
        if history_change_reason is None:
            message = generate_history_message(instance, validated_data)
        try:
            testcase_history = TestCaseHistoryModel()
            fields = generate_changed_fields(instance, validated_data)
            testcase_history.save_history(instance, self.context['request'].user, change_reason=message if message else history_change_reason, changed_fields=fields)
        except Exception as e:
            logging.error(str(e))
        instance = super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        represent = super(TestCaseSerializer, self).to_representation(instance)
        represent['tags'] = [i.name for i in instance.tags.all()]
        represent['created_by'] = instance.reporter if instance.reporter else instance.created_by.fullname
        return represent

class StepsListSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestCaseModel
        fields = ("steps", )


class TestCaseStepSerializer(serializers.Serializer):

    step_number = serializers.IntegerField(read_only=True)
    step_action = serializers.CharField()
    step_data = serializers.CharField()
    expected_result = serializers.CharField()

    def update_step(self, validated_data):
        testcase_instance = TestCaseModel.objects.get(id=self.context["testcase"])
        testcase_instance.steps[self.context["step_id"]] = {key: value for key, value in validated_data.items()}
        testcase_instance.save()
        return True

    def delete_step(self):
        _steps = {}
        _key_id = 1
        testcase_instance = TestCaseModel.objects.get(id=self.context["testcase"])
        del testcase_instance.steps[self.context["step_id"]]
        for key, value in testcase_instance.steps.items():
            _steps[str(_key_id)] = value
            _key_id += 1
        testcase_instance.steps = _steps
        testcase_instance.save()
        return True

class ExcelUploadSerializer(serializers.Serializer):

    UPLOAD_TYPE_CHOICES = [
        ('testcase', _('TestCase')),
        ('report', _('Report'))
    ]

    uploadtype = serializers.ChoiceField(choices=UPLOAD_TYPE_CHOICES)
    file = serializers.FileField()

    def __init__(self, instance=None, data=..., **kwargs):
        resolved_match = getattr(kwargs['context']['request'], 'resolver_match', None)
        if resolved_match.url_name == 'get-excel':
            allowed_fields = ['uploadtype']
            self.fields = {field: self.fields[field] for field in allowed_fields if field in self.fields}
        super().__init__(instance, data, **kwargs)

    def to_representation(self, instance):
        """
        Modify the serialized data when responding to GET requests.
        """
        data = super().to_representation(instance)
        request = self.context.get("request")

        if request and request.method == "GET":
            return {"uploadtype": data["uploadtype"]}

        return data


class NatcoGraphAPISerializer(serializers.Serializer):
    natco = serializers.CharField(max_length=200, required=True)
    avg_load_time = serializers.DecimalField(max_digits=5, decimal_places=4, required=False)
    avg_cpu_load = serializers.DecimalField(max_digits=5, decimal_places=4, required=False)
    avg_ram_load = serializers.DecimalField(max_digits=5, decimal_places=4, required=False)

    def __init__(self, *args, **kwargs):
        request = kwargs['context']['request'] if 'context' in kwargs and 'request' in kwargs['context'] else None
        if request:
            if request.path.split('/')[-2] == 'load_time':
                self.fields = {
                    'natco': self.fields['natco'],
                    'avg_load_time': self.fields['avg_load_time']
                }
            elif request.path.split('/')[-2] == 'cpu_load':
                self.fields = {
                    'natco': self.fields['natco'],
                    'avg_cpu_load': self.fields['avg_cpu_load']
                }
            elif request.path.split('/')[-2] == 'ram_load':
                self.fields = {
                    'natco': self.fields['natco'],
                    'avg_ram_load': self.fields['avg_ram_load']
                }
        super().__init__(*args, **kwargs)


class MetricSerializer(serializers.Serializer):
    natco = serializers.CharField(max_length=10)
    builname = serializers.CharField(max_length=10)
    value = serializers.FloatField()


class TestCaseFilterSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=20)
    value = serializers.CharField(max_length=20)


class DistinctTestResultSerializer(serializers.Serializer):
    testcase = serializers.CharField()
    natco = serializers.CharField()
    cpu_usage = serializers.CharField()
    ram_usage = serializers.CharField()
    load_time = serializers.CharField()

    def get_min_cpu(self, obj):
        return obj['min_cpu']

    def get_min_ram(self, obj):
        return obj['min_ram']



class CommentSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(read_only=True)
    created = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'comments', 'created_by', 'created')

    def get_instance(self):
        _instance = {
            "ScriptIssue": ScriptIssue,
            "TestCaseModel": TestCaseModel
        }
        return _instance.get(self.context.get('instance'))

    def get_model_instance(self):
        model_instance = ContentType.objects.get_for_model(self.get_instance())
        return model_instance

    def get_object_instance(self, id=id):
        instance = get_object_or_404(self.get_instance(), pk=id)
        return instance

    def get_created(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y %I:%M %p")

    def account_instance(self, obj):
        if obj is not None:
            try:
                instance = Account.objects.get(email=obj)
                return instance.email
            except Account.DoesNotExist:
                return None
        return None

    def create(self, validated_data):
        object_id = self.context.get('object_id')
        obj_instance = self.get_object_instance(id=object_id)
        if obj_instance:
            cmd = Comment.objects.create(content_type=self.get_model_instance(), object_id=obj_instance.id,
                                         **validated_data)
            return cmd
        raise ScriptIssue.DoesNotExist("Object Does Not Exist")

    def update(self, instance, validated_data):
        if instance.created_by != validated_data.get('created_by'):
            raise serializers.ValidationError("You Cannot Edit Other Comments")
        if instance:
            instance.comments = validated_data.get('comments', instance.comments)
            instance.status = validated_data.get('status', instance.status)
            instance.resolved_by = validated_data.get('resolved_by', instance.resolved_by)
            instance.save()
        return instance


class IssueCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'comments', 'created_by', 'created']

    def get_created(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y %I:%M:%S %p")

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['created_by'] = instance.created_by.fullname
        return represent


class IssuesListSerializer(serializers.ModelSerializer):

    testcase = serializers.CharField(read_only=True)
    script = serializers.CharField(read_only=True)

    class Meta:
        model = ScriptIssue
        fields = ('id', 'testcase', 'script', 'status', 'created_by', 'resolved_by')

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['testcase'] = instance.script.testcase.name if instance.script else None
        represent['script'] = instance.script.script_name if instance.script else None
        represent['created_by'] = instance.created_by.fullname if instance.created_by else None
        represent['resolved_by'] = instance.resolved_by.fullname if instance.resolved_by else None
        return represent


class ScriptIssueList(serializers.ModelSerializer):

    class Meta:
        model = ScriptIssue
        fields = ('id', 'summary', 'status', 'result', 'created_by', 'resolved_by')

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['created_by'] = instance.created_by.fullname if instance.created_by else None
        represent['resolved_by'] = instance.resolved_by.fullname if instance.resolved_by else None
        return represent


class ScriptIssueSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(read_only=True)
    issues_comment = IssueCommentSerializer(many=True, read_only=True, source='comment.all')
    created = serializers.SerializerMethodField(read_only=True)
    modified = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        request = kwargs['context']['request'] if 'context' in kwargs and 'request' in kwargs['context'] else None
        resolve_match = getattr(request, 'resolver_match', None)
        if resolve_match.url_name == 'create-issue':
            allowed_fields = ['script', 'summary', 'description', 'result', 'created_by', 'status']
            self.fields = {field: self.fields[field] for field in allowed_fields if field in self.fields}
        else:
            self.Meta.fields = ['id', 'script', 'summary', 'description', 'status', 'issues_comment', 'created', 'result',
                                'modified', 'created_by', 'resolved_by']
        super(ScriptIssueSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = ScriptIssue
        fields = ['id', 'script', 'summary', 'description', 'status', 'issues_comment', 'created', 'modified', 'result',
                  'created_by', 'resolved_by']

    def get_account_instance(self, email):
        if email is not None:
            try:
                instance = Account.objects.get(email=email)
                return instance
            except Account.DoesNotExist:
                return None
        return None

    def get_created(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y %I:%M %p")

    def get_modified(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y %I:%M %p")

    def create(self, validated_data):
        resolved = validated_data.pop("resolved_by", None)
        issue = ScriptIssue.objects.create(**validated_data)
        return issue

    def update(self, instance, validated_data):
        if instance:
            instance.summary = validated_data.get('summary', instance.summary)
            instance.status = validated_data.get('status', instance.status)
            instance.resolved_by = self.get_account_instance(validated_data.get('resolved_by', instance.resolved_by))
            instance.description = validated_data.get('description', instance.description)
            instance.save()
        return instance

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['script'] = getattr(instance.script, 'script_name', None)
        # represent['created_by'] = getattr(instance.created_by, 'fullname', None)
        # represent['resolved_by'] = instance.resolved_by.fullname if instance.resolved_by else None
        return represent


class TestCaseScriptListSerializer(serializers.ModelSerializer):

    build_testcase = serializers.SerializerMethodField()

    class Meta:
        model = TestCaseScript
        fields = ('id', 'script_name', 'script_location', 'natCo', 'language', 'device', 'script_type', 
                  'build_testcase')

    def get_script_type(self, instance):
        if instance == 'performance':
            return 'Performance'
        elif instance == 'smoke':
            return 'Smoke'
        elif instance == 'soak':
            return 'Soak'
        return None
    
    def get_build_testcase(self, obj):
        return obj.get_testcase_name()


    def to_representation(self, instance):
        represent = super(TestCaseScriptListSerializer, self).to_representation(instance)
        represent['natCo'] = instance.natCo.natco if instance.natCo else None
        represent['language'] = instance.language.language_name if instance.language else None
        represent['device'] = instance.device.name if instance.device else None
        represent['script_type'] = instance.script_type.capitalize() if instance.script_type else None
        return represent


class TestcaseScriptSerializer(serializers.ModelSerializer):

    scripts_issues = ScriptIssueList(many=True, read_only=True)
    job_id  = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    job_ids = serializers.JSONField(read_only=True)
    created = serializers.SerializerMethodField(required=False, read_only=True)
    modified = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = TestCaseScript
        fields = '__all__'

    def get_created(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y %I:%M %p")

    def get_modified(self, obj):
        data = datetime.fromisoformat(str(obj.created))
        return data.strftime("%d-%m-%Y %I:%M %p")
    
    def to_representation(self, instance):
        represent = super().to_representation(instance)
        resolve_match = getattr(self.context['request'], 'resolver_match', None)
        represent['natCo'] = instance.natCo.natco if instance.natCo else None
        represent['language'] = instance.language.language_name if instance.language else None
        represent['device'] = instance.device.name if instance.device else None
        represent['job_ids'] = [
                                {**i, 'url': "http://demo.com"} for i in instance.job_ids
                                ] if instance.job_ids else []
        represent['supported_natcos'] = [i.__str__() for i in instance.supported_natcos.all()]
        if resolve_match.url_name == 'script-list':
            represent['developed_by'] = instance.developed_by.fullname if instance.developed_by else None
        else:
            represent['developed_by'] = instance.developed_by.fullname if instance.developed_by else None
            represent['reviewed_by'] = instance.reviewed_by.fullname if instance.reviewed_by else None
            represent['modified_by'] = instance.modified_by.fullname if instance.modified_by else None
        return represent

    def create(self, validated_data):
        ids = validated_data.pop('job_id', None)
        job_ids = []
        for i in range(len(ids)):
            job_ids.append({
                "id": i,
                "job_id": ids[i],
            })
        validated_data['job_ids'] = job_ids
        return super().create(validated_data)

    def update(self, instance, validated_data):
        ids = validated_data.pop('job_id', None)
        job_ids = []
        for i in range(len(ids)):
            job_ids.append({
                "id": i,
                "job_id": ids[i],
            })
        validated_data['job_ids'] = job_ids
        return super().update(instance, validated_data)


class TestCaseHistoryModelSerializer(serializers.ModelSerializer):

    history_id = serializers.IntegerField(source='id')
    history_user = serializers.CharField(source='user')
    history_change_reason = serializers.CharField(source="change_reason")
    history_date = serializers.DateTimeField(source="created")
    changed_to = serializers.JSONField(source="changed_fields")
    
    class Meta:
        model = TestCaseHistoryModel
        fields = ("history_id", "history_user", "changed_to", "history_change_reason", "history_date")

    def time_format(self, obj):
        data = datetime.fromisoformat(str(obj))
        return data.strftime("%d-%m-%Y %I:%M %p")

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent["history_user"] = instance.user.fullname if instance.user else None
        represent["changed_to"] = [instance.changed_fields]
        represent['history_date'] = self.time_format(instance.created)
        return represent


class ModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Module
        fields = ('name', )


class TestCaseTypeOptionSerializer(serializers.ModelSerializer):

    value = serializers.CharField(source='name')
    label = serializers.SerializerMethodField(read_only=True)

    def get_label(self, obj):
        return obj.name.capitalize() if obj.name else None

    class Meta:
        model = TestcaseTypes
        fields = ('label', 'value')

class TestCaseTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestcaseTypes
        fields = ('name', )
