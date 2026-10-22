# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Data parallelism with the optimizer sharded across the GPUs (ZeRO stage 1) for GPT models.

from typing import Iterator, List, Optional, Tuple
import torch
import torch.nn as nn

from gptmodel.GptModel import GptModel
from gptmodel.MultiGpuGptModelDP import MultiGpuGptModelDP
from gptutils.consoleutils import print


class MultiGpuGptModelZeRO1(MultiGpuGptModelDP):
    """
    MultiGpuGptModelDP whose optimizer work and state are sharded across the GPUs (ZeRO stage 1, "zero redundancy optimizer").
    Forward/backward are the plain data parallelism of the base class: every GPU runs the whole model on its share of the batch and
    accumulates full fp32 gradients locally, with no traffic between micro-steps. The difference is the optimizer update. Every parameter
    has an owner GPU (largest tensors first onto the least loaded GPU, so the shards are balanced and the same on every run); the owner
    keeps that parameter's fp32 master and its optimizer state (AdamW moments, Muon momentum). Once per update:
      1. reduce-scatter: each owner receives only its shard's gradients from the other GPUs and averages them (reduce_gradients);
      2. the single optimizer, built over the shard masters (parameters()), updates every shard on its own GPU;
      3. all-gather: each owner sends its updated shard to every other GPU's compute copy (sync_weights).
    Per GPU this stores weights + gradients + 1/N of the optimizer state (16 -> 12 bytes/param on 2 GPUs, 9.3 on 6, with fp32 AdamW)
    instead of the base class's full 16 on the primary, and moves 2 x (N-1)/N model sizes per update on every GPU instead of N-1 model
    sizes each way through the primary alone. The arithmetic is the base class's exactly: the same averaged gradients, the same AdamW on
    fp32 masters; only where each number is stored and computed changes.
    raw_model (device 0) keeps a full fp32 copy that the all-gather refreshes after every update, so sample generation, state_dict() and
    the checkpoints see the complete model as before; after a checkpoint is loaded into it, adopt_primary_weights() spreads it to the shards.
    """
    def __init__(
        self,
        raw_model: GptModel,
        devices: Optional[List[torch.device]] = None,
        compile: bool = False,
        compute_dtype: Optional[torch.dtype] = None,
        compile_mode: Optional[str] = None,
        reference_model: Optional[nn.Module] = None,
    ):
        super().__init__(raw_model, devices=devices, compile=compile, compute_dtype=compute_dtype, compile_mode=compile_mode, reference_model=reference_model)
        self._replica_params: List[List[nn.Parameter]] = [list(rep.parameters()) for rep in self.raw_replicas]  # same order as the masters
        load = [0] * self.num_gpus
        self.owner: List[int] = [0] * len(self._master_params)
        for k in sorted(range(len(self._master_params)), key=lambda k: -self._master_params[k].numel()):
            j = min(range(self.num_gpus), key=lambda g: (load[g], g))
            self.owner[k], load[j] = j, load[j] + self._master_params[k].numel()
        # The shard masters: device 0's are raw_model's parameters; another owner's is its compute copy's parameter when that is already
        # fp32 (fp8 mode, norms, embeddings) and otherwise a private fp32 copy on the owner (bf16 compute copies)
        self.shard_params: List[torch.Tensor] = []
        for k, (m, j) in enumerate(zip(self._master_params, self.owner)):
            p = self._replica_params[j][k]
            self.shard_params.append(m if j == 0 else p if p.dtype == torch.float32 else m.detach().to(self.devices[j]).clone().requires_grad_(m.requires_grad))
        print(f"[Multi-GPU ZeRO-1] Optimizer state sharded across {self.num_gpus} GPUs: " + ", ".join(f"{d} {n / 1e6:.1f}M params" for d, n in zip(self.devices, load)))

    def parameters(self, recurse: bool = True) -> Iterator[torch.Tensor]:
        return iter(self.shard_params)

    def named_parameters(self, prefix: str = "", recurse: bool = True) -> Iterator[Tuple[str, torch.Tensor]]:
        return iter([(name, sp) for (name, _), sp in zip(self.raw_model.named_parameters(prefix=prefix, recurse=recurse), self.shard_params)])

    def _grad_of(self, gpu_idx: int, k: int) -> Optional[torch.Tensor]:
        """The fp32 gradient GPU gpu_idx accumulated for parameter k (device 0 accumulates into the masters' .grad, the others into _grad_bufs)."""
        return self._master_params[k].grad if gpu_idx == 0 else self._grad_bufs[gpu_idx][k]

    def reduce_gradients(self):
        """Reduce-scatter: every owner receives its shard's gradient sums from the other GPUs (2-D ones in the wire dtype), adds them to its own
        and averages; the gradients of the parameters a GPU does not own are freed. Once per optimizer update, not per micro-step."""
        if self.num_gpus <= 1:
            return
        for dev in self.devices:
            torch.cuda.synchronize(dev)
        scale = 1.0 / self.num_gpus
        lowp = self._transfer_dtype()
        with torch.no_grad():
            for j in range(self.num_gpus):
                for i in range(self.num_gpus):
                    if i == j:
                        continue
                    pairs, landed, pending = [], [], 0

                    def flush():
                        nonlocal pairs, landed, pending
                        self._copy_across(pairs, i, j)
                        for k, g in landed:
                            acc = self._grad_of(j, k)
                            acc = g.to(torch.float32) if acc is None else acc.add_(g)
                            if j == 0:
                                self._master_params[k].grad = acc
                            else:
                                self._grad_bufs[j][k] = acc
                        pairs, landed, pending = [], [], 0

                    for k in range(len(self._master_params)):
                        src = self._grad_of(i, k) if self.owner[k] == j else None
                        if src is None:
                            continue
                        g = src.to(lowp) if lowp is not None and k in self._lowp_grad_idx else src
                        land = torch.empty_like(g, device=self.devices[j])
                        pairs.append((g, land)); landed.append((k, land))
                        pending += g.numel() * g.element_size()
                        if pending >= self.COPY_BATCH_BYTES:
                            flush()
                    flush()
            for k, (sp, j) in enumerate(zip(self.shard_params, self.owner)):
                acc = self._grad_of(j, k)
                sp.grad = None if acc is None else acc.mul_(scale)
                if j != 0:
                    self._master_params[k].grad = None  # device 0's sum of a shard it does not own has been sent
            self._grad_bufs = [[None] * len(self._master_params) for _ in self.devices]  # owned sums now live in the shard masters' .grad

    def sync_weights(self):
        """All-gather: every owner's updated shard goes to each other GPU's compute copy (and to raw_model on device 0), cast on the owner to the
        destination's dtype or to the wire dtype for eligible weights a destination stores in fp32, in batched pipelined transfers."""
        lowp = self._transfer_dtype()
        with torch.no_grad():
            for j in range(self.num_gpus):
                for k, (sp, o) in enumerate(zip(self.shard_params, self.owner)):  # the owner's own compute copy (a private fp32 master feeds its bf16 weight)
                    p = self._replica_params[j][k]
                    if o == j and p is not sp:
                        p.copy_(sp)
                for i in range(self.num_gpus):
                    if i == j:
                        continue
                    dests = lambda k: [self._replica_params[i][k]] + ([self._master_params[k]] if i == 0 and self.raw_replicas[0] is not self.raw_model else [])
                    pairs, landed, pending = [], [], 0

                    def flush():
                        nonlocal pairs, landed, pending
                        self._copy_across(pairs, j, i)
                        for d, w in landed:
                            d.copy_(w)
                        pairs, landed, pending = [], [], 0

                    for k, (sp, o) in enumerate(zip(self.shard_params, self.owner)):
                        if o != j:
                            continue
                        for d in dests(k):
                            # a compute copy may take the wire dtype (what autocast computes with anyway); raw_model's fp32 copy must stay exact
                            wire = d.dtype if d.dtype != sp.dtype else (lowp if lowp is not None and k in self._lowp_weight_idx and d is not self._master_params[k] else sp.dtype)
                            w = sp.to(wire) if wire != sp.dtype else sp
                            if d.dtype == wire:
                                pairs.append((w, d))
                            else:
                                land = torch.empty_like(w, device=self.devices[i])
                                pairs.append((w, land)); landed.append((d, land))
                            pending += w.numel() * w.element_size()
                            if pending >= self.COPY_BATCH_BYTES:
                                flush()
                    flush()
            for i, rep in enumerate(self.raw_replicas):
                if rep is not self.raw_model:
                    for b0, b_other in zip(self.raw_model.buffers(), rep.buffers()):
                        b_other.data.copy_(b0.data.to(self.devices[i], non_blocking=True))

    def adopt_primary_weights(self):
        """After weights were loaded into raw_model (checkpoint restore): the shards owned elsewhere take them over, then everyone is refreshed."""
        with torch.no_grad():
            for k, (sp, j) in enumerate(zip(self.shard_params, self.owner)):
                if j != 0:
                    sp.copy_(self._master_params[k].to(self.devices[j]))
        self.sync_weights()

    def zero_grad(self, set_to_none: bool = True):
        super().zero_grad(set_to_none=set_to_none)
        for sp in self.shard_params:
            sp.grad = None
