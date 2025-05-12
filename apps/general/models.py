from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from apps.core.models import AutomationChoices

# Create your models here.

User = get_user_model()


class JobIDCounter(TimeStampedModel):

    automation_team = models.IntegerField()
    verification_team = models.IntegerField()

    def __str__(self):
        return f"Verification Team - {self.verification_team} : Automation Team - {self.automation_team}"


class Status(TimeStampedModel):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    def save(self, **kwargs):
        self.name = self.name.lower()
        super().save(**kwargs)


class StatusGroup(TimeStampedModel):

    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_owner')
    status = models.ManyToManyField(Status, related_name='group_status')
    members = models.ManyToManyField(User, related_name='group_members')

    def __str__(self):
        return self.name

    def get_status(self):
        lst = [i.name for i in self.status.all()]
        return lst



class Notification(TimeStampedModel):

    message = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_notification')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='user_notification')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    status = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return "%s - %s" % (self.message, self.user.get_full_name())

    class Meta:
        ordering = ['-created']

    def get_absolute_url(self):
        context_dict = {
            "scriptissue": 'script/issue-detail',
            "testcasemodel": 'testcase',
        }
        if self.object_id and (self.content_type.model in context_dict):
            if self.content_type.app_label:
                return f"{self.content_type.app_label}/{context_dict[self.content_type.model]}/{self.object_id}"
            return f"{context_dict[self.content_type.model]}/{self.object_id}/"
        elif self.object_id is None and (self.content_type.model in context_dict):
            if self.content_type.app_label:
                return f"{self.content_type.app_label}/{context_dict[self.content_type.model]}/"
            return f"{context_dict[self.content_type.model]}/"
        else:
            return None
