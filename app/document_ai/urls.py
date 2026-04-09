from django.urls import path
from document_ai.search.views import VectorSearchView

app_name = "document_ai"

urlpatterns = [
    path("v1/search/", VectorSearchView.as_view(), name="vector-search"),
]
