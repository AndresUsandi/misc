# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Unified optimizer implementations, algorithms, and configuration helpers for GPT models.

import math
from pathlib import Path
import sys
from typing import Any, List, Optional, Union

import torch
import torch.nn as nn
from torchao.optim import _AdamW

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
    def __init__(self, params: Any, lr: float = 1e-3, momentum: float = 0.95, nesterov: bool = True, ns_steps: int = 5):
        defaults = dict(lr=lr, momentum=momentum, nesterov=nesterov, ns_steps=ns_steps)
        super().__init__(params, defaults)

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
                target_dtype = p.dtype if p.dtype in (torch.bfloat16, torch.float16, getattr(torch, "float8_e4m3fn", None)) else g.dtype
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


def _fp32_to_fp16_sr(x: torch.Tensor) -> torch.Tensor:
    # float16 keeps the top 10 of float32's 23 mantissa bits: adding random low bits before truncating them rounds away from
    # zero with probability (dropped bits) / 2^13. Values below float16's normal range (6.1e-5) still round to nearest.
    rand = torch.randint(0, 1 << 13, x.shape, device=x.device, dtype=torch.int32)
    return ((x.view(torch.int32) + rand) & -(1 << 13)).view(torch.float32).half()


def _fp16_adamw_update(
    p: torch.Tensor,
    grad: torch.Tensor,
    exp_avg: torch.Tensor,
    exp_avg_sq: torch.Tensor,
    step: float,
    lr: float,
    beta1: float,
    beta2: float,
    weight_decay: float,
    eps: float
) -> None:
    grad_f32 = grad.float()
    exp_avg_f32 = exp_avg.float().lerp_(grad_f32, 1 - beta1)
    exp_avg_sq_f32 = exp_avg_sq.float().lerp_(grad_f32.square_(), 1 - beta2)
    exp_avg.copy_(exp_avg_f32)
    exp_avg_sq.copy_(exp_avg_sq_f32)
    denom = exp_avg_sq_f32.sqrt_().div_(math.sqrt(1 - beta2 ** step)).add_(eps)
    p.copy_(_fp32_to_fp16_sr(p.float().mul_(1 - lr * weight_decay).addcdiv_(exp_avg_f32, denom, value=-lr / (1 - beta1 ** step))))


class Fp16AdamW(torch.optim.Optimizer):
    """AdamW for float16 weights at fine-tuning/DPO learning rates: the float16 counterpart of torchao's bf16 stochastic rounding.

    A plain float16 update is lost when it is smaller than half the gap to the neighboring float16 value (~0.000015 near 0.02,
    ~0.001 near 1.0), which fine-tuning updates usually are, and float16 moments round squared gradients to zero. Here the
    math runs in float32, the moments are stored as bfloat16 (float32's range at float16's size), and new weights are rounded
    to float16 up or down at random, so small updates land correctly on average. Not torch.compile'd: Inductor skips bfloat16
    graphs on the pre-Ampere GPUs that use float16 weights.
    """
    def __init__(self, params: Any, lr: float = 1e-3, betas: tuple = (0.9, 0.999), eps: float = 1e-8, weight_decay: float = 1e-2):
        super().__init__(params, dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay))

    @torch.no_grad()
    def step(self) -> None:
        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue
                state = self.state[p]
                if not state:
                    state["step"] = 0.0
                    state["exp_avg"] = torch.zeros_like(p, dtype=torch.bfloat16)
                    state["exp_avg_sq"] = torch.zeros_like(p, dtype=torch.bfloat16)
                state["step"] += 1
                # 4M-value slices bound the float32 temporaries (~80 MB) for the largest weights, e.g. the token embedding
                for chunk in zip(*(t.view(-1).split(1 << 22) for t in (p, p.grad, state["exp_avg"], state["exp_avg_sq"]))):
                    _fp16_adamw_update(*chunk, state["step"], group["lr"], *group["betas"], group["weight_decay"], group["eps"])

    def load_state_dict(self, state_dict: dict) -> None:
        super().load_state_dict(state_dict)  # casts the saved moments to the weights' float16, where they underflow again
        params = [p for group in self.param_groups for p in group["params"]]
        param_ids = [i for group in state_dict["param_groups"] for i in group["params"]]
        for i, p in zip(param_ids, params):
            saved = state_dict["state"].get(i, {})
            for key in ("exp_avg", "exp_avg_sq"):
                if key in saved:
                    self.state[p][key] = saved[key].to(device=p.device, dtype=torch.bfloat16)
            if "step" in saved:
                self.state[p]["step"] = float(saved["step"])


