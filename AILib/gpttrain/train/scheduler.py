# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Learning rate scheduling for GPT pretraining.

import math


def get_lr_cosine_schedule(it: int, max_lr: float, min_lr: float, warmup_steps: int, total_steps: int) -> float:
    """Computes learning rate with linear warmup and cosine decay."""
    if it < warmup_steps:
        return max_lr * (it + 1) / max_lr if warmup_steps == 0 else max_lr * (it + 1) / warmup_steps
    if it > total_steps:
        return min_lr
    decay_ratio = (it - warmup_steps) / max(1, (total_steps - warmup_steps))
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return min_lr + coeff * (max_lr - min_lr)
