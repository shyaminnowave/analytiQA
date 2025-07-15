from django.urls import path, re_path
from apps.core.apis import views


urlpatterns = [

    # Testcase API
    path('testcase/', views.TestCaseListView.as_view(), name="testcase-list"),
    path('testcase', views.TestCaseView.as_view(), name='create-testcase '),
    path('testcase/<int:id>', views.TestCaseDetailView.as_view(), name='testcase-details'),
    path('testcase/<int:id>/comment', views.TestcaseCommentView.as_view(), name='testcase-comment'),
    path('testcase/edit/comment/<int:id>', views.TestCaseCommentEditView.as_view(), name='edit-testcasecomment'),


    # Testcase Steps API
    path('testcase/<int:test_id>/steps', views.TestcaseStepView.as_view(), name='testcase-steps'),
    path('testcase/<int:test_id>/step/<int:step_id>', views.TestcaseStepDetailView.as_view(), name='testcase-step'),

    # TestCase NatCo API
    path('testcase/<int:id>/natCos', views.TestCaseNatCoView.as_view(), name='testcase-natCo'),
    path('testcase/natCo', views.TestCaseNatcoList.as_view(), name='natCo-list'),
    path('testcase/natCo/<int:pk>', views.TestCaseNatCoDetail.as_view(), name='natCo-details'), # need to check

    # TestCase ScriptIssue API
    path('script/<int:id>/issues', views.ScriptIssueView.as_view(), name='issues'),
    path('script/<int:id>/issue', views.ScriptIssueCreateView.as_view(), name='create-issue'),
    path('script/issue-detail/<int:id>', views.ScriptIssueDetailView.as_view(), name='testcase-issue-detail'),

    # TestCase ScriptIssue Comment API
    path('script/issues/<int:id>/comments', views.CommentsView.as_view(), name='issue-comment'),
    path('script/issue/<int:id>/create/comment', views.CommentCreateView.as_view(), name='create-comment'),
    path('script/issues/comment/<int:pk>', views.CommentEditView.as_view(), name='edit-comment'),

    # TestCase Script API
    path('testcase/<int:pk>/script', views.TestCaseScriptView.as_view(), name='create-script'),
    path('testcase/<int:pk>/scripts', views.TestCaseScriptList.as_view(), name='script-list'),
    path('testcase/script-detail/<int:pk>', views.TestcaseScriptDetailView.as_view(), name='testcase-script-detail'),

    # Script Issues Page
    path('issues-list', views.IssuesList.as_view(), name='issue-list'),

    # Tags API
    path('tags', views.TagsList.as_view(), name='tags'),
    path('tags/<int:id>', views.TagsDetails.as_view(), name='tags-detail'),

    # Module API
    path('module', views.ModulAPIView.as_view(), name='module'),
    path('add-module', views.MapModuleViewAPI.as_view(), name='add-module'),

    # Testcase Type
    path('test-types', views.TestcaseTypeOptionView.as_view(), name='test-types'),
    path('testcase-type', views.TestcaseTypeView.as_view(), name='testcase-type'),

    # Utility API
    path('natCo-status', views.NatCoStatusView.as_view(), name='natCo-status'),
    path('search', views.SearchView.as_view(), name='search'),
    path('testcase/history/<int:id>', views.TestCaseHistory.as_view(), name="testcase-history"),
    path('excel', views.ExcelUploadView.as_view(), name='excel-upload'),
    path('get-excel', views.GetExcelView.as_view(), name='get-excel'),

    # TestCase Bulk Update API
    re_path(r"update-bulk/(?P<path>.*)$", views.BulkFieldUpdateView.as_view(), name='update-bulk')
]
