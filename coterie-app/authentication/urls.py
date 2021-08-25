from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import RegisterView, AllUsers, ChangePasswordView, MyTokenObtainPairView, UserProfiles, UserProfile, UserProfilesById, UserProjects

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('update_my_password/', ChangePasswordView.as_view(),
         name='update_my_password'),
    path('users/', UserProfiles.as_view(), name='user-list'),
    path('profile/', UserProfile.as_view(), name='profile-detail'),
    path('users/<int:id>/', UserProfilesById.as_view(), name='user-detail'),
    path('user/projects/', UserProjects.as_view(), name='user-projects-list'),
]
