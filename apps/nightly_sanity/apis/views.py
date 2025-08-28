import time
from rest_framework.views import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from apps.nightly_sanity.apis.serializers import ReleaseSerializer, ApkFilesSerializer, NatcoSerializer, ApiFileNameSerializer, TestExecutionSerializer, TestFunctionalitySerializer, \
                                                TestIterationSerializer
from analytiQA.helpers import custom_generics as c
from apps.core.pagination import CustomPagination
from collections import defaultdict
from django.db.models.functions import Replace
from django.db.models import Count, Sum
from analytiQA.helpers.renders import ResponseInfo
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, \
    extend_schema_view
from apps.nightly_sanity.models import ApkFiles, ApkInstallations, Releases, StbNodes, TestExecutions, TestIterations, TestCases

# Create your views here.


@extend_schema(
    summary="Returns list of Release",
    description="""
    This endpoint allows authenticated users to retrieve a 
    """,
    tags=['Releases API View']
)
class ReleaseListView(generics.ListAPIView):
    """
    API view to list all releases.
    """
    queryset = Releases.objects.using('sanity').all()
    serializer_class = ReleaseSerializer
    pagination_class = CustomPagination


@extend_schema(
    summary="",
    description="""""",
    tags=['NatCo API List']
)
class NatcoListView(generics.ListAPIView):
    """
    API view to list all NATCOs.
    """
    queryset = ApkFiles.objects.using('sanity').only('natco').distinct('natco')
    serializer_class = NatcoSerializer
    pagination_class = CustomPagination


@extend_schema(tags=['Natco Build API'])
class NatcoBuildView(generics.ListAPIView):

    def get_queryset(self):
        natco = self.kwargs.get('natco')
        return ApkFiles.objects.using('sanity').filter(natco=natco).only('filename')

    serializer_class = ApiFileNameSerializer
    pagination_class = CustomPagination


@extend_schema(tags=['APK List API View'])
class ApkListView(generics.ListAPIView):
    """
    API view to list all APK files.
    """
    queryset = ApkFiles.objects.using('sanity').all()
    serializer_class = ApkFilesSerializer
    pagination_class = CustomPagination


@extend_schema(tags=['Funtionality Listing API'])
class TestFunctionalityListView(generics.ListAPIView):

    """
    API view to list all test functionalities.
    """
    queryset = TestCases.objects.using('sanity').only('functionality').distinct('functionality')
    serializer_class = TestFunctionalitySerializer    
    pagination_class = CustomPagination


@extend_schema(tags=['Graph Data API View'])
class BuildMetrixView(c.CustomRetriveAPIVIew):
    """
    A demo API view to illustrate the use of custom generics.
    """
    
    serializer_class = TestExecutionSerializer

    def get_queryset(self):
        """
        Generate APK test results grouped by build version.
        Process build version in Python after getting data from DB.
        """
        queryset = TestExecutions.objects.using('sanity').filter(
            natco=self.request.GET.get('natco')
        )
        return queryset

    def get_apk_result(self, data):
        result = defaultdict(lambda: defaultdict(dict))
        for entry in data:
            release = entry["get_release"]
            testcase = entry["get_testcase"].upper()  # Uppercase like your example
            result[release][testcase].setdefault("total", 0)
            result[release][testcase].setdefault("failed", 0)

            result[release][testcase]["total"] += entry["total_iterations"]
            result[release][testcase]["failed"] += entry["failed_iterations"]

        # Convert failed/total to percentage
        final_output = {}
        for release, cases in result.items():
            final_output[release] = {}
            for case, counts in cases.items():
                percentage = (counts["failed"] / counts["total"]) * 100 if counts["total"] else 0
                final_output[release][case] = f"{percentage:.0f}%"

        return final_output

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve test execution data.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        if serializer.data:
            self.response_format['data'] = self.get_apk_result(serializer.data)
            self.response_format['message'] = "'%s' avaliable Natco Builds" % self.request.GET.get('natco')
            return Response(self.response_format, status=status.HTTP_200_OK)
        else:
            self.response_format['data'] = None
            self.response_format['messgae'] = "No Natco name '%s'" % self.request.GET.get('natco')
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        

