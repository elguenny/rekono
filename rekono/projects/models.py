from typing import Any

from django.conf import settings
from django.db import models
from django.db.models import constraints
from django.db.models.deletion import CASCADE

# Create your models here.


class Project(models.Model):
    name = models.TextField(max_length=50, unique=True)
    description = models.TextField(max_length=250)
    defectdojo_product_id = models.IntegerField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='members',
        blank=True
    )

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name

    def get_project(self) -> Any:
        return self
