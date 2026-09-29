# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Learning rate scheduling for DPO preference optimization.

import math


def get_cosine_lr_with_warmup(
    current_step: int,
    warmup_steps: int,
    total_steps: int,
    peak_lr: float,
    min_lr: float = 1e-7
) -> float:
    """Calculates learning rate with linear warmup and cosine decay."""
    if current_step < warmup_steps:
        return min_lr + (peak_lr - min_lr) * (current_step / max(1, warmup_steps))
    if current_step >= total_steps:
        return min_lr
    progress = (current_step - warmup_steps) / max(1, total_steps - warmup_steps)
    return min_lr + 0.5 * (peak_lr - min_lr) * (1.0 + math.cos(math.pi * progress))