@extend_schema(tags=['Nacto Builds Comparison API View'])
class CompareBuildsAPI(generics.GenericAPIView):
    
    def get_details(self, data):
        grouped = defaultdict(lambda: {"total_passed": 0, "total_failed": 0, "total_error": 0,
        "modules": defaultdict(lambda: {
            "module_passed": 0,
            "module_failed": 0, 
            "module_error": 0,
            "testcases": defaultdict(lambda: {
                    "testcase_passed": 0, 
                    "testcase_failed": 0, 
                    "testcase_error": 0
                })
            })
        })
        for metrix in data:
            release = metrix['get_release']
            module = metrix['get_testcase']
            testcase = metrix['get_testcase_name']
            grouped[release]["total_passed"] += metrix["passed_iterations"]
            grouped[release]["total_failed"] += metrix["failed_iterations"]
            grouped[release]["total_error"] += metrix["error_iterations"]

            grouped[release]['modules'][module]["module_passed"] += metrix["passed_iterations"]
            grouped[release]['modules'][module]["module_failed"] += metrix["failed_iterations"]
            grouped[release]['modules'][module]["module_error"] += metrix["error_iterations"]

            grouped[release]['modules'][module]['testcases'][testcase]["testcase_passed"] += metrix["passed_iterations"]
            grouped[release]['modules'][module]['testcases'][testcase]["testcase_failed"] += metrix["failed_iterations"]
            grouped[release]['modules'][module]['testcases'][testcase]["testcase_error"] += metrix["error_iterations"]
        return grouped
    

    def get(self, request, *args, **kwargs):
        natco = request.GET.get('natco')
        builds = request.GET.get('builds')
        builds_list = builds.split(',')
        if builds:
            _release_build = {
                'release_id__in' : Releases.objects.using('sanity').filter(
                    box_release_info__in=builds_list
                )
            }
        if (natco == None or natco == '') or (builds == None or builds == ''):
            return Response(
                {   
                    'status_code': status.HTTP_200_OK,
                    'status': False,    
                    'data': "No data",
                    'message': 'No data found',
                }, status=status.HTTP_404_NOT_FOUND
            )
        start_time = time.time()
        queryset = TestExecutions.objects.using('sanity').filter(
            overall_status__in=['passed', 'failed'],
            natco=natco,
            **_release_build
            )
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total Time Taken {total_time}")
        serializer = TestExecutionSerializer(queryset, many=True)
        if serializer.data:
            return Response(
                {   
                    'status_code': status.HTTP_200_OK,
                    'status': True,    
                    'data': self.get_details(serializer.data),
                    'message': 'Test execution data retrieved successfully.',
                }, status=status.HTTP_200_OK)
        return Response(
            {   
                'status_code': status.HTTP_200_OK,
                'status': True,    
                'data': None,
                'message': "No Build '%s' Fount for '%s' Natco" % (natco, builds_list)
            },
            status=status.HTTP_200_OK
        )


@extend_schema(tags=['API to Fetch All total Iterations of Build based on Natco'])
class NatcoTotalRunsAPI(generics.GenericAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super().__init__(**kwargs)

    def get_queryset(self):
        queryset = TestExecutions.objects.using('sanity').filter(natco=self.request.GET.get('natco')).values('release_id').annotate(total_sum=Sum('total_iterations'))
        return queryset    

    def get(self, request, *args, **kwargs):
        _data = defaultdict(lambda: int)
        queryset = self.get_queryset()
        if queryset:
            for i in queryset:
                get_build_info = Releases.objects.using('sanity').get(id=i['release_id'])
                _data[get_build_info.box_release_info] = i['total_sum']
            self.response_format['data'] = _data
            self.response_format['status_code'] = status.HTTP_200_OK
            self.response_format['message'] = "Success"
            return Response(
                self.response_format, status=status.HTTP_200_OK
            )
        self.response_format["data"] = None
        self.response_format['status_code'] = status.HTTP_404_NOT_FOUND
        self.response_format['message'] = "Error"
        return Response(
            self.response_format, status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(tags=['Testcase Failure Details API View'])
class BuildFailureViewAPI(c.CustomGenericsAPIView):

    def get_queryset(self):
        print(self.request.GET.get('builds'))
        sql = """
            SELECT * FROM test_iterations as ti 
                LEFT JOIN (
                    SELECT te.id, testcase_name, natco, box_release_info
                    FROM test_executions as te 
                    LEFT JOIN test_cases as tc ON te.testcase_number = tc.id
                    LEFT JOIN releases as re ON te.release_id = re.id
                ) as pl ON ti.execution_id = pl.id 
                WHERE natco = %s 
                AND testcase_name = %s
                AND box_release_info = %s
                AND (result = 'fail' or result = 'error');
        """
        print(f"SQL: {sql}")
        print(f"Params: {[self.request.GET.get('natco'), self.request.GET.get('testcase'), self.request.GET.get('builds')]}")
        queryset = TestIterations.objects.using('sanity').raw(sql,
                                                              params=[self.request.GET.get('natco'), self.request.GET.get('testcase'), self.request.GET.get('builds')])
        print("Actual query results:")
        for item in queryset:
            print(f"Item: {item}")
            print(f"Result: {item.result}")
            print(f"Box release info: {getattr(item, 'box_release_info', 'NOT FOUND')}")
            print("---")
        return queryset
    
    serializer_class = TestIterationSerializer
    
    def get(self, request, *args, **kwargs):
        natco = request.GET.get('natco', None)
        testcase = request.GET.get('testcase', None)
        builds = request.GET.get('builds', None)
        if natco and testcase and builds :
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            if serializer.data:
                return Response(
                    {   
                        'status_code': status.HTTP_200_OK,
                        'status': True,    
                        'data': serializer.data,
                        'message': 'Test execution data retrieved successfully.',
                    }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {   
                        'status_code': status.HTTP_200_OK,
                        'status': True,    
                        'data': None,
                        'message': "No Error Logs of '%s' for the testcase '%s'" % (request.GET.get('natco'), (request.GET.get('testcase'))),
                    }, status=status.HTTP_200_OK)
        return Response(
            {   
                'status_code': status.HTTP_200_OK,
                'status': True,    
                'data': None,
                'message': "QueryParams Cannot be Empty",
            }, status=status.HTTP_200_OK)
