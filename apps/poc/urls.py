from django.urls import path
from .views import TestCaseView, TestPlanView, CalculateScore, GetTestCase, CheckScore, AddTestPlan, PlanDetailView, \
    TestPlanningView

urlpatterns = [
    path("testcase", TestCaseView.as_view(), name="testcase"),
    path('plan', TestPlanningView.as_view(), name="plan"),
    path("test-plan", TestPlanView.as_view(), name="testplan"),
    path('calculate-score', CalculateScore.as_view(), name="calculate-score"),
    path('ajax-testcase', GetTestCase.as_view(), name='ajax-testcase'),
    path('check-score', CheckScore.as_view(), name='check-score'),
    path('add-test-plan', AddTestPlan.as_view(), name='add-test-plan'),
    path('plan-detail/<int:id>', PlanDetailView.as_view(), name='plan-detail'),
]