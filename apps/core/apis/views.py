import os
import re
import logging
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from apps.core.models import (TestCaseModel, TestCaseStep, NatcoStatus, Comment, ScriptIssue, TestCaseScript, Tag, \
                              TestCaseHistoryModel, Module, TestcaseTypes)
from apps.core.apis.serializers import (
    TestCaseSerializerList,
    TestCaseSerializer,
    ExcelUploadSerializer,
    NatcoStatusSerializer,
    BulkFieldUpdateSerializer,
    ScriptIssueSerializer,
    CommentSerializer,
    TestcaseScriptSerializer,
    TestCaseScriptListSerializer,
    ScriptIssueList,
    TagSerializer,
    TestCaseStepSerializer,
    StepsListSerializer,
    IssuesListSerializer,
    TestCaseHistoryModelSerializer,
    ModuleSerializer,
    TestCaseTypeOptionSerializer,
    TestCaseTypeSerializer
)
from django.core.files.storage import default_storage
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.core.pagination import CustomPagination, CustomPageNumberPagination
from drf_spectacular.utils import extend_schema
from django_filters import rest_framework as filters
from apps.core.filters import NatcoStatusFilter, TestCaseFilter
from analytiQA.helpers.renders import ResponseInfo
from analytiQA.helpers import custom_generics as cgenerics
from rest_framework import status
from django.db.models import Prefetch, Case, When, Value, IntegerField
from rest_framework import serializers
from rest_framework.views import APIView
from django.http import HttpResponse
from apps.core.utlity import get_testcase_module
from apps.core.excel import TestCaseExl
from apps.stb.mixins import OptionMixin
from apps.core.tasks import process_excel
from apps.core.permissions import TestCaseUpdatePermission, CommentPermission
#########################################################################

logging = logging.getLogger(__name__)


