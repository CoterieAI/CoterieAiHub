from django.db import models
from authentication.models import User
from .utils import Roles, Status, default_role, default_status
from django.utils.translation import gettext_lazy as _

# Create your models here.
#team can exist without projects, 
# projects cannot exit witout a team

class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(User, related_name='owned_teams', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='teams', through='Enrollments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Enrollments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(_("Roles"), max_length=58, choices=Roles.choices, default=default_role)
    status = models.CharField(_("Status"), max_length=58, choices=Status.choices, default=default_status)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'team']]
        verbose_name_plural = "Enrollments"
    
    def __str__(self):
        return str(self.team)