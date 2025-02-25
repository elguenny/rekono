from django_filters.rest_framework import FilterSet, filters
from likes.filters import LikeFilter
from tools.models import Configuration, Tool


class ToolFilter(LikeFilter):
    '''FilterSet to filter and sort Tool entities.'''

    o = filters.OrderingFilter(fields=('name', 'stage', 'likes_count'))         # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = Tool
        fields = {                                                              # Filter fields
            'name': ['exact', 'icontains'],
            'command': ['exact', 'icontains'],
            'configurations': ['exact'],
            'configurations__name': ['exact', 'icontains'],
            'arguments__inputs__type__name': ['exact'],
            'configurations__outputs__type__name': ['exact'],
            'stage': ['exact']
        }


class ConfigurationFilter(FilterSet):
    '''FilterSet to filter and sort Configuration entities.'''

    o = filters.OrderingFilter(fields=('tool', 'name'))                         # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = Configuration
        fields = {                                                              # Filter fields
            'tool': ['exact'],
            'tool__name': ['exact', 'icontains'],
            'tool__command': ['exact', 'icontains'],
            'tool__stage': ['exact'],
            'name': ['exact', 'icontains'],
            'default': ['exact'],
            'tool__arguments__inputs__type__name': ['exact'],
            'outputs__type__name': ['exact'],
        }
