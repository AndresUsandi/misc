# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Unified optimizer implementations, algorithms, and configuration helpers for GPT models.

import math
from pathlib import Path
import sys
from typing import Any, Callable, List, Optional, Union

import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import TrainingArgs
from gptio.pathutil import STAGE_TRAIN, STAGE_OPTIMIZE
from gptutils.consoleutils import print


def set_optimizer_lr(optimizer: Union[torch.optim.Optimizer, List[torch.optim.Optimizer]], lr: float) -> None:
    """Sets the learning rate on every param group; torchao optimizers keep lr as a tensor that must be filled in place."""
    opts = optimizer if isinstance(optimizer, list) else [optimizer]
    # Peak LRs come from optimizer.defaults (the constructor values): unlike param_group keys, they survive load_state_dict on resume
    adamw_initial_lr = next((float(o.defaults["lr"]) for o in opts if o.__class__.__name__ != "CustomMuon" and "lr" in o.defaults), None)

    for opt in opts:
        is_muon = opt.__class__.__name__ == "CustomMuon"
        target_lr = float(opt.defaults["lr"]) * (lr / adamw_initial_lr) if is_muon and adamw_initial_lr else lr
        for param_group in opt.param_groups:
            if torch.is_tensor(param_group["lr"]):
                param_group["lr"].fill_(target_lr)
            else:
                param_group["lr"] = target_lr


def lr_schedule_from_resume(optimizer: Union[torch.optim.Optimizer, List[torch.optim.Optimizer]], start_step: int, planned_lr_at: Callable[[int], float], total_steps: int, warmup_steps: int, min_lr: float) -> Callable[[int], float]:
    """Returns the lr(step) function a session should follow. Fresh runs, and resumes whose LR horizon is unchanged, follow planned_lr_at
    (the warmup + cosine of the current plan). When the horizon moved since the checkpoint (an estimated step plan replaced by the exact
    one, a different num_epochs, more or fewer files), the LR the checkpointed optimizer last applied (restored by load_state_dict) is no
    longer on the new curve, so the run would jump; instead the cosine is re-anchored: it continues from that LR at start_step down to
    min_lr at total_steps. Differences within 0.5% (one step of normal cosine slope) are ignored, as is an LR still at the constructor
    peak (an optimizer whose state was not restored has nothing to continue from)."""
    opts = optimizer if isinstance(optimizer, list) else [optimizer]
    adamw = next((o for o in opts if o.__class__.__name__ != "CustomMuon"), None)
    resumed_lr = float(adamw.param_groups[0]["lr"]) if adamw else None
    planned = planned_lr_at(start_step)
    if start_step <= 0 or start_step < warmup_steps or resumed_lr is None or resumed_lr == float(adamw.defaults["lr"]) or abs(resumed_lr - planned) <= 0.005 * max(planned, 1e-12):
        return planned_lr_at
    span = max(1, total_steps - start_step)
    print(f"[Training Plan] LR horizon changed since the checkpoint: the new plan puts step {start_step:,} at {planned:.3e} but the run was at {resumed_lr:.3e}; continuing the cosine from {resumed_lr:.3e} down to {min_lr:.3e} over the remaining {span:,} update(s) instead of jumping.")
    return lambda step: min_lr if step >= total_steps else min_lr + 0.5 * (resumed_lr - min_lr) * (1.0 + math.cos(math.pi * (step - start_step) / span))


def zeropower_via_newtonschulz5(G: torch.Tensor, steps: int = 5, eps: float = 1e-7) -> torch.Tensor:
    """Newton-Schulz iteration to compute the zeroth power / orthogonalization of matrix G."""
    assert len(G.shape) == 2
    a, b, c = (3.4445, -4.7750, 2.0315)
    X = G.bfloat16() if G.dtype == torch.bfloat16 else G.float()
    X /= (X.norm() + eps)
    if G.size(0) > G.size(1):
        X = X.T
    for _ in range(steps):
        A = X @ X.T
        B = b * A + c * A @ A
        X = a * X + B @ X
    if G.size(0) > G.size(1):
        X = X.T
    return X.to(dtype=G.dtype)


