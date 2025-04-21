from rest_framework.viewsets import GenericViewSet
from analytiQA.helpers.custom_generics import GenericAPIView, CustomCreateAPIView, CustomRetrieveDestroyAPIView, \
                        CustomRetriveAPIVIew, CustomDestroyAPIView, CustomUpdateAPIView, CustomGenericsAPIView, \
                        CustomRetrieveUpdateAPIView, CustomRetrieveUpdateDestroyAPIView, mixins


class QAModelViewSet(CustomCreateAPIView,
                     CustomRetriveAPIVIew,
                     CustomUpdateAPIView,
                     CustomDestroyAPIView,
                     mixins.ListModelMixin,
                     GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass




