from django.contrib.auth.models import User
from django.db import models
from executions.enums import ParameterKey, Status
from processes.models import Process, Step
from projects.models import Target
from tools.enums import IntensityRank
from tools.models import Configuration, Tool

# Create your models here.


class Request(models.Model):
    target = models.ForeignKey(Target, related_name='requests', on_delete=models.CASCADE)
    process = models.ForeignKey(Process, on_delete=models.CASCADE, blank=True, null=True)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, blank=True, null=True)
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    intensity = models.IntegerField(
        choices=IntensityRank.choices,
        default=IntensityRank.NORMAL,
        blank=True,
        null=True
    )
    executor = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=Status.choices, default=Status.REQUESTED)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        value = f'{self.target.project.name} - {self.target.target} - '
        if self.process:
            value += self.process.name
        elif self.tool:
            value += self.tool.name
            if self.configuration:
                value += f' - {self.configuration.name}'
        return value


class Parameter(models.Model):
    request = models.ForeignKey(Request, related_name='parameters', on_delete=models.CASCADE)
    key = models.IntegerField(choices=ParameterKey.choices)
    value = models.TextField(max_length=250)


class Execution(models.Model):
    request = models.ForeignKey(Request, related_name='executions', on_delete=models.CASCADE)
    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    rq_job_pid = models.IntegerField(blank=True, null=True)
    step = models.ForeignKey(Step, on_delete=models.CASCADE, blank=True, null=True)
    output_file = models.TextField(max_length=50, blank=True, null=True)
    output_plain = models.TextField(blank=True, null=True)
    output_error = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=Status.choices, default=Status.REQUESTED)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        if self.step:
            req = self.request.__str__()
            return f'{req} - {self.step.tool.name} - {self.step.configuration.name}'
        else:
            return self.request.__str__()
