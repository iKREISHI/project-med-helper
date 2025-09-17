from typing import List, Dict, Any
from django.conf import settings
from sentence_transformers import CrossEncoder

_CE_MODEL_NAME = getattr(
    settings, "CROSS_ENCODER_MODEL", "DiTy/cross-encoder-russian-msmarco"
)
_CE_BATCH = int(getattr(settings, "CROSS_ENCODER_BATCH", 32))

_cross_encoder = None


def _get_ce():
    global _cross_encoder
    if _cross_encoder is None:
        # CPU → device='cpu' ; если есть GPU, уберите параметр
        _cross_encoder = CrossEncoder(_CE_MODEL_NAME, device="cpu")
    return _cross_encoder


def rerank(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int,
    text_key: str = "text",
) -> List[Dict[str, Any]]:
    """
    Принимает уже отсортированный список кандидатов и
    дополнительно ранжирует их кросс-энкодером.
    """
    if not candidates:
        return []

    ce = _get_ce()
    pairs = [(query, c.get(text_key, "")) for c in candidates]

    # CrossEncoder.predict принимает список пар строк
    scores = ce.predict(pairs, batch_size=_CE_BATCH, convert_to_numpy=True)

    for c, s in zip(candidates, scores):
        c["_ce_score"] = float(s)

    # чем выше score, тем релевантнее
    candidates.sort(key=lambda x: x["_ce_score"], reverse=True)
    return candidates[:top_k]
