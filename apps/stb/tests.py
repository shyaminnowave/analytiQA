from django.test import TestCase
import pytest
from pkg_resources import DistributionNotFound, get_distribution
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from apps.stb.models import Language
from django.core.exceptions import ValidationError
from apps.stb.models import STBManufacture, Language, Natco
from apps.stb.apis.serializers import LanguageSerializer, STBManufactureSerializer
# Create your tests here.


class TestLanguageModel(TestCase):

    def setUp(self):
        Language.objects.create(language_name="English")
        Language.objects.create(language_name="Germany")
        Language.objects.create(language_name="Polish")
        Language.objects.create(language_name="Hungarian")
        Language.objects.create(language_name="Croatian")
        Language.objects.create(language_name="Montenegrin")
        Language.objects.create(language_name="Macedonian")

    def test_language_str(self):
        english = Language.objects.get(language_name="English")
        germany = Language.objects.get(language_name="Germany")
        self.assertEqual(str(english), "English")
        self.assertEqual(str(germany), "Germany")


class TestLanguageSerializer(TestCase):
    def setUp(self):
        self.data = {
            "language_name": "Hindi"
        }

    def test_language_create(self):
        serializer = LanguageSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_language(self):
        invalid_data = {
            'language_name': "223payr"
        }
        serializer = LanguageSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_language(self):
        language = Language.objects.create(language_name="Test")
        serializer = LanguageSerializer(language)
        self.assertEqual(serializer.data['language_name'], 'Test')   


class TestSTBManufacture(TestCase):

    def setUp(self) -> None:
        STBManufacture.objects.create(name="Skyworth")
        STBManufacture.objects.create(name="SDMC")
        self.data = {
            "name": "Sei Robotics"
        }

    def test_stb(self):
        stb = STBManufacture.objects.get(name="Skyworth")
        self.assertEqual(stb.name, 'Skyworth')

    def test_stb_create(self):
        self._data = {
            "name": "HTC"
        }
        serializer = STBManufactureSerializer(data=self._data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_stb(self):
        invalid_data = {
            'name': "223payr"
        }
        serializer = STBManufactureSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid(), False)

    def test_stb_serializer(self):
        language = STBManufacture.objects.create(name="Test")
        serializer = STBManufactureSerializer(language)
        self.assertEqual(serializer.data['name'], 'Test') 


class TestNatco(TestCase):

    def setUp(self):
        Natco.objects.create(country='Poland', natco='PL')
        Natco.objects.create(country='Hungary', natco='HU')
        Natco.objects.create(country='Croatia', natco='HR')
        Natco.objects.create(country='Montenegro', natco='ME')
        Natco.objects.create(country='North Macedonia', natco='MKT')

    def test_natco_create(self):
        data = {
            'country': "Austria",
            'natco': "AT"
        }
        natco = Natco.objects.create(**data)
        self.assertEqual(natco.natco, 'AT')


class TestNatcoManufactureLang(TestCase):

    def test_natco_manufacture(self):
        natco = Natco.objects.create(country='Poland', natco='PL')
        device = STBManufacture.objects.create(name="SDMC")
        language = Language.objects.create(language_name="English")
        natco_manufacture_lang = NactoManufacturesLanguage.objects.create(
            natco=natco,
            device_name=device,
            language_name=language
        )
        self.assertEqual(natco_manufacture_lang.natco, natco)