def create_hybrid_optimizers(
    model: nn.Module,
    adamw_lr: float = 5e-4,
    muon_lr: float = 1e-3,
    weight_decay: float = 0.1,
    use_adamw_only: bool = False,
    fine_tuning: bool = False
) -> List[torch.optim.Optimizer]:
    """Partitions model parameters into Muon (internal 2D weights) and Fused AdamW (1D / Embeddings / Norms)."""
    raw_model = getattr(model, "raw_model", getattr(model, "module", model))
    raw_model = getattr(raw_model, "_orig_mod", raw_model)

    use_fused = torch.cuda.is_available() and hasattr(torch.optim.AdamW, "default_options")

    if use_adamw_only:
        has_fp16 = any(p.dtype == torch.float16 for p in model.parameters() if p.requires_grad)
        adamw_eps = 1e-4 if has_fp16 else 1e-8
        try:
            return [torch.optim.AdamW(model.parameters(), lr=adamw_lr, weight_decay=weight_decay, eps=adamw_eps, fused=use_fused)]
        except Exception:
            return [torch.optim.AdamW(model.parameters(), lr=adamw_lr, weight_decay=weight_decay, eps=adamw_eps)]

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
        optimizers.append(CustomMuon(muon_params, lr=muon_lr, momentum=0.95))

    if adamw_params:
        has_fp16 = any(p.dtype == torch.float16 for p in adamw_params)
        adamw_eps = 1e-4 if has_fp16 else 1e-8
        if fine_tuning and adamw_params[0].dtype == torch.bfloat16:
            print("[Optimizer] AdamW part (1D/Norms/Embeddings) uses bf16 stochastic rounding (torchao) for small fine-tuning learning rates.")
            optimizers.append(_AdamW(adamw_params, lr=adamw_lr, weight_decay=weight_decay, eps=adamw_eps, bf16_stochastic_round=True))
        elif fine_tuning and has_fp16:
            print("[Optimizer] AdamW part (1D/Norms/Embeddings) uses fp16 stochastic rounding (fp32 math, bf16 moments) for small fine-tuning learning rates.")
            optimizers.append(Fp16AdamW(adamw_params, lr=adamw_lr, weight_decay=weight_decay))
        else:
            try:
                optimizers.append(torch.optim.AdamW(adamw_params, lr=adamw_lr, weight_decay=weight_decay, eps=adamw_eps, fused=use_fused))
            except Exception:
                optimizers.append(torch.optim.AdamW(adamw_params, lr=adamw_lr, weight_decay=weight_decay, eps=adamw_eps))

    return optimizers


def setup_stage_optimizer(
    target_model: nn.Module,
    args: TrainingArgs,
    use_cuda: bool,
    weight_dtype: torch.dtype,
) -> Union[torch.optim.Optimizer, List[torch.optim.Optimizer]]:
    """Instantiates and configures optimizer(s) appropriately for pretraining, fine-tuning, or optimization."""
    stage = args.stage
    if stage == STAGE_TRAIN:
        use_adamw_only = not args.use_muon
        optimizers = create_hybrid_optimizers(
            target_model, adamw_lr=args.learning_rate, muon_lr=args.muon_lr, weight_decay=args.weight_decay,
            use_adamw_only=use_adamw_only
        )
        if use_adamw_only:
            print("Optimizer Configured: 1 ([Single Fused AdamW for all layers, default])")
        else:
            print(f"Optimizers Configured: {len(optimizers)} ([CustomMuon (2D matrices), Fused AdamW (1D/Norms)])")
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
            fine_tuning=True
        )

    use_fused = use_cuda and hasattr(torch.optim.AdamW, "default_options")
    target_params = [p for p in target_model.parameters() if p.requires_grad]
    has_fp16 = any(p.dtype == torch.float16 for p in target_params)
    adamw_eps = 1e-4 if has_fp16 else 1e-8
    if stage != STAGE_TRAIN and weight_dtype == torch.bfloat16:
        print("[Optimizer] AdamW with bf16 stochastic rounding (torchao) for small fine-tuning learning rates.")
        return _AdamW(target_params, lr=args.learning_rate, weight_decay=args.weight_decay, eps=adamw_eps, bf16_stochastic_round=True)
    elif stage != STAGE_TRAIN and weight_dtype == torch.float16:
        print("[Optimizer] AdamW with fp16 stochastic rounding (fp32 math, bf16 moments) for small fine-tuning learning rates.")
        return Fp16AdamW(target_params, lr=args.learning_rate, weight_decay=args.weight_decay)
    else:
        try:
            return torch.optim.AdamW(
                target_params,
                lr=args.learning_rate,
                weight_decay=args.weight_decay,
                eps=adamw_eps,
                fused=use_fused
            )
        except Exception:
            return torch.optim.AdamW(
                target_params,
                lr=args.learning_rate,
                weight_decay=args.weight_decay,
                eps=adamw_eps
            )
