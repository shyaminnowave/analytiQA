import logging
from rest_framework.views import APIView, Response
from apps.stb.models import Language, STBManufacture, NatCo, NatcoRelease, STBNode, STBNodeConfig, STBToken, STBUrl
from apps.stb.apis.serializers import LanguageSerializer, STBManufactureSerializer, NactoSerializer, \
    NatcoOptionSerializer, LanguageOptionSerializer, DeviceOptionSerializer, NatcoReleaseOptionSerializer, \
    NatcoReleaseInfo
from apps.core.pagination import CustomPagination
from analytiQA.helpers import custom_generics as c
from django.shortcuts import get_object_or_404
from rest_framework import generics
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


class NatcoInfoView(generics.ListCreateAPIView):

    pagination_class = CustomPagination
    serializer_class = NatcoReleaseInfo
    queryset = NatcoRelease.objects.all()


class STBRunnerAPIView(APIView):

    def post(self, request, *args, **kwargs):
        stb = STBClient()
        runner = stb.run_testcase_by_name(
            node_id = request.data.get('node_id'),
            test_cases = request.data.get('test_cases'),
            test_pack_revision = request.data.get('test_pack_revision'),
            remote_control = request.data.get('remote_control')
        )
        return Response(runner)