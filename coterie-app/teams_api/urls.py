from django.urls import path
from . import views

urlpatterns = [
    path('teams/', views.TeamListApiView.as_view(),
         name=views.TeamListApiView.name),
    path('teams/<int:team_id>/', views.TeamDetailApiView.as_view(),
         name=views.TeamDetailApiView.name),
    path('<int:team_id>/projects/',
         views.ProjectListView.as_view(), name='project-list'),
    path('<int:team_id>/projects/<int:id>/',
         views.ProjectDetailView.as_view(), name='project-detail'),
    path('<int:team_id>/invites/',
         views.TeamInviteListAPIView.as_view(), name='team-invite-list'),
    path('<int:team_id>/invites/<int:invite_id>/',
         views.TeamInviteDetailAPIView.as_view(), name='team-invite-detail'),
    path('invite-acceptance/', views.AcceptEmailInvite.as_view(),
         name='invite-acceptance'),

]
