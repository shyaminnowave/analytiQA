import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.core.models import TestCaseModel, NatcoStatus, ScriptIssue, AutomationChoices, TestCaseScript, \
    TestCaseHistoryModel
from apps.general.models import Notification
from apps.stb.models import NatCo
from django.db import transaction
from django.shortcuts import get_object_or_404
from apps.general.utils import get_status_group
from django.contrib.contenttypes.models import ContentType

logging = logging.getLogger(__name__)


@receiver(post_save, sender=ScriptIssue)
def set_notification(sender, instance, created, **kwargs):
    if created:
        try:
            Notification.objects.create(
                message=f"{instance.script.script_name} - Script issue Opened By {instance.created_by}",
                user=instance.created_by,
                assigned_to=instance.script.developed_by,
                status=True,
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
            )
        except Exception as e:
            Notification.objects.create(
                message=f"{instance.script.script_name} - Script issue Opened Failed",
                user=instance.created_by,
                assigned_to=instance.script.developed_by,
                status=False,
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
            )
            logging.error(e)
    if created is False and instance.resolved_by:
        try:
            Notification.objects.create(
                message=f"{instance.script.script_name} - {instance.summary} Resolved by {instance.resolved_by}",
                user=instance.created_by,
                assigned_to=instance.resolved_by,
                status=True,
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
            )
        except Exception as e:
            Notification.objects.create(
                message=f"{instance.script.script_name} - {instance.summary} Resolved by {instance.resolved_by} Failed",
                user=instance.created_by,
                assigned_to=instance.script.developed_by,
                status=False,
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
            )
            logging.error(str(e))


@receiver(post_save, sender=TestCaseModel)
def send_notification(sender, instance, created, **kwargs):
    try:
        _lst = TestCaseHistoryModel.objects.filter(testcase=instance).first()
        if instance and _lst:
            """
            If Instance.History is None, Then its the First Instance
            """
            _prev = _lst.other_changes.get('assigned', None)
            if _prev != instance.assigned:
                Notification.objects.create(
                    message=f"Testcase ID {instance.id} is assigned to you by {instance.created_by.get_full_name()}",
                    user=instance.created_by,
                    content_type=ContentType.objects.get_for_model(instance),
                    object_id=instance.id,
                    status=True,
                    assigned_to=instance.assigned,
                )
        elif instance and instance.assigned:
            try:
                Notification.objects.create(
                    message=f"Testcase ID {instance.id} is assigned to you by {instance.created_by.get_full_name()}",
                    user=instance.created_by,
                    content_type=ContentType.objects.get_for_model(instance),
                    object_id=instance.id,
                    status=True,
                    assigned_to=instance.assigned,
                )
            except Exception as e:
                print(str(e))
        else:
            logging.error("No User assigned")
    except Exception as e:
        logging.error(str(e))


@receiver(post_save, sender=TestCaseModel)
def send_notification_group(sender, instance, created, **kwargs):
    try:
        _lst = TestCaseHistoryModel.objects.filter(testcase=instance).first()
        group = get_status_group(instance.automation_status)
        if _lst.automation_status == group.status: return
        if instance.automation_status and group:
            owner = group.owner
            Notification.objects.create(
                message=f"Testcase ID {instance.id} Status is now in {instance.automation_status}",
                user=instance.created_by,
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                status=True,
                assigned_to=group.owner,
            )
            return None
        else:
            return None
    except Exception as e:
        logging.error(str(e))
        return None


@receiver(post_save, sender=TestCaseModel)
def save_natCostas(sender, instance, created, **kwargs):
    try:
        if instance.automation_status == AutomationChoices.NOT_AUTOMATABLE:
            return

        current_user = TestCaseHistoryModel.objects.filter(testcase=instance).first()

        if NatcoStatus.objects.filter(test_case=instance).exists():
            logging.info(f"NactCoStatus already exists for Testcase {instance}")
            return

        natCo_list = NatCo.objects.prefetch_related('manufacture', 'language')
        status_entries = []

        for i in natCo_list:
            # Get related manufactures
            languages = i.language.all()
            for language in languages:
                status_entries.append(
                    NatcoStatus(
                        test_case=instance,
                        natco=i,
                        language=language.language_name,
                        device=i.manufacture.name,
                        user=current_user.user,
                    )
                )
        if status_entries:
            with transaction.atomic():
                NatcoStatus.objects.bulk_create(status_entries)
            logging.info(f"Created {len(status_entries)} NatcoStatus entries for TestCase {instance.id}")
        else:
            logging.warning(f"No valid NatcoStatus entries to create for TestCase {instance.id}")
    except Exception as e:
        logging.error(f"Error in save_natCostas: {str(e)}")


@receiver(post_save, sender=ScriptIssue)
def change_testcase_status(sender, instance, created, **kwargs):
    try:
        _instance = TestCaseModel.objects.get(pk=instance.script.testcase.id)
        if _instance:
            if instance.status == 'open':
                _instance.automation_status = AutomationChoices.IN_DEVELOPMENT
            elif instance.status == 'under_review':
                _instance.automation_status = AutomationChoices.REVIEW
            elif instance.status == 'closed':
                _testcase = ScriptIssue.check_open_issues(instance=instance.testcase)
                if _testcase is False:
                    _instance.automation_status = AutomationChoices.READY
            _instance.save()
        else:
            logging.error("No Created Instance is Found")
    except TestCaseModel.DoesNotExist as e:
        logging.error(str(e))


@receiver(post_save, sender=TestCaseScript)
def change_natcoStatus(sender, instance, created, **kwargs):
    try:
        if created:
            get_natco_instance = NatcoStatus.objects.get(
                test_case=instance.testcase,
                natco=instance.natCo.natco,
                device=instance.device.name,
                language=instance.language.language_name
            )
            get_natco_instance.applicable = True
            get_natco_instance.save()
        return
    except Exception as e:
        logging.error(str(e))

