from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import  RegisterView, AllUsers, ChangePasswordView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', obtain_auth_token, name='login'),
    path('users', AllUsers.as_view(), name='users'),
    path('update_my_password/', ChangePasswordView.as_view(), name='update_my_password'),
]