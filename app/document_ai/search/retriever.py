import logging
from typing import Any, Dict, List, Optional

from pgvector.django import CosineDistance, L2Distance, MaxInnerProduct

from config.enums import AIStatus
from document_ai.models import ChunkEmbedding

logger = logging.getLogger(__name__)


class VectorRetriever:
    def __init__(self, model_name: str = "BAAI/bge-m3", distance_strategy: str = "cosine"):
        self.model_name = model_name
        self.distance_strategy = distance_strategy

    def _get_distance_func(self, vector):
        if self.distance_strategy == "cosine":
            return CosineDistance("vector", vector)
        if self.distance_strategy == "l2":
            return L2Distance("vector", vector)
        if self.distance_strategy == "inner_product":
            return MaxInnerProduct("vector", vector)
        raise ValueError(f"Unknown distance strategy: {self.distance_strategy}")

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        threshold: Optional[float] = None,
        node_ids: Optional[List[int]] = None,
        user=None,
    ) -> List[Dict[str, Any]]:
        from document_ai.embedding.embeding_models import bge_m3_embedder

        try:
            query_vector = bge_m3_embedder(query, model_name=self.model_name)
        except Exception as exc:
            logger.error("Failed to embed query: %s", exc)
            raise

        distance_func = self._get_distance_func(query_vector)

        qs = (
            ChunkEmbedding.objects.annotate(distance=distance_func)
            .select_related("chunk", "chunk__parse_result", "chunk__parse_result__node")
            .filter(model_name=self.model_name, status=AIStatus.COMPLETED)
        )

        if user is not None:
            qs = qs.filter(chunk__parse_result__node__owner=user)

        if node_ids is not None:
            qs = qs.filter(chunk__parse_result__node_id__in=node_ids)

        if threshold is not None:
            qs = qs.filter(distance__lte=threshold)

        results = qs.order_by("distance")[:top_k]

        retrieved_data = []
        for emb in results:
            chunk = emb.chunk
            prompt_context = f"[Document: {chunk.parse_result.node.name}]"
            if chunk.page_from:
                prompt_context += f" p.{chunk.page_from}"
            if chunk.section_title:
                prompt_context += f" - {chunk.section_title}"
            prompt_context += f"\n{chunk.text}"

            retrieved_data.append(
                {
                    "chunk_id": chunk.id,
                    "node_id": chunk.parse_result.node_id,
                    "node_name": chunk.parse_result.node.name,
                    "file_ext": chunk.parse_result.metadata.get("file_ext", ""),
                    "text": chunk.text,
                    "prompt_context": prompt_context,
                    "section": chunk.section_title,
                    "pages": f"{chunk.page_from}-{chunk.page_to}" if chunk.page_to else str(chunk.page_from),
                    "distance": emb.distance,
                }
            )

        return retrieved_data
