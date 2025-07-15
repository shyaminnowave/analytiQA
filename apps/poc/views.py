import json
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import Http404
from apps.core.models import TestCaseModel, TestPlan, Module, TestCaseMetaData, TestScore
from django.core.paginator import Paginator
from apps.poc.utils import check_score
from rest_framework.generics import ListAPIView
from apps.core.apis.views import CustomPagination
from rest_framework import serializers, viewsets


# Create your views here.


class TestPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestPlan
        fields = '__all__'


class TestPlanningView(ListAPIView):

    serializer_class = TestPlanSerializer
    pagination_class = CustomPagination
    queryset = TestPlan.objects.all()


class TestCaseView(generic.TemplateView):

    template_name = 'poc/testcase.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        testcases = TestCaseModel.objects.all()
        paginator = Paginator(testcases, self.paginate_by, allow_empty_first_page=True)
        page_number = self.request.GET.get('page') if self.request.GET.get('page') else 1
        page = paginator.page(page_number)
        context['testcases'] = page
        return context


class TestPlanView(generic.TemplateView):

    template_name = 'poc/testplan.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        testplans = TestPlan.objects.all()
        modules = Module.objects.all()
        paginator = Paginator(testplans, self.paginate_by, allow_empty_first_page=True)
        page_number = self.request.GET.get('page') if self.request.GET.get('page') else 1
        page = paginator.page(page_number)
        context['testplan'] = page
        context['modules'] = modules
        return context


class GetTestCase(generic.View):

    def post(self, request, *args, **kwargs):
        lst = []
        data = json.loads(request.body.decode('utf-8'))
        testcase = [int(tc['id']) for tc in data.get('testcases', None)]
        queryset = TestCaseModel.objects.exclude(id__in=testcase).values('id', 'test_name')
        for i in queryset:
            temp = {
                "id": i['id'],
                "test_name": i['test_name'],
            }
            lst.append(temp)
        return HttpResponse(json.dumps(lst), content_type='application/json')


class CalculateScore(generic.View):

    def check_score(self, queryset):
        lst = []
        if queryset:
            for i in queryset:
                try:
                    instance = get_object_or_404(TestCaseMetaData, id=i.id)
                    temp = {
                        "id": i.id,
                        "name": i.name,
                        "score": float(instance.get_testscore())
                    }
                    lst.append(temp)
                except Http404:
                    temp = {
                        "id": i.id,
                        "name": i.name,
                        "score": 10.00
                    }
                    lst.append(temp)
        return lst

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        priority = data.get('priority', None)
        status = data.get('status', None)
        module = data.get('module', [])
        queryset = TestCaseModel.objects.filter(priority=priority, status=status, module__id__in = module).only('id', 'name', 'module')
        score = self.check_score(queryset)
        return HttpResponse(json.dumps(score) if score else None, content_type='application/json')


class CheckScore(generic.View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        testcase = data.get('testcases', None)
        queryset = TestCaseModel.objects.filter(id__in=testcase)
        score =  check_score(queryset)
        return HttpResponse(json.dumps(score) if score else None, content_type='application/json')


class AddTestPlan(generic.View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        try:
            testplan = TestPlan.objects.create(
                name = data.get('testplan'),
                description = data.get('description'),
                priority = data.get('priority'),
                status = data.get('status'),
            )
            modules = data.get('module', [])
            testcase = data.get('testcase', [])
            if modules:
                module_ids = [int(mid) for mid in modules]
                module = Module.objects.filter(id__in=module_ids)
                testplan.modules.add(*module)

            for tc in testcase:
                testcase_id = tc.get('id', None)
                print(testcase_id)
                score = tc.get('score', None)

                try:
                    testcase_obj = TestCaseModel.objects.get(id=testcase_id)
                    print(testcase_obj)
                    TestScore.objects.create(
                        testplan = testplan,
                        testcases = testcase_obj,
                        testscore = score
                    )
                except TestCaseModel.DoesNotExist:
                    print(f'{testcase_id} does not exist')
                    continue
            testplan.save()
        except Exception as e:
            return HttpResponse(str(e), content_type='application/json')
        return HttpResponse(json.dumps({"data": "success"}), content_type='application/json')


class PlanDetailView(generic.TemplateView):

    template_name = 'poc/details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.kwargs['id'])
        context['object'] = TestPlan.objects.get(id=self.kwargs['id'])
        return context

