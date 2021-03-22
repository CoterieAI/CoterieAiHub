from django.contrib import admin
from .models import Team, Enrollments

# Register your models here.
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'created_at', 'updated_at')
    ordering = ('id',)
    search_fields = ('name',)

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'team', 'status', 'role')
    ordering = ('id',)
    search_fields = ('team', 'user',)

admin.site.register(Team, TeamAdmin)
admin.site.register(Enrollments, EnrollmentAdmin)