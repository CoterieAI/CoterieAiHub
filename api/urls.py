from django.urls import path
from .views import  TeamApiView, TeamInviteListAPIView, TeamInviteDetailAPIView, AcceptEmailInvite, ProjectListView, ProjectDetailView

urlpatterns = [
    path('teams/', TeamApiView.as_view(), name=TeamApiView.name),
    path('invite-member/', TeamInviteListAPIView.as_view(), name=TeamInviteListAPIView.name),
    path('team-member/<int:invite_id>/', TeamInviteDetailAPIView.as_view(), name=TeamInviteDetailAPIView.name),
    path('invite-acceptance/', AcceptEmailInvite.as_view(), name='invite-acceptance'),
    path('<int:team_id>/projects', ProjectListView.as_view(), name='project-list'),
    path('<int:team_id>/project/<int:id>', ProjectDetailView.as_view(), name='project-detail'),
]