class CustomMuon(torch.optim.Optimizer):
    """Muon optimizer for internal 2D weight matrices (Linear layers)."""
    def __init__(self, params: Any, lr: float = 1e-3, momentum: float = 0.95, nesterov: bool = True, ns_steps: int = 5, momentum_dtype: Optional[torch.dtype] = None):
        defaults = dict(lr=lr, momentum=momentum, nesterov=nesterov, ns_steps=ns_steps)
        super().__init__(params, defaults)
        self.momentum_dtype = momentum_dtype  # --use_bf16_for_muon_momentum; an attribute (not a param_group key) so it survives load_state_dict and the flag stays authoritative on resume

    def load_state_dict(self, state_dict: dict) -> None:
        super().load_state_dict(state_dict)  # casts every loaded buffer to the fp32 param dtype; re-cast right away so a resumed run keeps the bf16 saving
        for s in self.state.values():
            if self.momentum_dtype is not None and "momentum_buffer" in s:
                s["momentum_buffer"] = s["momentum_buffer"].to(self.momentum_dtype)

    @torch.no_grad()
    def step(self) -> None:
        for group in self.param_groups:
            lr = group["lr"]
            momentum = group["momentum"]
            nesterov = group["nesterov"]
            ns_steps = group["ns_steps"]

            for p in group["params"]:
                if p.grad is None:
                    continue
                g = p.grad
                if g.ndim != 2:
                    continue

                state = self.state[p]
                target_dtype = self.momentum_dtype if self.momentum_dtype is not None else (p.dtype if p.dtype in (torch.bfloat16, torch.float16, getattr(torch, "float8_e4m3fn", None)) else g.dtype)
                if "momentum_buffer" not in state:
                    state["momentum_buffer"] = torch.zeros_like(g, dtype=target_dtype)

                buf = state["momentum_buffer"]
                g_typed = g.to(dtype=target_dtype)
                buf.mul_(momentum).add_(g_typed)

                if nesterov:
                    g_update = g_typed.add(buf, alpha=momentum)
                else:
                    g_update = buf

                u = zeropower_via_newtonschulz5(g_update.to(dtype=torch.float32), steps=ns_steps).to(dtype=p.dtype)
                scaled_lr = lr * max(1.0, p.size(0) / p.size(1)) ** 0.5
                p.data.add_(u, alpha=-scaled_lr)
                p.grad = None


def create_hybrid_optimizers(
    model: nn.Module,
    adamw_lr: float = 5e-4,
    muon_lr: float = 1e-3,
    weight_decay: float = 0.1,
    use_adamw_only: bool = False,
    fine_tuning: bool = False,
    adamw8bit: bool = False,
    muon_momentum_dtype: Optional[torch.dtype] = None,
) -> List[torch.optim.Optimizer]:
    """Partitions model parameters into Muon (internal 2D weights) and Fused AdamW (1D / Embeddings / Norms). The weights are fp32 masters
    (gptio.precision), so plain fused AdamW is exact at every learning rate; no stochastic-rounding variants are needed.
    adamw8bit (--use_torchao_adamw8bit): torchao AdamW8bit in place of AdamW, same update with the moments stored block-quantized to 8 bits."""
    use_fused = torch.cuda.is_available()
    if adamw8bit:
        from torchao.optim import AdamW8bit

    if use_adamw_only:
        if adamw8bit:
            return [AdamW8bit(model.parameters(), lr=adamw_lr, weight_decay=weight_decay)]
        try:
            return [torch.optim.AdamW(model.parameters(), lr=adamw_lr, weight_decay=weight_decay, fused=use_fused)]
        except Exception:
            return [torch.optim.AdamW(model.parameters(), lr=adamw_lr, weight_decay=weight_decay)]

    muon_params = []
    adamw_params = []

    for name, p in model.named_parameters():
        if not p.requires_grad:
            continue
        if p.ndim == 2 and ("tok_emb" not in name and "pos_emb" not in name and "out_head" not in name):
            muon_params.append(p)
        else:
            adamw_params.append(p)

    optimizers = []
    if muon_params:
        optimizers.append(CustomMuon(muon_params, lr=muon_lr, momentum=0.95, momentum_dtype=muon_momentum_dtype))

    if adamw_params and adamw8bit:
        optimizers.append(AdamW8bit(adamw_params, lr=adamw_lr, weight_decay=weight_decay))
    elif adamw_params:
        try:
            optimizers.append(torch.optim.AdamW(adamw_params, lr=adamw_lr, weight_decay=weight_decay, fused=use_fused))
        except Exception:
            optimizers.append(torch.optim.AdamW(adamw_params, lr=adamw_lr, weight_decay=weight_decay))

    return optimizers


