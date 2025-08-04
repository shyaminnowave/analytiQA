from rest_framework.views import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from apps.nightly_sanity.apis.serializers import ReleaseSerializer, ApkFilesSerializer, NatcoSerializer, ApiFileNameSerializer, TestExecutionSerializer, TestFunctionalitySerializer
from analytiQA.helpers import custom_generics as c
from apps.core.pagination import CustomPagination
from collections import defaultdict
from django.db.models.functions import Replace
from apps.nightly_sanity.models import ApkFiles, ApkInstallations, Releases, StbNodes, TestExecutions, TestIterations, TestCases

# Create your views here.


class ReleaseListView(generics.ListAPIView):
    """
    API view to list all releases.
    """
    queryset = Releases.objects.using('sanity').all()
    serializer_class = ReleaseSerializer
    pagination_class = CustomPagination


class NatcoListView(generics.ListAPIView):
    """
    API view to list all NATCOs.
    """
    queryset = ApkFiles.objects.using('sanity').only('natco').distinct('natco')
    serializer_class = NatcoSerializer
    pagination_class = CustomPagination


class NatcoBuildView(generics.ListAPIView):

    def get_queryset(self):
        natco = self.kwargs.get('natco')
        return ApkFiles.objects.using('sanity').filter(natco=natco).only('filename')

    serializer_class = ApiFileNameSerializer
    pagination_class = CustomPagination


class ApkListView(generics.ListAPIView):
    """
    API view to list all APK files.
    """
    queryset = ApkFiles.objects.using('sanity').all()
    serializer_class = ApkFilesSerializer
    pagination_class = CustomPagination


class TestFunctionalityListView(generics.ListAPIView):

    """
    API view to list all test functionalities.
    """
    queryset = TestCases.objects.using('sanity').only('functionality').distinct('functionality')
    serializer_class = TestFunctionalitySerializer    
    pagination_class = CustomPagination



class BuildMetrixView(generics.GenericAPIView):
    """
    A demo API view to illustrate the use of custom generics.
    """
    
    serializer_class = TestExecutionSerializer
    queryset = TestExecutions.objects.using('sanity').all()

    def get_apk_test_results_v1(self):
        """
        Generate APK test results grouped by build version.
        Process build version in Python after getting data from DB.
        """
        natco = self.request.GET.get('natco', None)
        print(f"Received NATCO: {natco}")
        
        # Get all APK files with their related test executions
        apk_results = defaultdict(lambda: defaultdict(lambda: {'failed': 0, 'total': 0}))
        
        # Query to get test executions for each APK file
        test_executions = TestExecutions.objects.using('sanity').select_related(
            'stb_node', 'test'
        ).filter(
            stb_node__apkinstallations__apk__natco=natco,
            stb_node__apkinstallations__apk__isnull=False,
            overall_status__isnull=False
        ).values(
            'stb_node__apkinstallations__apk__filename',  # Get filename instead of property
            'test__functionality',
            'overall_status',
            'passed_iterations',
            'failed_iterations',
            'total_iterations'
        ).distinct()
        
        # Process the results
        for execution in test_executions:
            filename = execution['stb_node__apkinstallations__apk__filename']
            functionality = execution['test__functionality']
            
            # Extract build version from filename in Python
            build_version = None
            if filename and '-' in filename:
                parts = filename.split('-')
                if len(parts) > 2:
                    build_version = parts[2]  # Get the build version part
            
            # Use build_version as key instead of filename
            key = build_version if build_version else filename
            
            if key and functionality:
                # Use passed/total iterations if available, otherwise use overall_status
                if execution['total_iterations'] and execution['failed_iterations']:
                    failed = execution['failed_iterations']
                    total = execution['total_iterations']
                else:
                    # If iterations not available, treat overall_status as binary
                    failed = 1 if execution['overall_status'].lower() in ['failed'] else 0
                    total = 1
                
                apk_results[key][functionality]['failed'] += failed
                apk_results[key][functionality]['total'] += total
        
        # Calculate percentages
        final_results = {}
        for build_version, functionalities in apk_results.items():
            final_results[build_version] = {}
            for functionality, stats in functionalities.items():
                if stats['total'] > 0:
                    percentage = round((stats['failed'] / stats['total']) * 100)
                    final_results[build_version][functionality] = f"{percentage}%"
                else:
                    final_results[build_version][functionality] = "0%"
        
        return final_results

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve test execution data.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {   
                'status_code': status.HTTP_200_OK,
                'status': True,    
                'data': self.get_apk_test_results_v1(),
                'message': 'Test execution data retrieved successfully.',
            },
            status=status.HTTP_200_OK)


class DetailView(APIView):

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve detailed information.
        """
        # Example of how to use the serializer
        queryset = TestExecutions.objects.using('sanity').all()
        pass