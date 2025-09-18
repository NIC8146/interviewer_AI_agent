from django.urls import path, include
from . import views

urlpatterns = [
    path("chat/<str:pk>", views.home, name='home'),
    path("upload_file/<str:pk>", views.upload_file_view, name="upload_file"),
    path("check_resume/<str:pk>", views.check_resume_status, name="check_resume"),
]
