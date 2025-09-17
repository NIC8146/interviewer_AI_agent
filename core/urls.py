
from django.urls import path, include
from . import views

urlpatterns = [
    path("chat/<str:pk>", views.home, name='home'),
    path("", views.file_upload_view, name="file_upload"),
]