def freeze_lower_layers(model: nn.Module, below_layer: int) -> None:
    """--dpo_freeze_below_layer: marks the embeddings (token, position, the tied output head) and transformer blocks 0..below_layer-1 as not
    trainable, on the model and on every data-parallel compute copy (they mirror the masters' flags only when they are built). Call before
    the optimizer is created: it collects the parameters that still require gradients."""
    frozen = ("tok_emb.", "pos_emb.", "out_head.") + tuple(f"trf_blocks.{i}." for i in range(below_layer))
    copies = {id(m): m for m in [getattr(model, "raw_model", getattr(model, "module", model))] + list(getattr(model, "raw_replicas", []))}
    n_frozen = n_total = 0
    for m in copies.values():
        m = getattr(m, "_orig_mod", m)
        for name, p in m.named_parameters():
            if name.startswith(frozen):
                p.requires_grad_(False)
    for name, p in next(iter(copies.values())).named_parameters():
        n_total += p.numel(); n_frozen += p.numel() if not p.requires_grad else 0
    print(f"[DPO Freeze] Embeddings and transformer blocks 0-{below_layer - 1} frozen: {n_frozen:,} of {n_total:,} parameters ({100 * n_frozen / n_total:.0f}%) stay at their SFT values; blocks {below_layer}.. and the final norm train.")


def setup_stage_optimizer(
    target_model: nn.Module,
    args: TrainingArgs,
    use_cuda: bool,
    weight_dtype: torch.dtype,
) -> Union[torch.optim.Optimizer, List[torch.optim.Optimizer]]:
    """Instantiates and configures optimizer(s) appropriately for pretraining, fine-tuning, or optimization."""
    stage = args.stage
    muon_momentum_dtype = torch.bfloat16 if args.use_bf16_for_muon_momentum else None
    if args.use_bf16_for_muon_momentum and args.use_muon:
        print("[Low-VRAM Optimization] Muon momentum buffers stored in bf16 (halves the Muon optimizer state; weights and Newton-Schulz stay fp32).")
    if stage == STAGE_TRAIN:
        use_adamw_only = not args.use_muon
        optimizers = create_hybrid_optimizers(
            target_model, adamw_lr=args.learning_rate, muon_lr=args.muon_lr, weight_decay=args.weight_decay,
            use_adamw_only=use_adamw_only, adamw8bit=args.use_torchao_adamw8bit, muon_momentum_dtype=muon_momentum_dtype
        )
        adamw_name = "torchao AdamW8bit (8-bit moments)" if args.use_torchao_adamw8bit else "Fused AdamW"
        if use_adamw_only:
            print(f"Optimizer Configured: 1 ([Single {adamw_name} for all layers{', default' if not args.use_torchao_adamw8bit else ''}])")
        else:
            print(f"Optimizers Configured: {len(optimizers)} ([CustomMuon (2D matrices), {adamw_name} (1D/Norms)])")
        return optimizers

    # SFT or DPO
    muon_active = args.use_muon and use_cuda
    if args.use_muon and not use_cuda:
        print("[Optimizer Warning] CustomMuon requires CUDA; falling back to AdamW.")
    if muon_active:
        print("[Optimizer] Selected Hybrid CustomMuon (2D weights) + Fused AdamW (1D/Norms/Embeddings).")
        return create_hybrid_optimizers(
            target_model,
            adamw_lr=args.learning_rate,
            muon_lr=args.muon_lr,
            weight_decay=args.weight_decay,
            use_adamw_only=False,
            fine_tuning=True,
            adamw8bit=args.use_torchao_adamw8bit,
            muon_momentum_dtype=muon_momentum_dtype,
        )

    use_fused = use_cuda
    target_params = [p for p in target_model.parameters() if p.requires_grad]
    if args.use_torchao_adamw8bit and use_cuda:
        from torchao.optim import AdamW8bit
        print("[Optimizer] Selected torchao AdamW8bit (AdamW with 8-bit block-quantized moments, fp32 masters).")
        return AdamW8bit(target_params, lr=args.learning_rate, weight_decay=args.weight_decay)
    try:
        return torch.optim.AdamW(target_params, lr=args.learning_rate, weight_decay=args.weight_decay, fused=use_fused)
    except Exception:
        return torch.optim.AdamW(target_params, lr=args.learning_rate, weight_decay=args.weight_decay)
