from typing import List
import gc
import logging

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

logger = logging.getLogger(__name__)

_TOKENIZER = None
_MODEL = None
_MODEL_NAME = None
_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# TODO: 임베딩 처리 과정에서 서버 메모리 부족 방지를 위해,
# 1. GPU 메모리 OOM 방어를 위해 배치(Batch) 처리 로직 검토할 것.
# 2. 서비스 확장 시 `bge-m3` 모델을 GPU 전용 TGI / vLLM 서버로 분리하는 것 고려.

def _clear_cuda_cache() -> None:
    if _DEVICE.type == "cuda":
        torch.cuda.empty_cache()
        if torch.cuda.is_available():
            torch.cuda.ipc_collect()


def _get_model_and_tokenizer(model_name: str):
    """
    BGE-M3 모델과 토크나이저를 로드합니다. (싱글톤)
    """
    global _TOKENIZER, _MODEL, _MODEL_NAME, _DEVICE
    
    if _MODEL_NAME != model_name:
        _TOKENIZER = AutoTokenizer.from_pretrained(model_name)
        _MODEL = AutoModel.from_pretrained(model_name)
        _MODEL.to(_DEVICE)
        _MODEL.eval()
        _MODEL_NAME = model_name
        
    return _MODEL, _TOKENIZER


def bge_m3_embedder(
    text: str,
    model_name: str = "BAAI/bge-m3",
    padding: bool = False,
    truncation: bool = True,
    normalize: bool = True,
    max_length: int = 8192,
) -> list[float]:
    """
    BGE-M3 모델 전용 임베딩 함수
    # TODO: 현재 입력 토큰은 1024 + alpha, 토큰 들어오는 것이 불안정함.
    """
    
    if not isinstance(text, str):
        raise ValueError("Text not String")

    text = text.strip()
    if not text:
        raise ValueError("Text is Empty")

    model, tokenizer = _get_model_and_tokenizer(model_name)

    try:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=truncation,
            padding=padding,
            max_length=max_length,
        )

        inputs = {k: v.to(_DEVICE) for k, v in inputs.items()}

        with torch.inference_mode():
            outputs = model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0]

            if normalize:
                embeddings = F.normalize(embeddings, p=2, dim=1)

        vector = embeddings[0].detach().cpu().tolist()

        if not vector:
            raise RuntimeError("Embedding vector is empty")

        return vector

    except torch.cuda.OutOfMemoryError as e:
        logger.exception(
            "CUDA OOM during embedding. model=%s, max_length=%s, device=%s",
            model_name, max_length, _DEVICE,
        )
        _clear_cuda_cache()
        gc.collect()
        raise RuntimeError(
            f"GPU OOM while embedding text (model={model_name}, max_length={max_length})"
        ) from e

    finally:
        for var_name in ("inputs", "outputs", "embeddings"):
            if var_name in locals():
                del locals()[var_name]
        gc.collect()
        if _DEVICE.type == "cuda":
            torch.cuda.empty_cache()