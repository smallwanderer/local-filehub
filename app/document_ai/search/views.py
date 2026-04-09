from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from document_ai.search.serializers import (
    VectorSearchRequestSerializer,
    VectorSearchResponseSerializer,
)


@method_decorator(csrf_exempt, name="dispatch")
class VectorSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Vector search",
        operation_description="Embed the query and return the most relevant indexed chunks.",
        request_body=VectorSearchRequestSerializer,
        responses={200: VectorSearchResponseSerializer(many=True)},
    )
    def post(self, request, *args, **kwargs):
        if not getattr(request.user, "email_verified", False):
            return Response(
                {"error": "Email verification required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = VectorSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            from document_ai.search.retriever import VectorRetriever

            retriever = VectorRetriever()
            results = retriever.retrieve(
                query=serializer.validated_data["query"],
                top_k=serializer.validated_data.get("top_k", 5),
                threshold=serializer.validated_data.get("threshold"),
                node_ids=serializer.validated_data.get("node_ids"),
                user=request.user,
            )
            return Response(results, status=status.HTTP_200_OK)
        except ImportError as exc:
            return Response(
                {
                    "error": "Retrieval backend is unavailable",
                    "detail": str(exc),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as exc:
            return Response(
                {"error": "Retrieval failed", "detail": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