@extend_schema(
    summary="Bulk update fields for test cases or NATCO entities",
    description=(
        "This endpoint allows for bulk updates of specific fields in test cases or NATCO entities.\n\n"
        "**Path Parameters:**\n"
        "- `status`: Updates the status of test cases.\n"
        "- `automation-status`: Updates the automation status of test cases.\n"
        "- `natco/status`: Updates the status of NATCO entities.\n\n"
        "**Request Body:**\n"
        "The body should contain the fields to be updated. The exact fields depend "
        "on the operation being performed.\n\n"
        "**Responses:**\n"
        "- `200 OK`: Successfully updated the specified fields.\n"
        "- `400 Bad Request`: Returned if the provided data is invalid or if the update operation fails."
    ),
    tags=["TestCase Module APIS"]
)
class BulkFieldUpdateView(generics.GenericAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(BulkFieldUpdateView, self).__init__(**kwargs)

    serializer_class = BulkFieldUpdateSerializer

    def get_serializer_context(self):
        return {
            'field': self.kwargs.get('path').split('/')[0]
        }

    def patch(self, request, *args, **kwargs):
        kwargs_splitted = kwargs.get("path").split("/")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            match kwargs_splitted[0]:
                case "status":
                    instance = serializer.update_testcase_status(serializer.validated_data)
                case "automation_status":
                    instance = serializer.update_testcase_automation(serializer.validated_data)
                case "natco":
                    match kwargs_splitted[1]:
                        case "status":
                            instance = serializer.update_natco_status(serializer.validated_data)
                        case "applicable":
                            instance = serializer.update_applicable_status(serializer.validated_data)
                        case _:
                            instance = False
                case _:
                    instance = False
            response_template = {
                "status": True,
                "status_code": status.HTTP_200_OK,
                "data": None,
                "message": "Success"
            }
            return Response(
                response_template,
                status=status.HTTP_200_OK if instance else status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "status": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


#########################################################################


@extend_schema(
    summary="Retrieve a list of test cases",
    description=(
        "This endpoint retrieves a paginated list of test cases.\n\n"
    ),
    tags=["TestCase Module APIS"]
)
class TestCaseListView(generics.ListAPIView):

    # authentication_classes = [JWTAuthentication]
    # permission_classes = [AdminPermission]
    serializer_class = TestCaseSerializerList
    pagination_class = CustomPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = TestCaseFilter
    filterset_fields = [
        "jira_id",
        "test_name",
        "status",
        "priority",
        "automation_status",
    ]

    def get_queryset(self):
        queryset = None
        types = self.request.GET.get('type', None)
        if types:
            queryset = TestCaseModel.objects.filter(
                testcase_type = types.lower()
            )
        else:
            queryset = TestCaseModel.objects.all()
        return queryset.only("jira_id", "name", "priority", "testcase_type",
                                                               "status", "automation_status")

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)
        return response


@extend_schema(
    summary="Create a new test case",
    description=(
        "This endpoint allows you to create a new test case.\n\n"
    ),
    tags=["TestCase Module APIS"]
)
class TestCaseView(cgenerics.CustomCreateAPIView):

    authentication_classes = (JWTAuthentication,)
    serializer_class = TestCaseSerializer

    def post(self, request, *args, **kwargs):
        self.response_format['message'] = "TestCase Created Successfull"
        return super(TestCaseView, self).post(request, *args, **kwargs)

    def get_serializer_context(self, **kwargs):
        return {
            "request": self.request
        }


@extend_schema(
    summary="Retrieve, update, or delete a test case",
    description=(
        "This endpoint allows you to retrieve, update, or delete a test case by its ID.\n\n"
    ),
    tags=["TestCase Module APIS"]
)
class TestCaseDetailView(cgenerics.CustomRetrieveUpdateDestroyAPIView):

    authentication_classes = [JWTAuthentication, ]
    lookup_field = "id"
    serializer_class = TestCaseSerializer

    def get_object(self):
        queryset = get_object_or_404(
            TestCaseModel.objects.
            prefetch_related(
                Prefetch("test_steps", queryset=TestCaseStep.objects.only(
                    "id",
                    "step_number",
                    "step_data",
                    "step_action",
                    "expected_result",
                    "testcase__id"
                ))
            ),
            id=self.kwargs.get("id"),
        )
        return queryset

    def get_serializer_context(self):
        return {
            "request": self.request
        }

class TestcaseStepView(cgenerics.CustomRetriveAPIVIew):

    authentication_classes = [JWTAuthentication, ]
    serializer_class = StepsListSerializer

    def get_object(self):
        return TestCaseModel.objects.only("steps").get(id=self.kwargs.get("test_id"))



class TestcaseStepDetailView(cgenerics.CustomRetrieveUpdateDestroyAPIView):

    serializer_class = TestCaseStepSerializer

    def get_object(self):
        instance = TestCaseModel.objects.get(id=self.kwargs.get("test_id")).steps[str(self.kwargs.get("step_id"))]
        return instance

    def get_serializer_context(self):
        return (
            {
                "testcase": self.kwargs.get("test_id"),
                "step_id": str(self.kwargs.get("step_id")),
            }
        )

    def put(self, request, *args, **kwargs):
        try:
            response = self.get_serializer(self.get_object(), data=request.data)
            if response.is_valid():
                response.update_step(response.validated_data)
                self.response_format['status'] = True
                self.response_format['status_code'] = status.HTTP_200_OK
                self.response_format['data'] = "Success"
                self.response_format['message'] = "Success"
                return Response(self.response_format, status=status.HTTP_200_OK)
            else:
                self.response_format['status'] = False
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format['message'] = response.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as err:
            default_error = {key: value[0] if isinstance(value, list) else value for key, value in
                                 err.detail.items()}
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
            self.response_format['data'] = 'Error'
            self.response_format['message'] = default_error
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['message'] = {"error": str(e)}
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            response = self.get_serializer(self.get_object())
            res = response.delete_step()
            if res is True:
                self.response_format['status'] = True
                self.response_format['status_code'] = status.HTTP_200_OK
                self.response_format['data'] = "Deleted"
                self.response_format['message'] = "Success"
                return Response(self.response_format, status=status.HTTP_200_OK)
            else:
                self.response_format['status'] = False
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format['message'] = response.errors
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as err:
            default_error = {
                key: value[0] if isinstance(value, list) else value for key, value in err.detail.items()
            }
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
            self.response_format['data'] = 'Error'
            self.response_format['message'] = default_error
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['message'] = {"error": str(e)}
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestCaseNatCoView(generics.ListAPIView):

    # permission_classes = [AdminPermission]
    serializer_class = NatcoStatusSerializer
    lookup_field = "id"
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = (
            NatcoStatus.objects.select_related("test_case", "user", "modified")
            .filter(test_case_id=self.kwargs.get("id")).order_by('-applicable')
        )
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(TestCaseNatCoView, self).list(request, *args, **kwargs)
        return response


@extend_schema(
    summary="Retrieve NATCO statuses for a specific test case",
    description=(
        "This endpoint retrieves the NATCO statuses associated with a specific test case.\n\n"
        "**Path Parameters:**\n"
        "- `jira_id`: The unique identifier of the test case for which NATCO statuses are being queried.\n\n"
        "**Response:**\n"
        "- `200 OK`: A list of NATCO statuses, including the `id` and `summary` fields.\n"
        "- `404 Not Found`: Returned if no NATCO statuses are found for the specified test case."
    ),
    tags=["TestCase Module APIS"]
)
class TestCaseNatcoList(generics.ListAPIView):
    # permission_classes = [AdminPermission]
    serializer_class = NatcoStatusSerializer
    filterset_class = NatcoStatusFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = NatcoStatus.objects.select_related('test_case', 'user', 'modified').all().order_by('True')
        return queryset

    def list(self, request, *args, **kwargs):
        data = self.get_queryset()
        filter_set = self.filterset_class(request.GET, self.get_queryset())
        if filter_set.is_valid():
            data = filter_set.qs
        paginated_data = self.paginate_queryset(data)
        serializer = self.get_serializer(paginated_data, many=True)
        try:
            if serializer:
                return self.get_paginated_response(serializer.data)
            return None
        except Exception as e:
            return Response({"success": False, "data": str(e)})


@extend_schema(
    summary="Retrieve, update, or delete a NATCO status",
    description=(
        "This endpoint allows for retrieving, updating, or deleting a NATCO status by its ID.\n\n"
        "**Path Parameters:**\n"
        "- `id`: The unique identifier of the NATCO status.\n\n"
        "**Responses:**\n"
        "- `200 OK`: Returns the requested NATCO status details when retrieved.\n"
        "- `204 No Content`: Indicates successful deletion of the NATCO status.\n"
        "- `400 Bad Request`: Returned when the update request is invalid.\n"
        "- `404 Not Found`: Returned if the specified NATCO status does not exist."
    ),
    tags=["TestCase Module APIS"]
)
class TestCaseNatCoDetail(cgenerics.CustomRetrieveUpdateDestroyAPIView):
    # permission_classes = [AdminPermission]
    serializer_class = NatcoStatusSerializer
    lookup_field = "pk"

    def get_object(self):
        queryset = NatcoStatus.objects.select_related("test_case", "user", "modified").get(
            id=self.kwargs.get("pk")
        )
        return queryset

    def get_serializer_context(self):
        return {
            'request': self.request
        }


@extend_schema(
    summary="Retrieve Filter Options for Test Cases",
    description=(
        "This endpoint returns various filter options for test cases, including:\n\n"
        "- **Test Case Status**: A list of available status choices for test cases.\n"
        "- **Status**: A list of general status options.\n"
        "- **Priority**: A list of priority levels for test cases.\n"
        "- **Automation**: A list of automation-related options.\n\n"
        "Each filter option is represented as an object with `label` and `value` fields."
    ),
    tags=["TestCase Module APIS"]
)
class ExcelUploadView(APIView):

    serializer_class = ExcelUploadSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        try:
            upload_type = request.data.get("uploadtype", None)
            file_name = default_storage.save(f'temp_uploads/{upload_type}.xlsx', request.data.get("file"))
            file_path = default_storage.path(file_name)
            match upload_type:
                case 'testcase':
                    instance = process_excel.delay(file_path, "shyam6132@gmail.com")
            self.response_format['status'] = True
            self.response_format['status_code'] = status.HTTP_200_OK
            self.response_format['data'] = "Excel Will Upload Shortly"
            self.response_format['message'] = "Success"
            return Response(self.response_format, status=status.HTTP_200_OK)
        except Exception as err:
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
            self.response_format['data'] = 'Error'
            self.response_format['message'] = str(err)
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


class GetExcelView(APIView):

    def get(self, request, *args, **kwargs):
        _type = request.GET.get('file_type')

        if _type == 'testcase':  
            file_path = 'templates/excel/TestcaseDemo.xlsx'
            
            if not os.path.exists(file_path):
                return HttpResponse("File not Found", status=404)

            with open(file_path, 'rb') as excel_file:
                response = HttpResponse(
                    excel_file.read(),
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                response["Content-Disposition"] = 'attachment; filename="TestcaseDemo.xlsx"'
                return response

        return HttpResponse("Invalid Request", status=400)
    

@extend_schema(
    summary="Retrieve and Create Script Issues",
    description=(
        "This endpoint allows you to retrieve all script issues associated with a "
        "specific test case identified by its ID.\n\n"
        "You can also create a new script issue by providing the required details in the request body."
    ),
    tags=["TestCase Module APIS"]
)
class ScriptIssueView(generics.ListAPIView):

    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = ScriptIssueList
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = ScriptIssue.objects.filter(script=self.kwargs.get("id"))
        return queryset


class ScriptIssueCreateView(cgenerics.CustomCreateAPIView):

    serializer_class = ScriptIssueSerializer

    def get_serializer_context(self):
        return {
            "request": self.request
        }

@extend_schema(
    summary="Retrieve, Update, and Delete Script Issue",
    description=(
        "This endpoint allows you to retrieve, update, or delete a specific script issue identified by its ID.\n\n"
        "You can update the script issue by providing the required fields in the request body. "
        "To delete a script issue, simply send a DELETE request to this endpoint."
    ),
    tags=["TestCase Module APIS"]
)
class ScriptIssueDetailView(cgenerics.CustomRetrieveUpdateDestroyAPIView):

    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = ScriptIssueSerializer

    def get_object(self):
        queryset = ScriptIssue.objects.select_related('script', 'created_by', 'resolved_by').prefetch_related(
            Prefetch("comment", queryset=Comment.objects.only('comments', 'created_by'))
        ).get(id=self.kwargs.get('id'))

        return queryset


@extend_schema(
    summary="Retrieve and Edit Comment",
    description=(
        "This endpoint allows users to retrieve a specific comment by its ID and update the comment's text.\n\n"
        "To update a comment, provide the new text in the request body."
    ),
    tags=["TestCase Module APIS"]
)
class CommentEditView(cgenerics.CustomRetrieveUpdateDestroyAPIView):

    serializer_class = CommentSerializer
    permission_classes = [CommentPermission, ]

    def get_object(self):
        queryset = Comment.objects.select_related('created_by').get(id=self.kwargs['pk'])
        return queryset


class TestCaseScriptList(generics.ListAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = TestCaseScriptListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = TestCaseScript.objects.select_related('natCo').filter(testcase=self.kwargs['pk']).only(
            "id", "script_name", "script_location", "script_type", "natCo"
        )
        return queryset


class TestCaseScriptView(cgenerics.CustomCreateAPIView):

    serializer_class = TestcaseScriptSerializer


class TestcaseScriptDetailView(cgenerics.CustomRetrieveUpdateDestroyAPIView):

    serializer_class = TestcaseScriptSerializer

    def get_object(self):
        try:
            queryset = TestCaseScript.objects.select_related('natCo', 'language', 'device', 'developed_by',
                                                             'modified_by', 'reviewed_by').get(id=self.kwargs.get('pk'))
        except Exception as e:
            logging.error(str(e))
            return None
        return queryset


@extend_schema(
    summary="List and Create Comments",
    description=(
        "This endpoint allows users to retrieve a list all the comments of a Script Issue and create new comments"
        " for a Script Issue\n\n"
        "To create a new comment, provide the required fields in the request body, such as 'text' and 'author'."
    ),
    tags=["TestCase Module APIS"]
)
class CommentsView(generics.ListCreateAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    serializer_class = CommentSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Comment.objects.filter(object_id=self.kwargs['id'])
        return queryset

    def get_serializer_context(self):
        return {
            'object_id': self.kwargs.get('id', None)
        }


class IssuesList(generics.ListAPIView):

    authentication_classes = (JWTAuthentication, )
    serializer_class = IssuesListSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = [
        'status'
    ]

    def get_queryset(self):
        status_order = Case(
            When(status='open', then=Value(1)),
            When(status='under_review', then=Value(2)),
            When(status='closed', then=Value(3)),
            output_field=IntegerField()
        )
        queryset = ScriptIssue.objects.all().order_by(status_order)
        return queryset

class TagsList(cgenerics.CustomListCreateAPIView):

    pagination_class = CustomPagination
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.all()
    
class TagsDetails(cgenerics.CustomRetrieveUpdateDestroyAPIView):

    serializer_class = TagSerializer
    lookup_field = 'id'

    def get_object(self):
        return get_object_or_404(Tag, id=self.kwargs.get('id'))

class TestCaseHistory(generics.GenericAPIView):

    serializer_class = TestCaseHistoryModelSerializer

    
    def __init__(self, **kwargs) -> None:
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    def get_queryset(self):
        return TestCaseHistoryModel.objects.filter(testcase=self.kwargs.get('id'))

    def get(self, request, *args, **kwargs):
        try:
            response = self.get_serializer(self.get_queryset(), many=True, context={"request": request})
            if response.data:
                self.response_format['status'] = True
                self.response_format['status_code'] = status.HTTP_200_OK
                self.response_format['data'] = response.data
                return Response(self.response_format, status=status.HTTP_200_OK)
            else:
                self.response_format['status'] = False
                self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
                self.response_format['message'] = "No data Found"
                return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)
        except serializers.ValidationError as err:
            default_error = {
                key: value[0] if isinstance(value, list) else value for key, value in err.detail.items()
            }
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
            self.response_format['data'] = 'Error'
            self.response_format['message'] = default_error
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.response_format['status'] = False
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['message'] = {"error": str(e)}
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchView(generics.ListAPIView):


    serializer_class = TestCaseSerializerList
    pagination_class = CustomPagination

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        tags = self.request.query_params.get('tags', None)
        jira_id = self.request.query_params.get('jira_id', None).split('-')[1] if self.request.query_params.get('jira_id') else None
        query = Q()
        if name:
            query |= Q(name__icontains=name)
        if tags:
            query |= Q(tags__name__icontains=tags)
        if jira_id:
            query |= Q(jira_id__icontains=jira_id)
        return TestCaseModel.objects.filter(query).distinct()


class SearchTags(generics.ListAPIView):

    serializer_class = TestCaseSerializerList
    pagination_class = CustomPagination

    
class TestcaseCommentView(cgenerics.CustomListCreateAPIView):

    serializer_class = CommentSerializer
    
    def get_queryset(self):
        queryset = Comment.objects.filter(object_id=self.kwargs.get('id'))
        return queryset

    def get_serializer_context(self):
        return {
            "object_id": self.kwargs.get('id', None),
            "instance": 'TestCaseModel'
        }
    
    def post(self, request, *args, **kwargs):
        self.response_format["message"] = "New Comment Added"
        return super().post(request, *args, **kwargs)
    

class TestCaseCommentEditView(cgenerics.CustomRetrieveUpdateDestroyAPIView):

    serializer_class = CommentSerializer
    permission_classes = [CommentPermission, ]

    def get_object(self):
        queryset = Comment.objects.select_related('created_by').get(id=self.kwargs['id'])
        return queryset
    

class CommentCreateView(cgenerics.CustomCreateAPIView):

    serializer_class = CommentSerializer

    def get_serializer_context(self):
        return {
            "object_id": self.kwargs.get('id', None),
            "instance": "ScriptIssue"
            
        }
    
    def post(self, request, *args, **kwargs):
        self.response_format['message'] = "TestCase Created Successfull"
        return super().post(request, *args, **kwargs)
    

class NatCoStatusView(generics.ListAPIView):

    queryset = NatcoStatus.objects.all()
    serializer_class = NatcoStatusSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = [
        "natco",
        "device",
        "applicable"
    ]

# ----------------------------------------------------------------------------------------------------------------------

class TestcaseTypeOptionView(cgenerics.OptionAPIView):

    queryset = TestcaseTypes.objects.all()
    serializer_class = TestCaseTypeOptionSerializer


class TestcaseTypeView(cgenerics.CustomCreateAPIView):

    serializer_class = TestCaseTypeSerializer


class ModulAPIView(APIView):

    def get(self, request, *args, **kwargs):
        queryset = TestCaseModel.objects.only('name')
        lst = set()
        for item in queryset:
            x = get_testcase_module(item.name)
            lst.add(x)
        try:
            l = []
            for i in lst:
                instance = Module.objects.filter(name=i).first()
                if not instance:
                    _temp = {
                        "name": i
                    }
                    l.append(Module(**_temp))
            Module.objects.bulk_create(l)
            return Response("Success")
        except Exception as e:
            print(e)
            return Response("Fail")


class MapModuleViewAPI(APIView):

    def get(self, request, *args, **kwargs):
        queryset = TestCaseModel.objects.all()
        try:
            for item in queryset:
                module = get_testcase_module(item.name)
                get_module = get_object_or_404(Module, name=module)
                setattr(item, 'module', get_module)
                print(item.module)
            instance = TestCaseModel.objects.bulk_update(queryset, fields=['module'])
            return Response("Success")
        except Exception as e:
            print(e)
            return Response("Fail")