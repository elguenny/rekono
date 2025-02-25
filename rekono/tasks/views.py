from typing import Any

from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from targets.models import Target
from tasks import services
from tasks.enums import Status
from tasks.filters import TaskFilter
from tasks.models import Task
from tasks.queue import producer
from tasks.serializers import TaskSerializer

# Create your views here.


class TaskViewSet(GenericViewSet, CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin):
    '''Task ViewSet that includes: get, retrieve, create amd cancel features.'''

    queryset = Task.objects.all().order_by('-id')
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
    # Fields used to search tasks
    search_fields = ['target__target', 'process__name', 'process__steps__tool__name', 'tool__name']

    def get_queryset(self) -> QuerySet:
        '''Get the queryset that the user is allowed to get, based on project members.

        Returns:
            QuerySet: Queryset
        '''
        return super().get_queryset().filter(target__project__members=self.request.user)

    def perform_create(self, serializer: TaskSerializer) -> None:
        '''Create a new instance using a serializer.

        Args:
            serializer (TaskSerializer): Serializer to use in the instance creation
        '''
        # Check if current user can execute tasks against this target based on project membership
        project_check = Target.objects.filter(
            id=serializer.validated_data.get('target').id,
            project__members=self.request.user
        ).exists()
        if not project_check:
            # Current user can't execute tasks against this target
            raise PermissionDenied()
        serializer.save(executor=self.request.user)                             # Include current user as executor

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        '''Cancel task.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        '''
        instance = self.get_object()
        try:
            services.cancel_task(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={200: TaskSerializer})
    @action(detail=True, methods=['POST'], url_path='repeat', url_name='repeat')
    def repeat_task(self, request: Request, pk: str) -> Response:
        '''Repeat task execution.

        Args:
            request (Request): Received HTTP request
            pk (str): Id of the task to repeat

        Returns:
            Response: HTTP response
        '''
        task = self.get_object()
        if task.status in [Status.REQUESTED, Status.RUNNING]:
            # If task status is requested or running, it can't be repeated
            return Response('Execution is still running', status=status.HTTP_400_BAD_REQUEST)
        # Create a new task from the original one
        new_task = Task.objects.create(
            target=task.target,
            process=task.process,
            tool=task.tool,
            configuration=task.configuration,
            intensity=task.intensity,
            executor=request.user
        )
        new_task.wordlists.set(task.wordlists.all())                            # Add wordlists from original task
        producer(new_task)                                                      # Enqueue new task
        serializer = TaskSerializer(instance=new_task)                          # Return new task data
        return Response(serializer.data, status=status.HTTP_201_CREATED)
