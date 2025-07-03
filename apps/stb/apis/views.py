import logging
from rest_framework.views import APIView, Response
from apps.stb.utils import get_branch
from apps.stb.models import Language, STBManufacture, NatCo, NatcoRelease, STBNode, STBNodeConfig, STBAuthToken, \
    NatCoFirmware
from apps.stb.apis.serializers import LanguageSerializer, STBManufactureSerializer, NactoSerializer, \
    NatcoOptionSerializer, LanguageOptionSerializer, DeviceOptionSerializer, NatcoReleaseOptionSerializer, \
    NatcoReleaseInfo, NatcoFirmwareOptionSerializer, NatcoFirmwareSerializer, RunTestCaseSerializer
from apps.core.pagination import CustomPagination
from analytiQA.helpers import custom_generics as c
from django.shortcuts import get_object_or_404
from rest_framework.renderers import TemplateHTMLRenderer
from apps.stb.stbtester import STBClient


logger = logging.getLogger(__name__)

class LanguageListView(c.CustomListCreateAPIView):

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    pagination_class = CustomPagination
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class LanguageDetailView(c.CustomRetrieveUpdateDestroyAPIView):

    def get_object(self):
        queryset = get_object_or_404(Language, pk=self.kwargs.get('pk'))
        return queryset

    serializer_class = LanguageSerializer


class StbManufactureListView(c.CustomListCreateAPIView):

    queryset = STBManufacture.objects.all()
    serializer_class = STBManufactureSerializer
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        return super(StbManufactureListView, self).get(request, *args, **kwargs)


class StbManufactureDetailView(c.CustomRetrieveUpdateDestroyAPIView):

    def get_object(self):
        queryset = get_object_or_404(STBManufacture, pk=self.kwargs.get('pk'))
        return queryset

    serializer_class = STBManufactureSerializer


class NatCoAPIView(c.CustomListCreateAPIView):

    serializer_class = NactoSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return NatCo.objects.prefetch_related('manufacture', 'language')


class NatCoDetailAPIView(c.CustomRetrieveUpdateDestroyAPIView):

    def get_object(self):
        queryset = get_object_or_404(NatCo, pk=self.kwargs.get('pk'))
        return queryset

    serializer_class = NactoSerializer


class NatCoOptionView(c.OptionAPIView):

    queryset = NatCo.objects.only('id', 'natco')
    serializer_class = NatcoOptionSerializer


class LanguageOptionView(c.OptionAPIView):

    serializer_class = LanguageOptionSerializer

    def get_queryset(self):
        if not self.request.GET.get('natCo'):
            return Language.objects.only('id', 'language_name')
        natCo = NatCo.objects.get(natco=self.request.GET.get('natCo'))
        return natCo.language.all()


class DeviceOptionView(c.OptionAPIView):

    serializer_class = DeviceOptionSerializer

    def get_queryset(self):
        if not self.request.GET.get('natCo'):
            return STBManufacture.objects.only('id', 'name')
        devices = STBManufacture.objects.filter(devices__natco=self.request.GET.get('natCo'))
        return devices


class NatCoReleaseOptionView(c.OptionAPIView):

    queryset = NatcoRelease.objects.all()
    serializer_class = NatcoReleaseOptionSerializer


class NatCoFirmwareOptionView(c.OptionAPIView):

    queryset = NatCoFirmware.objects.all()
    serializer_class = NatcoFirmwareOptionSerializer


class NatCoFirmwareView(c.CustomListCreateAPIView):

    serializer_class = NatcoFirmwareSerializer
    pagination_class = CustomPagination
    queryset = NatCoFirmware.objects.all()


class NatCoFirmwareDetailView(c.CustomRetrieveUpdateDestroyAPIView):

    serializer_class = NatcoFirmwareSerializer

    def get_object(self):
        queryset = get_object_or_404(NatCoFirmware, pk=self.kwargs.get('pk'))
        return queryset


class NatcoInfoView(c.CustomListCreateAPIView):

    pagination_class = CustomPagination
    serializer_class = NatcoReleaseInfo
    queryset = NatcoRelease.objects.all()


class GetSTBBranchAPI(APIView):

    def get(self, request, *args, **kwargs):
        branches = get_branch(
            auth="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",
            repo="stb-tester/stb-tester-test-pack-innowave"
        )
        if not branches:
            return Response({"error": "No branches"})
        return Response(branches)


class STBRunnerPackAPIView(APIView):

    @staticmethod
    def get_stb_nodes():
        stb_nodes = STBNode.objects.all()
        lst = []
        for stb in stb_nodes:
            lst.append(stb.node_id)
        return lst

    @staticmethod
    def get_branches():
        branches = get_branch(
            auth="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",
            repo="stb-tester/stb-tester-test-pack-innowave"
        )
        return branches if branches else []

    def get(self, request, *args, **kwargs):
        data = dict()
        stb_nodes = self.get_branches()
        get_stb_nodes = self.get_stb_nodes()
        data['stb_nodes'] = stb_nodes
        data['get_stb_nodes'] = get_stb_nodes
        return Response(data)


class STBTestcaseView(APIView):

    def get(self, request, *args, **kwargs):
        test_pack = request.GET.get('branch')
        client = STBClient(
            request=self.request,
        )
        testcases = client.get_testcase_names(test_pack)
        return Response(testcases)


class StbSchedulerView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        branch_list = get_branch(
            auth='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',
            repo='stb-tester/stb-tester-test-pack-innowave'
        )
        stb_branches = STBClient(request=self.request,).get_node_status()
        return Response({
            "user": request.user,
            "branches": branch_list,
            "stb_nodes": [b for b in stb_branches]
        })


class STBRunnerAPIView(APIView):

    serializer_class = RunTestCaseSerializer

    def add_schedule_data(self, data):
        # STBScheduleModel.objects.create(
        #     end_time = data['end_time'],
        #     job_id = data['job_uid'],
        #     job_url = data['job_url'],
        #     log_url = data['log_url'],
        #     result_counts = data['result_counts'],
        #     start_time = data['start_time'],
        #     status = data['status'],
        #     triage_url = data['triage_url'],
        # )
        return

    def post(self, request, *args, **kwargs):
        serializer = RunTestCaseSerializer(
            data=request.data
        )
        if serializer.is_valid():
            client = STBClient(
                request=self.request,
            )
            result = client.run_testcase_by_name(
                node_id = request.data.get('node_id'),
                test_pack_revision = request.data.get('test_pack_revision'),
                test_cases = request.data.get('test_cases'),
                remote_control = request.data.get('remote_control'),
            )
            if result:
                # self.add_schedule_data(
                #     data = result
                # )
                return Response({
                    "status": "Success",
                    "data": result
                })
            else:
                return Response({
                    "status": "Failed",
                    "data": "Error"
                })
        return Response({
                    "status": "Failed",
                    "data": "Error"
                })
