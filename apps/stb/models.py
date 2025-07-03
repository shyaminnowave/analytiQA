from django.db import models
from django.contrib.auth import get_user_model
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords
from django.utils.translation import gettext_lazy as _
# Create your models here.

User = get_user_model()


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


class NatCo(TimeStampedModel):

    country = models.CharField(max_length=200)
    natco = models.CharField(max_length=10)
    manufacture = models.ForeignKey(STBManufacture, blank=True, on_delete=models.CASCADE, related_name='devices')
    language = models.ManyToManyField(Language, blank=True, related_name='languages')
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s - %s' % (self.natco, self.manufacture.name)

    class Meta:
        verbose_name = 'Natcos'
        verbose_name_plural = 'Natcos'
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

    class Meta:
        verbose_name = 'Natco Firmware'
        verbose_name_plural = 'Natco Firmware'


class NatcoRelease(TimeStampedModel):

    class ReleaseType(models.TextChoices):
        MAJOR = 'MR', _('Major Release')
        PATCH = "PAT", _('Patch Release')
        ENGINEERING = 'ENG', _('Engineering Release')

    natcos = models.ForeignKey(NatCo, on_delete=models.CASCADE, related_name='release')
    release_type = models.CharField(choices=ReleaseType.choices, max_length=20, help_text="MR - Major Release")
    build_type = models.CharField(max_length=200, default='', blank=True, null=True)
    build_version = models.CharField(max_length=200, blank=True, null=True)
    version = models.CharField(max_length=20, default='', blank=True, null=True)
    firmware = models.ForeignKey(NatCoFirmware, on_delete=models.CASCADE, related_name='releases')
    friendly_name = models.CharField(max_length=200, blank=True, null=True)
    android_version = models.DecimalField(default=0, max_digits=20, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.natcos.natco} {self.release_type} - {self.android_version}"

    def get_natCo_fullname(self):
        return f"{self.natcos.natco} {self.release_type}{self.version} {self.firmware} {self.android_version}"
    

    class Meta:
        verbose_name = 'NatCo Releases'
        verbose_name_plural = 'NatCo Releases'


class STBNodeMapping(TimeStampedModel):

    stb_node = models.ForeignKey(STBNode, on_delete=models.CASCADE, related_name='mappings')
    natcos = models.ForeignKey(NatCo, on_delete=models.CASCADE, related_name='natcos')

    def __str__(self):
        return f"{self.natcos} - {self.stb_node.node_id}"


class STBNodeConfig(TimeStampedModel):

    stb_node = models.ForeignKey(STBNode, on_delete=models.CASCADE)
    natco = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.stb_node} - {self.natco}"

    class Meta:
        verbose_name = 'STB Node Configs'
        verbose_name_plural = 'STB Node Configs'


class StbBaseURL(TimeStampedModel):

    rest_endpoint = models.CharField(max_length=200, unique=True)
    private_endpoint = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.rest_endpoint


class StbAPIEndpoint(TimeStampedModel):

    name = models.CharField(max_length=200, unique=True)
    url = models.URLField(max_length=400)
    headers = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'STB API'
        verbose_name_plural = 'STB API'


class STBAuthToken(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    access_token = models.CharField(max_length=400)

    def __str__(self):
        return "%s - %s" % (self.user, self.access_token)

    @property
    def get_authorization_token(self):
        return {
            "Authorization": f"token {self.access_token}"
        }


    class Meta:
        verbose_name = 'STB Authorization Token'
        verbose_name_plural = 'STB Authorization Token'


class STBScheduleModel(TimeStampedModel):

    job_id = models.CharField(max_length=200, unique=True)
    job_url = models.URLField(max_length=400, blank=True, null=True)
    log_url = models.URLField(max_length=400, blank=True, null=True)
    result_counts = models.JSONField(default=dict)
    start_time = models.CharField(max_length=200)
    end_time = models.CharField(max_length=200)
    status = models.CharField(max_length=10, default='', blank=True, null=True)
    triage_url = models.URLField(max_length=400, blank=True, null=True)

    class Meta:
        verbose_name = 'STB schedule model'
        verbose_name_plural = 'STB schedule model'

class StbResult(TimeStampedModel):

    class ResultChoice(models.TextChoices):
        PASS = 'pass', _('Pass')
        FAIL = 'fail', _('Fail')
        ERROR = 'error', _('Error')

    result_id = models.CharField(max_length=255)
    job_uid = models.CharField(max_length=255)
    result_url = models.URLField()
    triage_url = models.URLField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    script = models.ForeignKey('core.TestCaseScript', on_delete=models.CASCADE, blank=True, null=True)
    result = models.CharField(choices=ResultChoice.choices, max_length=10)
    failure_reason = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.result_id

    def get_result(self):
        return self.result[:20]

    def get_start_date(self):
        _start_time = str(self.start_time).split(' ')
        _remove_gmt = _start_time[-1].split('+')
        if _remove_gmt and _start_time:
            _remove_gmt.pop()
            _start_time.pop()
        _start_time.extend(_remove_gmt)
        return 'T'.join(_start_time)


    def get_time(self, attr=None):
        _time = None
        if attr is None or attr == 'start_time':
            _time = str(self.start_time).split(' ')
        elif attr == 'end_time':
            _time = str(self.end_time).split(' ')
        _remove_gmt = _time[-1].split('+')
        if _remove_gmt and _time:
            _remove_gmt.pop()
            _time.pop()
        _time.extend(_remove_gmt)
        return ' '.join(_time)