from . import views
from django.urls import path

urlpatterns = [
    path('', views.CreateNewModelListView.as_view(), name='models-list-all'),
    path('<int:model_id>/', views.ModelVersionAPIView.as_view(),
         name="model-version-list"),
    path("<int:model_id>/<int:version_id>/",
         views.ModelDetailAPI.as_view(), name="model-detail")
]
