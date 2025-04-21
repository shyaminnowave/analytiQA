from django.db import models
from django_extensions.db.models import TimeStampedModel
from apps.stb.models import Natco, NatcoRelease
from apps.core.models import TestCaseModel

# Create your models here.

class JobInfo(TimeStampedModel):

    build = models.ForeignKey(NatcoRelease, on_delete=models.CASCADE)
    job_id = models.CharField(max_length=200)
    run_type = models.CharField(max_length=200)

    def __str__(self):
        return self.job_id
    
class RunInfo(TimeStampedModel):

    job_id = models.ForeignKey(JobInfo, on_delete=models.CASCADE)


class SanityReport(TimeStampedModel):

    pass

