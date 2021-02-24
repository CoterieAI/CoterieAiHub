from django.urls import path
from .views import  TeamApiView, TeamInviteListAPIView, TeamInviteDetailAPIView, AcceptEmailInvite

urlpatterns = [
    path('teams/', TeamApiView.as_view(), name=TeamApiView.name),
    path('invite-member/', TeamInviteListAPIView.as_view(), name=TeamInviteListAPIView.name),
    path('team-member/<int:invite_id>/', TeamInviteDetailAPIView.as_view(), name=TeamInviteDetailAPIView.name),
    path('invite-acceptance/', AcceptEmailInvite.as_view(), name='invite-acceptance'),
]