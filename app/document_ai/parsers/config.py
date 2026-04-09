from typing import Optional
from functools import lru_cache

from django.conf import settings

from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.transforms.serializer.base import BaseSerializerProvider
from transformers import AutoTokenizer


def get_embedding_model():
    return getattr(settings, "EMBEDDING_MODEL", "BAAI/bge-m3")

def get_max_tokens():
    # bge-m3 supports longer context, but we cap for practical local ingestion.
    return getattr(settings, "MAX_TOKENS", 1024)


@lru_cache(maxsize=1)
def get_raw_tokenizer():
    return AutoTokenizer.from_pretrained(get_embedding_model())


@lru_cache(maxsize=1)
def get_hf_tokenizer() -> HuggingFaceTokenizer:
    return HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(get_embedding_model()),
        max_tokens=get_max_tokens(),
    )

@lru_cache(maxsize=1)
def get_converter() -> DocumentConverter:
    return DocumentConverter()


def get_hybrid_hf_chunker(
    serializer_provider: Optional[BaseSerializerProvider] = None,
) -> HybridChunker:
    return HybridChunker(
        tokenizer=get_hf_tokenizer(),
        # [max_tokens] Optional, default is derived from tokenizer for HF case
        # max_tokens=MAX_TOKENS, 
        merge_peers=True,
        serializer_provider=serializer_provider,
    )
