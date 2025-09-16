
from django.urls import path, include
from . import views

urlpatterns = [
    path("chat/", views.home, name='home'),
    path("", views.file_upload_view, name="file_upload"),
]
