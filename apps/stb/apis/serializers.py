import re
from rest_framework import serializers
from apps.stb.models import Language, STBManufacture, NatCo, NatcoRelease


def non_number_validator(value):
    if value and not re.match(r'^[a-zA-Z/S]+$', value):
        raise serializers.ValidationError("Cannot Contain Numbers")
    return value


class LanguageSerializer(serializers.ModelSerializer):

    language_name = serializers.CharField(required=True, max_length=20)

    class Meta:
        fields = ('id', 'language_name',)
        model = Language

    def validate_language_name(self, value):
        if value is None:
            raise serializers.ValidationError({"language_name": "Language Field cannot be Empty"})
        elif value and not re.match(r"^[a-zA-Z/S]+$", value):
            raise serializers.ValidationError({"language_name": "Language Cannot Contain Numbers and Symbols"})
        return value

    def create(self, validated_data):
        if Language.objects.filter(language_name=validated_data.get('language_name')).exists():
            raise serializers.ValidationError({"language_name": "Language already Exists"})
        validated_data['language_name'] = validated_data.get('language_name').capitalize()
        return super(LanguageSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validated_data['language_name'] = validated_data.get('language_name').capitalize()
        if Language.objects.filter(language_name=validated_data.get('language_name')).count() >= 2:
            raise serializers.ValidationError({"language_name": "Language already Exists"})
        return super(LanguageSerializer, self).update(instance, validated_data)


class STBManufactureSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', )
        model = STBManufacture

    def validate_name(self, value):
        if value is None:
            raise serializers.ValidationError("STB Manufacture Name Cannot be Empty")
        elif value and not re.match(r"^[a-zA-Z/S]+$", value):
            raise serializers.ValidationError("STB Manufacture Name Cannot Contain Numbers")
        return value
    
    def validate(self, attrs):
        if attrs['name']:
            if STBManufacture.objects.filter(name=attrs['name']).exists():
                raise serializers.ValidationError("STB Manufacture Already Exists")
            else:
                return attrs
        else:
            raise serializers.ValidationError("Name Field Cannot be Empty")


class NactoSerializer(serializers.ModelSerializer):

    country = serializers.CharField(required=True, validators=[non_number_validator])
    natco = serializers.CharField(required=True, validators=[non_number_validator])

    class Meta:
        fields = ('id', 'country', 'natco', 'manufacture', 'language')
        model = NatCo

    def validate(self, attrs): 
        if attrs['country'] and attrs['natco']:
            if NatCo.objects.filter(country=attrs['country'], natco=attrs['natco']).exists():
                raise serializers.ValidationError("Country or Nacto Already Present Please Check")
        return attrs

    def to_representation(self, instance):
        represent = super(NactoSerializer, self).to_representation(instance)
        represent['manufacture'] = [i.name for i in instance.manufacture.all()]
        represent['language'] = [i.language_name for i in instance.language.all()]
        return represent


class NatcoOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = NatCo
        fields = ('id', 'natco',)


class LanguageOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = ('id', 'language_name',)


class DeviceOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = STBManufacture
        fields = ('id', 'name',)

class NatcoReleaseOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = NatcoRelease
        fields = ('id', 'natcos')

    def to_representation(self, instance):
        represent = super(NatcoReleaseOptionSerializer, self).to_representation(instance)
        represent['natcos'] = f"{instance.natcos.natco} - {instance.release_type} : {instance.android_version}"
        return represent


class NatcoFilterSerializerView(serializers.ModelSerializer):

    label = serializers.CharField(required=False)
    value = serializers.CharField(source="natco", required=False)

    class Meta:
        model = NatCo
        fields = ('label', 'value')

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['label'] = instance.natco
        return represent

class NatcoReleaseInfo(serializers.ModelSerializer):

    class Meta:
        model = NatcoRelease
        exclude = ('created', 'modified')

    def to_representation(self, instance):
        response =  super().to_representation(instance)
        response['natcos'] = instance.natcos.natco
        return response
