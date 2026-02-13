# files/urls.py
from django.urls import path
from . import views
from django.contrib import messages

app_name = "files"

urlpatterns = [
    # path("", views.file_list, name="list"),
    path("", views.dummy_file_list, name="list"),
    path("upload/", views.upload_file, name="upload"),
    path("<int:pk>/", views.file_detail, name="detail"),
    path("<int:pk>/download/", views.file_download, name="download"),
    path("<int:pk>/confirm_delete/", views.file_delete, name="delete"),
]
