from apps.stb.models import Language, STBManufacture, NatCo, NatcoRelease
from apps.stb.apis.serializers import LanguageSerializer, STBManufactureSerializer, NactoSerializer, \
    NatcoOptionSerializer, LanguageOptionSerializer, DeviceOptionSerializer, NatcoReleaseInfo
from apps.core.pagination import CustomPagination
from analytiQA.helpers import custom_generics as c
from django.shortcuts import get_object_or_404
from rest_framework import generics


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
        natCo = NatCo.objects.get(natco=self.request.GET.get('natCo'))
        return natCo.manufacture.all()


class NatcoInfoView(generics.ListCreateAPIView):

    pagination_class = CustomPagination
    serializer_class = NatcoReleaseInfo
    queryset = NatcoRelease.objects.all()
