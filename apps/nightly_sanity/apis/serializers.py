from rest_framework import serializers
from apps.nightly_sanity.models import Releases, ApkFiles, TestExecutions


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
        fields = ['id', 'stb_node', 'test', 'total_iterations',  'passed_iterations', 'failed_iterations']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['stb_node'] = instance.stb_node.friendly_name if instance.stb_node else None
        representation['test'] = instance.test.functionality if instance.test else None
        return representation


