from defectdojo import uploader
from defectdojo.exceptions import (EngagementIdNotFoundException,
                                   ProductIdNotFoundException)
from drf_spectacular.utils import extend_schema
from executions.filters import ExecutionFilter
from executions.models import Execution
from executions.serializers import ExecutionSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

# Create your views here.


class ExecutionViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Execution.objects.all()
    serializer_class = ExecutionSerializer
    filterset_class = ExecutionFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(task__target__project__members=self.request.user)

    @extend_schema(request=None, responses={200: None})
    @action(detail=True, methods=['POST'], url_path='defect-dojo', url_name='defect-dojo')
    def defect_dojo(self, request, pk):
        execution = self.get_object()
        try:
            uploader.upload_executions([execution])
            return Response(status=status.HTTP_200_OK)
        except (ProductIdNotFoundException, EngagementIdNotFoundException) as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
