from unittest import TestCase

import django_filters
from apps.core.models import NatcoStatus, TestCaseModel


class NatcoStatusFilter(django_filters.FilterSet):

    jira_id = django_filters.CharFilter(field_name='test_case__jira_id', lookup_expr='iexact')
    natco = django_filters.CharFilter(field_name='natco')
    language = django_filters.CharFilter(field_name='language', lookup_expr='iexact')
    status = django_filters.CharFilter(field_name='status', lookup_expr='icontains')
    device = django_filters.CharFilter(field_name='device', lookup_expr='iexact')
    applicable = django_filters.BooleanFilter(field_name='applicable')

    class Meta:
        model = NatcoStatus
        fields = ['natco', 'language', 'device', 'jira_id', 'applicable']


class TestCaseFilter(django_filters.FilterSet):

    testcase_type = django_filters.CharFilter(field_name='testcase_type', lookup_expr='in')
    status = django_filters.CharFilter(field_name='status', lookup_expr='in', method='filter_status')
    priority = django_filters.CharFilter(field_name='priority', lookup_expr='in', method='filter_priority')
    automation_status = django_filters.CharFilter(field_name='automation_status', lookup_expr='in',
                                                  method='filter_automation_status')

    class Meta:
        model = TestCaseModel
        fields = ['jira_id', 'name', 'status', 'priority', 'automation_status']

    def filter_status(self, queryset, name, value):
        """
        Custom filter method to handle multiple 'status' values.
        """
        values = self.request.GET.getlist(name)
        if values:
            return queryset.filter(**{f"{name}__in": values})
        return queryset

    def filter_priority(self, queryset, name, value):
        """
        Custom filter method to handle multiple 'priority' values.
        """
        values = self.request.GET.getlist(name)
        if values:
            return queryset.filter(**{f"{name}__in": values})
        return queryset

    def filter_automation_status(self, queryset, name, value):
        """
        Custom filter method to handle multiple 'automation_status' values.
        """
        values = self.request.GET.getlist(name)
        if values:
            return queryset.filter(**{f"{name}__in": values})
        return queryset


