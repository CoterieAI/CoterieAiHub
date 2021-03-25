from django.contrib import admin
from .models import Team, Enrollments, Project, AiModel, Deployment

# Register your models here.
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'created_at', 'updated_at')
    ordering = ('id',)
    search_fields = ('name',)

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'team', 'status', 'role')
    ordering = ('id',)
    search_fields = ('team', 'user',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'team', 'creator', 'is_archived', 'title', 'description', )
    ordering = ('id',)
    search_fields = ('team', 'creator', 'title')

class AiModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'model_name', 'gcr_url', 'created_at',)
    ordering = ('id',)
    search_fields = ('model_name',)

class DeploymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'deployment_id', 'name', 'model', 'project', 'description', 'service_endpoint', 'creator')
    ordering = ('id',)
    search_fields = ('model', 'project', 'name')

admin.site.register(Team, TeamAdmin)
admin.site.register(Enrollments, EnrollmentAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(AiModel, AiModelAdmin)
admin.site.register(Deployment, DeploymentAdmin)