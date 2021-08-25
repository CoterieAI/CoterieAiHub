from re import I
from django.db import models
from authentication.models import User
from teams_api.models import Project

# Create your models here.


class AiModel(models.Model):
    model_name = models.CharField(max_length=600)
    model_id = models.PositiveIntegerField()
    version_id = models.PositiveIntegerField()
    gcr_url = models.CharField(max_length=1000)
    description = models.CharField(max_length=1000, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["model_id", "version_id"]]
        ordering = ("id",)

    def __str__(self):
        return self.model_name + f"-V{self.model_id}"


class Deployment(models.Model):
    name = models.CharField(max_length=100)
    deployment_id = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')
    project = models.ForeignKey(
        Project, related_name='deployments', on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    model = models.ForeignKey(
        AiModel, related_name='deployments', on_delete=models.CASCADE)
    service_endpoint = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
