"""Assistant-only next-token objective, shared by pilot and numerical tests."""


def assistant_token_loss(logits, targets, assistant_start):
    import mlx.core as mx
    import mlx.nn as nn
    if logits.ndim != 3 or targets.shape != logits.shape[:2]:
        raise ValueError("expected [batch,time,vocab] logits and [batch,time] labels")
    if not 0 <= assistant_start < logits.shape[1]:
        raise ValueError("assistant target span is empty or out of range")
    losses = nn.losses.cross_entropy(logits.astype(mx.float32), targets, reduction="none")
    return mx.mean(losses[:, assistant_start:])
