from django.contrib import admin

from .models import Team, Enrollments, Project

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
