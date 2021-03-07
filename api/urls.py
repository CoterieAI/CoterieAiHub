from django.urls import path
from .views import  TeamListApiView, TeamDetailApiView, ProjectListView, ProjectDetailView, TeamInviteListAPIView,TeamInviteDetailAPIView, AcceptEmailInvite, AiModelListView, AiModelDetailView, SeldonDepolymentAPIView

urlpatterns = [
    path('teams/', TeamListApiView.as_view(), name=TeamListApiView.name),
    path('teams/<int:team_id>', TeamDetailApiView.as_view(), name=TeamDetailApiView.name),
    path('<int:team_id>/projects', ProjectListView.as_view(), name='project-list'),
    path('<int:team_id>/projects/<int:id>', ProjectDetailView.as_view(), name='project-detail'),
    path('<int:team_id>/invites/', TeamInviteListAPIView.as_view(), name='team-invite-list'),
    path('<int:team_id>/invites/<int:invite_id>/', TeamInviteDetailAPIView.as_view(), name='team-invite-detail'),
    path('invite-acceptance/', AcceptEmailInvite.as_view(), name='invite-acceptance'),
    path('models/', AiModelListView.as_view(), name='models-list'),
    path('models/<int:model_id>', AiModelDetailView.as_view(), name= 'model-detail'),
    path('seldon/', SeldonDepolymentAPIView.as_view(), name='seldon-deploy')
]