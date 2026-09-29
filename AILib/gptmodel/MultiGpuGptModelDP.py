# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# High-Performance Single-Process Multi-GPU Data Parallelism for GPT Models.

from concurrent.futures import ThreadPoolExecutor
import copy
from typing import Any, Dict, List, Optional, Tuple, Union
import torch
import torch.nn as nn
import torch.nn.functional as F

from gptmodel.GptModel import GptModel, LOGIT_CLAMP_MIN, LOGIT_CLAMP_MAX, DYNAMO_RECOMPILE_LIMIT
from gptutils.consoleutils import print


class MultiGpuGptModelDP(nn.Module):
    """
    Data-Parallel wrapper for GPT models across multiple GPUs.
    Maintains a full replica of GptModel on each GPU, executes forward/backward passes
    concurrently via ThreadPoolExecutor, averages gradients onto the primary replica,
    and synchronizes weights across all replicas after optimizer updates.
    """
    def __init__(
        self,
        raw_model: GptModel,
        devices: Optional[List[torch.device]] = None,
        compile: bool = False,
    ):
        super().__init__()
        self.raw_model = raw_model
        if devices is None:
            num_gpus = torch.cuda.device_count()
            self.devices = [torch.device(f"cuda:{i}") for i in range(num_gpus)] if num_gpus > 1 else [torch.device("cuda:0")]
        else:
            self.devices = devices

        self.num_gpus = len(self.devices)
        self.compile_enabled = compile
        self._compiled_keys: set = set()  # (grad mode, input shape) pairs the workers have already run (and so compiled)

        # Primary replica on device 0
        dev0 = self.devices[0]
        self.raw_model.to(dev0)
        self.raw_replicas: List[GptModel] = [self.raw_model]

        # Create identical model replicas on each additional GPU (deep copies keep converted layers such as torchao Float8Linear)
        weight_dtype = next(self.raw_model.parameters()).dtype
        for i in range(1, self.num_gpus):
            self.raw_replicas.append(copy.deepcopy(self.raw_model).to(device=self.devices[i]))

        # Replicas mirror the primary's trainable flags so every replica produces the same set of gradients
        for rep in self.raw_replicas[1:]:
            for p0, p in zip(self.raw_model.parameters(), rep.parameters()):
                p.requires_grad_(p0.requires_grad)

        # Pre-allocated flat exchange buffer per device (one transfer for gradient reduction / weight sync instead of one per tensor)
        numel = sum(p.numel() for p in self.raw_model.parameters())
        self.flat_buffers: List[torch.Tensor] = [torch.empty(numel, dtype=weight_dtype, device=d) for d in self.devices]
        self.flat_views: List[List[torch.Tensor]] = []
        for buf, rep in zip(self.flat_buffers, self.raw_replicas):
            offset, views = 0, []
            for p in rep.parameters():
                views.append(buf[offset:offset + p.numel()].view_as(p))
                offset += p.numel()
            self.flat_views.append(views)

        # Optionally compile each replica independently on its own device
        self.models: List[nn.Module] = []
        for i in range(self.num_gpus):
            m = self.raw_replicas[i]
            if self.compile_enabled and hasattr(torch, "compile"):
                try:
                    print(f"[Multi-GPU DP] Applying torch.compile to replica on {self.devices[i]}...")
                    m.compiled_forward_features = torch.compile(m.forward_features)
                    m.compiled_chunked_loss = torch.compile(m.chunked_loss)
                except Exception as e:
                    print(f"[Multi-GPU DP] torch.compile replica on {self.devices[i]} skipped ({e})")
            self.models.append(m)

        cd_tuning = torch._inductor.config.coordinate_descent_tuning  # Inductor config overrides are thread-local too: the compiling worker threads mirror the main thread's setting
        self.executor = ThreadPoolExecutor(max_workers=max(1, self.num_gpus), initializer=lambda: (setattr(torch._dynamo.config, "recompile_limit", DYNAMO_RECOMPILE_LIMIT), setattr(torch._inductor.config, "coordinate_descent_tuning", cd_tuning)))

    @property
    def cfg(self) -> Dict[str, Any]:
        return self.raw_model.cfg

    @property
    def first_device(self) -> torch.device:
        return self.devices[0]

    @property
    def last_device(self) -> torch.device:
        return self.devices[0]

    def parameters(self, recurse: bool = True):
        return self.raw_replicas[0].parameters(recurse=recurse)

    def named_parameters(self, prefix: str = "", recurse: bool = True):
        return self.raw_replicas[0].named_parameters(prefix=prefix, recurse=recurse)

    def state_dict(self, *args, **kwargs):
        return self.raw_replicas[0].state_dict(*args, **kwargs)

    def load_state_dict(self, state_dict, *args, **kwargs):
        res = self.raw_replicas[0].load_state_dict(state_dict, *args, **kwargs)
        self.sync_weights()
        return res

    def forward(self, in_idx: torch.Tensor, use_cache: bool = False, activation_checkpointing: bool = False) -> torch.Tensor:
        """Standard forward pass routed to primary replica on device 0."""
        dev0 = self.devices[0]
        if use_cache:
            return self.raw_replicas[0](in_idx.to(dev0), use_cache=True, activation_checkpointing=activation_checkpointing)
        return self.models[0](in_idx.to(dev0), use_cache=False, activation_checkpointing=activation_checkpointing)

    def forward_features(self, in_idx: torch.Tensor, activation_checkpointing: bool = False) -> torch.Tensor:
        dev0 = self.devices[0]
        raw_m = self.raw_replicas[0]
        model_feat = getattr(raw_m, "compiled_forward_features", raw_m.forward_features)
        return model_feat(in_idx.to(dev0), activation_checkpointing=activation_checkpointing)

    @property
    def out_head(self):
        return self.raw_replicas[0].out_head

    def _compute_chunked_loss(
        self,
        gpu_idx: int,
        in_tensor: torch.Tensor,
        tgt_tensor: torch.Tensor,
        chunk_size: int,
        amp_dtype: Optional[torch.dtype],
        activation_checkpointing: bool,
        do_backward: bool,
        accum_steps: int,
        scaler: Optional[torch.cuda.amp.GradScaler],
    ) -> torch.Tensor:
        dev = self.devices[gpu_idx]
        raw_m = self.raw_replicas[gpu_idx]
        model = self.models[gpu_idx]
        model_feat = getattr(raw_m, "compiled_forward_features", raw_m.forward_features)
        model_loss = getattr(raw_m, "compiled_chunked_loss", raw_m.chunked_loss)

        # Grad mode is thread-local: the engine's torch.no_grad() around evaluation never reaches this worker thread, which would otherwise
        # build (and sometimes retain) the full training graph for every evaluation batch
        with torch.cuda.device(dev), torch.set_grad_enabled(do_backward):
            if amp_dtype is not None:
                # cache_enabled=False: the cast cache is global while autocast nesting is per-thread, so one replica thread clearing it
                # while the other traces under torch.compile deadlocks (GIL vs cache mutex). The cache is empty anyway with bf16 weights.
                with torch.amp.autocast(device_type="cuda", dtype=amp_dtype, cache_enabled=False):
                    if hasattr(raw_m, "forward_features"):
                        hidden = model_feat(in_tensor, activation_checkpointing=activation_checkpointing)
                        loss = model_loss(hidden, tgt_tensor, chunk_size)
                    else:
                        logits = model(in_tensor, activation_checkpointing=activation_checkpointing)
                        logits = torch.clamp(logits.float(), min=LOGIT_CLAMP_MIN, max=LOGIT_CLAMP_MAX)
                        loss = F.cross_entropy(logits.flatten(0, 1), tgt_tensor.flatten())
            else:
                if hasattr(raw_m, "forward_features"):
                    hidden = model_feat(in_tensor, activation_checkpointing=activation_checkpointing)
                    loss = model_loss(hidden, tgt_tensor, chunk_size)
                else:
                    logits = model(in_tensor, activation_checkpointing=activation_checkpointing)
                    logits = torch.clamp(logits.float(), min=LOGIT_CLAMP_MIN, max=LOGIT_CLAMP_MAX)
                    loss = F.cross_entropy(logits.flatten(0, 1), tgt_tensor.flatten())

            if do_backward:
                scaled_loss = loss / accum_steps
                if scaler is not None:
                    scaled_loss = scaler.scale(scaled_loss)
                scaled_loss.backward()

            return loss.detach()

    def forward_backward_dp(
        self,
        input_batch: torch.Tensor,
        target_batch: torch.Tensor,
        chunk_size: int = 512,
        accum_steps: int = 1,
        activation_checkpointing: bool = False,
        amp_dtype: Optional[torch.dtype] = None,
        scaler: Optional[torch.cuda.amp.GradScaler] = None,
    ) -> Tuple[torch.Tensor, bool]:
        """
        Executes data-parallel forward and backward passes across all GPUs concurrently.
        Splits input_batch and target_batch evenly across devices, executes forward and backward passes
        in parallel worker threads, synchronizes CUDA execution, and averages gradients onto primary replica.

        Returns:
            Tuple[torch.Tensor, bool]: (loss_tensor, backward_executed)
        """
        batch_size = input_batch.shape[0]
        is_training = torch.is_grad_enabled() and self.training

        if self.num_gpus <= 1 or batch_size < self.num_gpus:
            dev0 = self.devices[0]
            inp = input_batch.to(dev0)
            tgt = target_batch.to(dev0)
            loss_val = self._compute_chunked_loss(
                0, inp, tgt, chunk_size, amp_dtype,
                activation_checkpointing, is_training, accum_steps, scaler
            )
            return loss_val, is_training

        chunks_in = torch.chunk(input_batch, self.num_gpus, dim=0)
        chunks_tgt = torch.chunk(target_batch, self.num_gpus, dim=0)
        actual_gpus = len(chunks_in)

        def _worker_step(gpu_idx: int) -> torch.Tensor:
            dev = self.devices[gpu_idx]
            sub_in = chunks_in[gpu_idx].to(dev, non_blocking=True)
            sub_tgt = chunks_tgt[gpu_idx].to(dev, non_blocking=True)
            return self._compute_chunked_loss(
                gpu_idx, sub_in, sub_tgt, chunk_size, amp_dtype,
                activation_checkpointing, is_training, accum_steps, scaler
            )

        # Submit concurrent forward (+ backward if is_training) on all GPUs. The first call with a new grad mode / shape compiles in every worker: run those
        # workers one at a time, concurrent compiles of identical kernels race on the Windows Triton cache (PermissionError, dropped autotune configs)
        key = (is_training, tuple(input_batch.shape))
        one_at_a_time = key not in self._compiled_keys and len(self._compiled_keys) < DYNAMO_RECOMPILE_LIMIT
        self._compiled_keys.add(key)
        futures = []
        for i in range(actual_gpus):
            futures.append(self.executor.submit(_worker_step, i))
            if one_at_a_time:
                futures[-1].result()
        losses = [f.result() for f in futures]

        avg_loss = torch.stack([l.to(self.devices[0], non_blocking=True) for l in losses]).mean()
        return avg_loss, is_training

    def reduce_gradients(self):
        """Reduces and averages accumulated gradients from all secondary replicas onto primary replica."""
        if self.num_gpus <= 1:
            return
        for dev in self.devices:
            torch.cuda.synchronize(dev)
        scale = 1.0 / self.num_gpus
        primary_params = list(self.raw_replicas[0].parameters())
        with torch.no_grad():
            for i in range(1, self.num_gpus):
                replica_params = list(self.raw_replicas[i].parameters())
                active = [k for k, (p0, p_other) in enumerate(zip(primary_params, replica_params)) if p0.grad is not None and p_other.grad is not None]
                if active:
                    torch._foreach_copy_([self.flat_views[i][k] for k in active], [replica_params[k].grad for k in active])
                    self.flat_buffers[0].copy_(self.flat_buffers[i], non_blocking=True)
                    torch._foreach_add_([primary_params[k].grad for k in active], [self.flat_views[0][k] for k in active])
                self.raw_replicas[i].zero_grad(set_to_none=True)

            for p0 in primary_params:
                if p0.grad is not None:
                    p0.grad.mul_(scale)

    def sync_weights(self):
        """Propagates updated weights and buffers from primary replica to all secondary replicas."""
        with torch.no_grad():
            torch._foreach_copy_(self.flat_views[0], list(self.raw_replicas[0].parameters()))
            for i in range(1, self.num_gpus):
                dev = self.devices[i]
                self.flat_buffers[i].copy_(self.flat_buffers[0], non_blocking=True)
                torch._foreach_copy_(list(self.raw_replicas[i].parameters()), self.flat_views[i])
                for b0, b_other in zip(self.raw_replicas[0].buffers(), self.raw_replicas[i].buffers()):
                    b_other.data.copy_(b0.data.to(dev, non_blocking=True))

    def zero_grad(self, set_to_none: bool = True):
        for r in self.raw_replicas:
            r.zero_grad(set_to_none=set_to_none)
