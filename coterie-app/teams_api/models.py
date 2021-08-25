from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import User
from .utils import Roles, Status, default_role, default_status


# Create your models here.


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(
        User, related_name='owned_teams', on_delete=models.CASCADE)
    members = models.ManyToManyField(
        User, related_name='teams', through='Enrollments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Enrollments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(_("Roles"), max_length=58,
                            choices=Roles.choices, default=default_role)
    status = models.CharField(
        _("Status"), max_length=58, choices=Status.choices, default=default_status)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'team']]
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return str(self.team)


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, default='')
    team = models.ForeignKey(
        Team, related_name='projects', on_delete=models.CASCADE)
    url = models.URLField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title
