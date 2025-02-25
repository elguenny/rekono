from typing import Any
from urllib.request import Request

from api.filters import RekonoFilterBackend
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from findings.enums import DataType
from findings.filters import (CredentialFilter, ExploitFilter, HostFilter,
                              OSINTFilter, PathFilter, PortFilter,
                              TechnologyFilter, VulnerabilityFilter)
from findings.models import (OSINT, Credential, Exploit, Finding, Host, Path,
                             Port, Technology, Vulnerability)
from findings.serializers import (CredentialSerializer, ExploitSerializer,
                                  HostSerializer, OSINTSerializer,
                                  PathSerializer, PortSerializer,
                                  TechnologySerializer,
                                  VulnerabilitySerializer)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import (DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from targets.serializers import TargetSerializer

# Create your views here.


class FindingBaseView(GenericViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin):
    '''Common finding ViewSet that includes: get, retrieve, enable and disable features.'''

    # Replace DjangoFilterBackend by RekonoFilterBackend to allow filters by N-M relations like 'executions' field.
    filter_backends = [RekonoFilterBackend, SearchFilter, OrderingFilter]

    def get_queryset(self) -> QuerySet:
        '''Get the Finding queryset that the user is allowed to get, based on project members.

        Returns:
            QuerySet: Execution queryset
        '''
        queryset = super().get_queryset()
        # Prevent warnings when access the API schema in SwaggerUI or Redoc
        # This is caused by the use of RekonoFilterBackend, that is required for Findings entities
        if self.request.user.id:
            return queryset.filter(executions__task__target__project__members=self.request.user)
        return None

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        '''Disable finding.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        '''
        finding: Finding = self.get_object()
        finding.is_active = False
        finding.save(update_fields=['is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None, responses={201: None})
    @action(detail=True, methods=['POST'], url_path='enable', url_name='enable')
    def enable(self, request: Request, pk: str) -> Response:
        '''Enable finding.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP response
        '''
        finding: Finding = self.get_object()
        finding.is_active = True
        finding.save(update_fields=['is_active'])
        return Response(status=status.HTTP_201_CREATED)


class OSINTViewSet(FindingBaseView):
    '''OSINT ViewSet that includes: get, retrieve, enable, disable, import in DD and target creation features.'''

    queryset = OSINT.objects.all().order_by('-id')
    serializer_class = OSINTSerializer
    filterset_class = OSINTFilter
    search_fields = ['data', 'source']                                          # Fields used to search OSINTs

    @extend_schema(request=None, responses={201: TargetSerializer})
    @action(detail=True, methods=['POST'], url_path='target', url_name='target')
    def target(self, request: Request, pk: str) -> Response:
        '''Target creation from OSINT data.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP response
        '''
        osint = self.get_object()
        if osint.data_type in [DataType.IP, DataType.DOMAIN]:                   # Only supported for IPs and Domains
            serializer = TargetSerializer(data={'project': osint.get_project().id, 'target': osint.data})
            if serializer.is_valid():
                target = serializer.create(serializer.validated_data)           # Target creation
                return Response(TargetSerializer(target).data, status=status.HTTP_201_CREATED)
        return Response(
            {'data_type': ['Unsupported option for this OSINT data type']}, status=status.HTTP_400_BAD_REQUEST
        )


class HostViewSet(FindingBaseView):
    '''Host ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Host.objects.all().order_by('-id')
    serializer_class = HostSerializer
    filterset_class = HostFilter
    search_fields = [                                                           # Fields used to search Hosts
        'address',
        'port__port', 'port__service',
        'port__path__path',
        'port__technology__name', 'port__technology__version',
        'port__vulnerability__name', 'port__vulnerability__cve',
        'port__vulnerability__cwe', 'port__vulnerability__severity',
        'port__technology__vulnerability__name',
        'port__technology__vulnerability__cve',
        'port__technology__vulnerability__cwe',
        'port__technology__vulnerability__severity',
        'port__vulnerability__exploit__name',
        'port__technology__vulnerability__exploit__name'
    ]


class PortViewSet(FindingBaseView):
    '''Port ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Port.objects.all().order_by('-id')
    serializer_class = PortSerializer
    filterset_class = PortFilter
    search_fields = [                                                           # Fields used to search Ports
        'host__address',
        'port', 'service',
        'path__path',
        'technology__name', 'technology__version',
        'vulnerability__name', 'vulnerability__cve',
        'vulnerability__cwe', 'vulnerability__severity',
        'technology__vulnerability__name', 'technology__vulnerability__cve',
        'technology__vulnerability__cwe', 'technology__vulnerability__severity',
        'vulnerability__exploit__name', 'technology__vulnerability__exploit__name'
    ]


class PathViewSet(FindingBaseView):
    '''Path ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Path.objects.all().order_by('-id')
    serializer_class = PathSerializer
    filterset_class = PathFilter
    search_fields = [                                                           # Fields used to search Paths
        'port__host__address',
        'port__port', 'port__service',
        'path'
    ]


class TechnologyViewSet(FindingBaseView):
    '''Technology ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Technology.objects.all().order_by('-id')
    serializer_class = TechnologySerializer
    filterset_class = TechnologyFilter
    search_fields = [                                                           # Fields used to search Technologies
        'port__host__address',
        'port__port', 'port__service',
        'port__path__path',
        'name', 'version',
        'vulnerability__name', 'vulnerability__cve',
        'vulnerability__cwe', 'vulnerability__severity',
        'vulnerability__exploit__name', 'exploit__name'
    ]


class CredentialViewSet(FindingBaseView):
    '''Credential ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Credential.objects.all().order_by('-id')
    serializer_class = CredentialSerializer
    filterset_class = CredentialFilter
    # Fields used to search Credentials
    search_fields = [
        'technology__port__host__address',
        'technology__port__port', 'technology__port__service',
        'technology__name', 'technology__version',
        'email', 'username'
    ]


class VulnerabilityViewSet(FindingBaseView):
    '''Vulnerability ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Vulnerability.objects.all().order_by('-id')
    serializer_class = VulnerabilitySerializer
    filterset_class = VulnerabilityFilter
    search_fields = [                                                           # Fields used to search Vulnerabilities
        'port__host__address', 'technology__port__host__address',
        'port__port', 'port__service',
        'technology__port__port', 'technology__port__service',
        'port__path__path', 'technology__port__path__path',
        'port__technology__name', 'port__technology__version',
        'technology__name', 'technology__version',
        'name', 'cve', 'cwe', 'severity',
        'exploit__name'
    ]


class ExploitViewSet(FindingBaseView):
    '''Exploit ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Exploit.objects.all().order_by('-id')
    serializer_class = ExploitSerializer
    filterset_class = ExploitFilter
    search_fields = [                                                           # Fields used to search Exploits
        'vulnerability__port__host__address', 'technology__port__host__address',
        'vulnerability__port__port', 'vulnerability__port__service',
        'technology__port__port', 'technology__port__service',
        'vulnerability__port__path__path',
        'technology__port__path__path',
        'vulnerability__port__technology__name', 'vulnerability__port__technology__version',
        'technology__name', 'technology__version',
        'vulnerability__name', 'vulnerability__cve',
        'vulnerability__cwe', 'vulnerability__severity',
        'technology__vulnerability__name', 'technology__vulnerability__cve',
        'technology__vulnerability__cwe', 'technology__vulnerability__severity',
        'title', 'edb_id'
    ]
