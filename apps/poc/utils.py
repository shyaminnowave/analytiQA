from apps.core.models import TestCaseModel, TestCaseMetaData
from django.shortcuts import get_object_or_404
from django.http import Http404

def check_score(queryset):
    lst = []
    if queryset:
        for i in queryset:
            try:
                instance = get_object_or_404(TestCaseMetaData, id=i.id)
                temp = {
                    "id": i.id,
                    "name": i.test_name,
                    "score": float(instance.get_testscore())
                }
                lst.append(temp)
            except Http404:
                temp = {
                    "id": i.id,
                    "name": i.test_name,
                    "score": 10.00
                }
                lst.append(temp)
    return lst