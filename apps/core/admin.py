from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, redirect
from apps.core.apis.views import TestCaseHistory
from apps.core.models import TestCaseModel, TestCaseStep, NatcoStatus, \
                                TestCaseScript, Comment, ScriptIssue, Tag, TestPlan, TestCaseHistoryModel, Module, TestcaseTypes
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ExportMixin, ImportExportModelAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from apps.core.widgets import JSONTableFormat, JsonTableWidget
from apps.core.forms import StepAddForm, TestCaseForm
from simple_history.admin import SimpleHistoryAdmin
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import format_html
from functools import update_wrapper
# Register your models here.


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ['id', 'name']
    search_fields = ['name']


class ExportAdmin(ExportMixin, admin.ModelAdmin):
    pass


class TestStepAdmin(admin.TabularInline):

    extra = 3
    model = TestCaseStep


class CommentAdmin(GenericTabularInline):

    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    model = Comment


@admin.register(TestCaseModel)
class TestCaseModelAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):

    form = TestCaseForm

    list_display = ('id', 'jira_link', 'name', 'module', 'priority', 'testcase_type', 'automation_status', 'created_by')
    list_filter = ('priority', 'testcase_type', 'status', 'module')
    list_editable = ('module', 'automation_status', 'priority', 'testcase_type', 'created_by')
    search_fields = ['tags', 'name']
    history_list_display = ["status", 'changed_to', 'history_type']
    autocomplete_fields = ['tags']

    def jira_link(self, value):
        link = format_html('<a href="https://jira.telekom.de/browse/{}" target="_blank">{}</a>', value.get_jira_id(), value.get_jira_id())
        return link

    def response_action(self, request, queryset):
        return super().response_action(request, queryset)

    def get_add_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)
        
        info = self.model._meta.app_label, self.model._meta.model_name

        return [
            path('<path:object_id>/add-step', wrap(self.add_step_view), name='%s_%s_addStep' % info),
            path('<path:object_id>/change-step/<int:id>', wrap(self.change_step_view), name='%s_%s_changeStep' % info)
        ]

    def get_urls(self):
        """Register custom admin URLs for adding steps."""
        urls = super().get_urls()
        curl = self.get_add_urls()
        return curl + urls
    
    def change_step_view(self, request, object_id, id):
        testcase = TestCaseModel.objects.get(id=object_id)
        steps = testcase.steps or {}
        print('steps', steps.get('1'))
        _steps = steps.get(id)
        if request.method == 'POST':
            form = StepAddForm(request.POST)
            if form.is_valid():
                steps[id] = {
                    "step_action": form.cleaned_data["step_action"],
                    "step_data": form.cleaned_data["step_data"],
                    "expected_result": form.cleaned_data["expected_result"]
                }
            testcase.steps = steps  # Update the steps field
            testcase.save()
            return redirect(reverse("admin:core_testcasemodel_change", args=[object_id]))
        else:
            form = StepAddForm(initial=_steps)
        return render(request, "admin/core/add-steps.html", {"form": form, "testcase": testcase})


    
    def add_step_view(self, request, object_id):
        testcase = TestCaseModel.objects.get(id=object_id)
        form = StepAddForm()
        if request.method == 'POST':
            step_no = request.POST.get("step_number")
            step_action = request.POST.get("step_action")
            step_data = request.POST.get("step_data")
            expected_result = request.POST.get("expected_result")

            _steps = {
                step_no: {
                    "step_action": step_action,
                    "step_data": step_data,
                    "expected_result": expected_result
                }
            }

            testcase.steps.update(_steps)
            testcase.save()
            return redirect(reverse("admin:core_testcasemodel_change", args=[object_id]))
        return render(request, "admin/core/add-steps.html", {"form": form})

class NatcoStatusAdmin(SimpleHistoryAdmin):

    list_display = ['id', 'test_case', 'natco', 'language', 'device', 'status', 'applicable']


class TestResultAdmin(admin.ModelAdmin):

    list_display = ['id', 'testcase', 'natco']
    search_fields = ('testcase',)
    list_filter = ['node_id', 'natco', 'stb_release', 'stb_firmware', 'stb_android', 'stb_build']


class ReportAdmin(admin.ModelAdmin):

    list_display = ['job_id', 'testcase', 'node']
    list_filter = ['node']


@admin.register(ScriptIssue)
class ScriptIssueAdmin(SimpleHistoryAdmin):

    list_display = ['id', 'summary']
    inlines = [CommentAdmin]


@admin.register(TestPlan)
class TestPlanAdmin(admin.ModelAdmin):

    list_display = ['id', 'name']
    filter_horizontal = ('testcases',)


@admin.register(TestCaseScript)
class TestcaseScriptAdmin(admin.ModelAdmin):

    list_display = ['id', 'script_name', 'language', 'device', 'natCo']
    
# admin.site.register(TestCaseModel, TestCaseModelAdmin)
admin.site.register(NatcoStatus, NatcoStatusAdmin)
admin.site.register(Comment)
admin.site.register(TestCaseStep, ImportExportModelAdmin)
admin.site.register(TestCaseHistoryModel)
admin.site.register(Module)
admin.site.register(TestcaseTypes)