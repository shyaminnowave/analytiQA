from django.db.models import Model
from django.db import transaction


class QuerySetEntry:

    @staticmethod
    def bulk_create_entries(cls, data):
        try:
            if issubclass(cls, Model):
                with transaction.atomic():
                    cls.objects.bulk_create(data)
            else:
                raise Exception
        except Exception as e:
            raise ValueError(f"Error in bulk Creation: {str(e)}")
        


def generate_history_message(instance, validated_data):
    message = None
    if instance.description != validated_data.get("description", instance.description):
        message = f"Desciption: {instance.description} changed to {validated_data.get('description')}"
    if instance.name != validated_data.get("name", instance.name):
        message = f"Name: {instance.name} changed to {validated_data.get('name')}"
    if instance.status != validated_data.get("status", instance.status):
        message = f"Status: {instance.status} changed to {validated_data.get('status')}"
    if instance.automation_status != validated_data.get("automation_status", instance.automation_status):
        message = f"Automation Status {instance.automation_status} changed to" \
                    f" {validated_data.get('automation_status')}"
    if instance.priority != validated_data.get("priority", instance.priority):
        message = f"Priority: {instance.priority} changed to {validated_data.get('priority')}"
    if instance.testcase_type != validated_data.get("testcase_type", instance.testcase_type):
        message = f"Testcase Type: {instance.testcase_type} changed to {validated_data.get('testcase_type')}"
    if instance.assigned != validated_data.get("assigned", instance.assigned):
        message = f"Assigned: {instance.assigned} changed to {validated_data.get('assigned')}"
    return message

def generate_changed_fields(instance, validated_data):
    msg = dict()
    if instance.description != validated_data.get("description", instance.description):
        msg['Desciption'] = f"{instance.description} changed to {validated_data.get('description')}" # type: ignore
    if instance.name != validated_data.get("name", instance.name):
        msg['Name'] = f"{instance.name} changed to {validated_data.get('name')}"
    if instance.status != validated_data.get("status", instance.status):
        msg["Status"] = f"{instance.status} changed to {validated_data.get('status')}"
    if instance.automation_status != validated_data.get("automation_status", instance.automation_status):
        msg["Automation Status"] = f"Automation Status {instance.automation_status} changed to" \
                    f" {validated_data.get('automation_status')}"
    if instance.priority != validated_data.get("priority", instance.priority):
        msg["Priority"] = f"{instance.priority} changed to {validated_data.get('priority')}"
    if instance.testcase_type != validated_data.get("testcase_type", instance.testcase_type):
        msg["Testcase Type"] = f"Testcase Type: {instance.testcase_type} changed to {validated_data.get('testcase_type')}"
    if instance.assigned != validated_data.get("assigned", instance.assigned):
        msg["Assigned"] = f"{instance.assigned} changed to {validated_data.get('assigned')}"
    return msg