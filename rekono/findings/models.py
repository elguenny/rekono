from typing import Any, Collection, Dict, Iterable, Optional, Tuple

from defectdojo.api.constants import DD_FINDING_DATE_FORMAT
from django.core.exceptions import ValidationError
from django.db import DEFAULT_DB_ALIAS, models
from executions.models import Execution
from findings.enums import DataType, OSType, PortStatus, Protocol, Severity
from findings.utils import get_unique_filter

# Create your models here.


def create_finding_foreign_key(model, name):
    return models.ForeignKey(
        model,
        related_name=name,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )


class Finding(models.Model):
    execution = models.ForeignKey(Execution, related_name='%(class)s', on_delete=models.CASCADE)
    creation = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    reported_to_defectdojo = models.BooleanField(default=False)

    key_fields = []

    class Meta:
        abstract = True
        ordering = ['-id']

    def validate_unique(self, exclude: Optional[Collection[str]] = None) -> None:
        unique_filter = get_unique_filter(self.key_fields, vars(self), self.execution)
        search = self._meta.model.objects.filter(**unique_filter)
        if search.exists():
            raise ValidationError('Unique constraint violation')
 
    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = DEFAULT_DB_ALIAS,
        update_fields: Optional[Iterable[str]] = None
    ) -> None:
        if not self.id:
            self.validate_unique()
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def __hash__(self) -> int:
        hash_fields = []
        unique_filter = get_unique_filter(self.key_fields, vars(self), self.execution)
        for value in unique_filter.values():
            hash_fields.append(value)
        return hash(tuple(hash_fields))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            equals = True
            unique_filter = get_unique_filter(o.key_fields, vars(o), o.execution)
            for key, value in get_unique_filter(self.key_fields, vars(self), self.execution).items():
                equals = equals and (unique_filter[key] == value)
            return equals
        return False

    def get_project(self) -> Any:
        return self.execution.task.target.project


class OSINT(Finding):
    data = models.TextField(max_length=250)
    data_type = models.TextField(max_length=10, choices=DataType.choices)
    source = models.TextField(max_length=50, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)

    key_fields = [
        {'name': 'data', 'is_base': False},
        {'name': 'data_type', 'is_base': False}
    ]

    def defect_dojo(self):
        return {
            'title': f'{self.data_type} found using OSINT techniques',
            'description': self.data,
            'severity': Severity.MEDIUM.value,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }


class Host(Finding):
    address = models.TextField(max_length=30)
    os = models.TextField(max_length=250, blank=True, null=True)
    os_type = models.TextField(max_length=10, choices=OSType.choices, default=OSType.OTHER)

    key_fields = [
        {'name': 'address', 'is_base': False}
    ]

    def defect_dojo(self):
        description = self.address
        if self.os:
            description += '- {self.os} ({self.os_type})'
        return {
            'title': 'Host discovered',
            'description': description,
            'severity': Severity.INFO.value,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }


class Enumeration(Finding):
    host = create_finding_foreign_key(Host, 'enumeration')
    port = models.IntegerField()
    port_status = models.TextField(
        max_length=15,
        choices=PortStatus.choices,
        default=PortStatus.OPEN
    )
    protocol = models.TextField(max_length=5, choices=Protocol.choices, blank=True, null=True)
    service = models.TextField(max_length=50, blank=True, null=True)

    key_fields = [
        {'name': 'host_id', 'is_base': True},
        {'name': 'port', 'is_base': False}
    ]

    def defect_dojo(self):
        description = f'{self.port} - {self.port_status} - {self.protocol} - {self.service}'
        return {
            'title': 'Port discovered',
            'description': description,
            'severity': Severity.INFO.value,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }


class Endpoint(Finding):
    enumeration = create_finding_foreign_key(Enumeration, 'endpoint')
    endpoint = models.TextField(max_length=500)
    status = models.IntegerField(blank=True, null=True)

    key_fields = [
        {'name': 'enumeration_id', 'is_base': True},
        {'name': 'endpoint', 'is_base': False}
    ]

    def defect_dojo(self):
        return {
            'protocol': self.enumeration.service,
            'host': self.enumeration.host.address,
            'port': self.enumeration.port,
            'path': self.endpoint
        }


class Technology(Finding):
    enumeration = create_finding_foreign_key(Enumeration, 'technology')
    name = models.TextField(max_length=100)
    version = models.TextField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=200, blank=True, null=True)
    related_to = create_finding_foreign_key('Technology', 'related_technologies')
    reference = models.TextField(max_length=250, blank=True, null=True)

    key_fields = [
        {'name': 'enumeration_id', 'is_base': True},
        {'name': 'name', 'is_base': False}
    ]

    def defect_dojo(self):
        return {
            'title': f'Technology {self.name} detected',
            'description': self.description if self.description else f'{self.name} {self.version}',
            'severity': Severity.LOW.value,
            'cwe': 200,     # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
            'references': self.reference,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }


class Vulnerability(Finding):
    technology = create_finding_foreign_key(Technology, 'vulnerability')
    enumeration = create_finding_foreign_key(Enumeration, 'vulnerability')
    name = models.TextField(max_length=50)
    description = models.TextField(blank=True, null=True)
    severity = models.TextField(choices=Severity.choices, default=Severity.MEDIUM)
    cve = models.TextField(max_length=20, blank=True, null=True)
    cwe = models.TextField(max_length=20, blank=True, null=True)
    osvdb = models.TextField(max_length=20, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)

    key_fields = [
        {'name': 'technology_id', 'is_base': True},
        {'name': 'enumeration_id', 'is_base': True},
        {'name': 'cve', 'is_base': False},
        {'name': 'name', 'is_base': False}
    ]

    def defect_dojo(self):
        return {
            'title': self.name,
            'description': self.description,
            'severity': Severity(self.severity).value,
            'cve': self.cve,
            'cwe': int(self.cwe.split('-', 1)[1]) if self.cwe else None,
            'references': self.reference,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }


class Credential(Finding):
    email = models.TextField(max_length=100, blank=True, null=True)
    username = models.TextField(max_length=100, blank=True, null=True)
    secret = models.TextField(max_length=300, blank=True, null=True)

    key_fields = [
        {'name': 'email', 'is_base': False},
        {'name': 'username', 'is_base': False},
        {'name': 'secret', 'is_base': False}
    ]

    def defect_dojo(self):
        description = ''
        for field in ['email', 'username', 'secret']:
            if getattr(self, field):
                if description:
                    description += ' - '
                description += getattr(self, field)
        return {
            'title': 'Credentials exposure',
            'description': description,
            'cwe': 200,     # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
            'severity': Severity.HIGH.value,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }


class Exploit(Finding):
    vulnerability = create_finding_foreign_key(Vulnerability, 'exploit')
    technology = create_finding_foreign_key(Technology, 'exploit')
    name = models.TextField(max_length=100)
    description = models.TextField(blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    checked = models.BooleanField(default=False)

    key_fields = [
        {'name': 'vulnerability_id', 'is_base': True},
        {'name': 'technology_id', 'is_base': True},
        {'name': 'name', 'is_base': False},
        {'name': 'reference', 'is_base': False}
    ]

    def defect_dojo(self):
        return {
            'title': f'Exploit {self.name} found',
            'description': self.description,
            'severity': Severity(self.vulnerability.severity).value if self.vulnerability else Severity.MEDIUM.value,   # noqa: E501
            'reference': self.reference,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }
