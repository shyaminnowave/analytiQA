from django.db import models
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Language(TimeStampedModel):
    language_name = models.CharField(max_length=100, unique=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s' % self.language_name

    class Meta:
        permissions = [
            ("view_language_option", "Can View Language Option List")
        ]


class STBManufacture(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s' % self.name

    class Meta:
        permissions = [
            ("view_stb_option", "Can View stb Option List")
        ]
        verbose_name = 'STB Manufactures'
        verbose_name_plural = 'STB Manufactures'


class Natco(TimeStampedModel):

    country = models.CharField(max_length=200)
    natco = models.CharField(max_length=10)
    manufacture = models.ManyToManyField(STBManufacture, blank=True, related_name='devices')
    language = models.ManyToManyField(Language, blank=True, related_name='languages')
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s' % self.natco

    class Meta:
        permissions = [
            ("view_natco_option", "Can View natco Option List")
        ]


class STBNode(TimeStampedModel):
    node_id = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.node_id

    class Meta:
        verbose_name = 'STB Nodes'
        verbose_name_plural = 'STB Nodes'


class NatCoFirmware(TimeStampedModel):

    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return '%s' % self.name


class NatcoRelease(TimeStampedModel):

    class ReleaseType(models.TextChoices):
        MAJOR = 'MR', _('MR')
        PATCH = "PAT", _('PAT')

    natcos = models.ForeignKey(Natco, on_delete=models.CASCADE, related_name='release')
    release_type = models.CharField(choices=ReleaseType.choices, max_length=20, help_text="MR - Major Release")
    build_type = models.CharField(max_length=200, default='', blank=True, null=True)
    build_version = models.CharField(max_length=200, blank=True, null=True)
    version = models.CharField(max_length=20, default='', blank=True, null=True)
    firmware = models.ForeignKey(NatCoFirmware, on_delete=models.CASCADE, related_name='releases')
    android_version = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.natcos.natco} {self.release_type} - {self.version}"

    def get_natco_fullname(self):
        return f"{self.natcos.natco} {self.release_type}{self.version} {self.firmware} {self.android_version}"
    

    class Meta:
        verbose_name = 'Natco Releases'
        verbose_name_plural = 'Natco Releases'


class STBNodeConfig(TimeStampedModel):

    stb_node = models.ForeignKey(STBNode, on_delete=models.CASCADE)
    natco = models.ForeignKey(NatcoRelease, on_delete=models.CASCADE, max_length=255, default='')
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.natco.natcos.natco} {self.natco.release_type} {self.natco.version} A{self.natco.android_version} -" \
               f" {self.stb_node.node_id}"

    class Meta:
        verbose_name = 'STB Node Configs'
        verbose_name_plural = 'STB Node Configs'
