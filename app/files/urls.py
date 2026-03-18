# files/urls.py
from django.urls import path
from . import views
from django.contrib import messages

app_name = "files"

urlpatterns = [
    path("upload/", views.upload_file, name="upload"),
    path("<int:pk>/", views.file_detail, name="detail"),
    path("<int:pk>/download/", views.file_download, name="download"),
    path("<int:pk>/confirm_delete/", views.file_delete, name="delete"),
    path("recent/", views.recent_files, name="recent"),
    path("starred/", views.starred_files, name="starred"),
    path("trash/", views.trash_files, name="trash"),
    path("toggle_star/<int:pk>/", views.toggle_star, name="toggle_star"),
    path("", views.file_list, name="list"),
]