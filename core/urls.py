from django.urls import path, include
from . import views

urlpatterns = [
    path("chat/<str:pk>", views.home, name='home'),
    path("upload_file/<str:pk>", views.upload_file_view, name="upload_file"),
]
