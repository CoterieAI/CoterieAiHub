from django.contrib import admin
from .models import AiModel, Deployment

# Register your models here.


class AiModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'model_name', 'gcr_url', 'created_at',)
    ordering = ('id',)
    search_fields = ('model_name',)


class DeploymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'deployment_id', 'name', 'model',
                    'project', 'description', 'service_endpoint', 'creator')
    ordering = ('id',)
    search_fields = ('model', 'project', 'name')


admin.site.register(AiModel, AiModelAdmin)
admin.site.register(Deployment, DeploymentAdmin)
