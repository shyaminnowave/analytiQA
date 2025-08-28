from rest_framework import serializers
from apps.nightly_sanity.models import Releases, ApkFiles, TestExecutions, TestIterations, TestCases


class ReleaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Releases
        fields = ['id', 'major_release', 'sub_release', 'box_release_info', 'release_date', 'created_at', 'updated_at']


class ApkFilesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApkFiles
        fields = '__all__'


class ApiFileNameSerializer(serializers.Serializer):
    filename = serializers.CharField(source='get_build_version', max_length=255, read_only=True)


class NatcoSerializer(serializers.Serializer):
    lable = serializers.CharField(source='natco', max_length=50)
    value = serializers.CharField(source='natco', max_length=50)


class TestFunctionalitySerializer(serializers.Serializer):

    functionality = serializers.CharField(max_length=255)


class TestExecutionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestExecutions
        fields = [
            'id', 'total_iterations', 'passed_iterations', 'failed_iterations', 'error_iterations', 'natco', 'get_release', 'get_testcase', 'get_testcase_name'
        ]
        

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation
    

class TestIterationSerializer(serializers.ModelSerializer):

    result_id = serializers.CharField(
        source='get_result_url',
        max_length=200,
        read_only=True
    )

    box_release_info = serializers.CharField(
        max_length = 20,
        read_only = True
    )

    class Meta:
        model = TestIterations
        fields = ['iteration_number', 'execution', 'result', 'failure_reason', 'result_id', 'box_release_info']

    def get_testcase(self, obj):
        if obj:
            get_name = TestCases.objects.using('sanity').get(id=obj)
            return get_name.testcase_name
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['natco'] = instance.execution.natco
        rep['testcase'] = self.get_testcase(instance.execution.testcase_number)
        return rep
