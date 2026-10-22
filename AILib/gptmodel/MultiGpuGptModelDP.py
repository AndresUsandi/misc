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
    raw_model holds the fp32 master weights on the primary GPU (what parameters(), state_dict(), the optimizer and checkpoints see). Each GPU
    runs a compute copy whose plain Linear weights are stored in the autocast compute dtype (mixed-precision training with master weights:
    the matmuls see exactly the bf16(master) that autocast would otherwise re-cast on every micro-step, so one cast per optimizer update
    replaces 2 x accum_steps of them), norms and embeddings staying fp32 as they are under autocast. Forward/backward passes run concurrently
    via ThreadPoolExecutor, each copy's gradients are accumulated in fp32 (exact over accum_steps, as with fp32 weights), averaged onto the
    masters, and after the optimizer update the masters are cast back into every compute copy.
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
        self._amp_dtype: Optional[torch.dtype] = None  # autocast dtype of the latest forward_backward_dp call, decides _transfer_dtype

        # fp32 masters on device 0
        dev0 = self.devices[0]
        self.raw_model.to(dev0)
        self._master_params = list(self.raw_model.parameters())
        # Low-precision tensors: weights of plain Linear layers that are not embeddings, whose only use under autocast is as bf16(weight)
        # (norms run in fp32, embeddings are gathered and summed in fp32 before the stream cast, torchao Float8Linear scales from the fp32
        # tensor), stored in compute_dtype by the compute copies; and all 2-D gradients, which cross the PCIe bus in bf16 (_transfer_dtype)
        emb = {id(p) for m in self.raw_model.modules() if isinstance(m, nn.Embedding) for p in m.parameters()}
        lin = {id(m.weight) for m in self.raw_model.modules() if isinstance(m, nn.Linear) and type(m).__name__ != "Float8Linear"}
        self._lowp_weight_idx = {k for k, p in enumerate(self._master_params) if id(p) in lin and id(p) not in emb}
        self._lowp_grad_idx = {k for k, p in enumerate(self._master_params) if p.ndim == 2}
        self.compute_dtype = compute_dtype if compute_dtype in (torch.bfloat16, torch.float16) and self._lowp_weight_idx else None

        # One compute copy per GPU (deep copies keep converted layers such as torchao Float8Linear). Without a compute dtype the primary
        # computes on the masters themselves, autocast casting per use
        self.raw_replicas: List[GptModel] = []
        for i in range(self.num_gpus):
            if i == 0 and self.compute_dtype is None:
                self.raw_replicas.append(self.raw_model)
                continue
            rep = copy.deepcopy(self.raw_model)
            for k, p in enumerate(rep.parameters()):
                if self.compute_dtype is not None and k in self._lowp_weight_idx:
                    p.data = p.data.to(self.compute_dtype)
            self.raw_replicas.append(rep.to(device=self.devices[i]))
        self._grad_bufs: List[List[Optional[torch.Tensor]]] = [[None] * len(self._master_params) for _ in self.devices]  # fp32 gradient accumulators of the copies on devices 1..n (the copy on device 0 accumulates into the masters' .grad)

        # Compute copies mirror the masters' trainable flags so every replica produces the same set of gradients
        for rep in self.raw_replicas:
            for p0, p in zip(self._master_params, rep.parameters()):
                p.requires_grad_(p0.requires_grad)

        # Optionally compile each replica independently on its own device
        self.models: List[nn.Module] = []
        for i in range(self.num_gpus):
            m = self.raw_replicas[i]
            if self.compile_enabled and hasattr(torch, "compile"):
                try:
                    print(f"[Multi-GPU DP] Applying torch.compile to replica on {self.devices[i]}...")
                    m.compiled_forward_features = torch.compile(m.forward_features, mode=compile_mode)
                    m.compiled_chunked_loss = torch.compile(m.chunked_loss, mode=compile_mode)
                except Exception as e:
                    print(f"[Multi-GPU DP] torch.compile replica on {self.devices[i]} skipped ({e})")
            self.models.append(m)

        # DPO: a frozen reference copy on every GPU, next to the policy copy it scores against (forward_backward_dpo); a plain list, so
        # train()/eval() of the wrapper never touch them and they stay in eval mode
        self.ref_replicas: List[nn.Module] = [] if reference_model is None else [(reference_model if i == 0 else copy.deepcopy(reference_model)).to(d) for i, d in enumerate(self.devices)]
        for rep in self.ref_replicas:
            if self.compile_enabled and hasattr(torch, "compile"):
                rep.compiled_forward_features = torch.compile(rep.forward_features, mode=compile_mode)

        # Cross-GPU transfers (reduce_gradients / sync_weights) are staged through pinned host memory on these side streams (_copy_across)
        self._streams = [torch.cuda.Stream(device=d) for d in self.devices] if self.num_gpus > 1 else []
        self._pinned: Optional[torch.Tensor] = None  # byte buffer, grown on demand to the largest transfer batch
        self._pinned_reader: Optional[torch.cuda.Stream] = None  # stream that last read from the pinned buffer

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
        return self.raw_model.parameters(recurse=recurse)

    def named_parameters(self, prefix: str = "", recurse: bool = True):
        return self.raw_model.named_parameters(prefix=prefix, recurse=recurse)

    def state_dict(self, *args, **kwargs):
        return self.raw_model.state_dict(*args, **kwargs)

    def load_state_dict(self, state_dict, *args, **kwargs):
        res = self.raw_model.load_state_dict(state_dict, *args, **kwargs)
        self.adopt_primary_weights()
        return res

    def adopt_primary_weights(self):
        """Makes weights loaded into raw_model (checkpoint restore) the model's weights everywhere: here the masters are raw_model, so a sync suffices."""
        self.sync_weights()

    def train(self, mode: bool = True):
        super().train(mode)
        for rep in self.raw_replicas:  # plain list, not registered submodules: propagate train/eval by hand
            rep.train(mode)
        return self

    def forward(self, in_idx: torch.Tensor, use_cache: bool = False, activation_checkpointing: bool = False) -> torch.Tensor:
        """Standard (single-GPU) forward pass on the fp32 masters, e.g. sample generation, whose KV cache lives on raw_model."""
        return self.raw_model(in_idx.to(self.devices[0]), use_cache=use_cache, activation_checkpointing=activation_checkpointing)

    def forward_features(self, in_idx: torch.Tensor, activation_checkpointing: bool = False) -> torch.Tensor:
        return self.raw_model.forward_features(in_idx.to(self.devices[0]), activation_checkpointing=activation_checkpointing)

    @property
    def out_head(self):
        return self.raw_model.out_head

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
                # while the other traces under torch.compile deadlocks (GIL vs cache mutex). Without it each weight still in fp32 (embeddings,
                # norms, or everything when there is no compute copy) is cast to the compute dtype once per use, so little is lost.
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
                if raw_m is not self.raw_model:
                    self._accumulate_grads(gpu_idx)

            return loss.detach()

    def _accumulate_grads(self, gpu_idx: int) -> None:
        """Adds the compute copy's gradients (compute dtype for the low-precision weights) into fp32 accumulators, then frees them: the masters'
        .grad on device 0, _grad_bufs elsewhere. Summing accum_steps micro-steps in fp32 is what fp32 weights gave for free; a bf16 sum would
        drop small contributions the way bf16 weights dropped small updates."""
        bufs = self._grad_bufs[gpu_idx]
        with torch.no_grad():
            for k, p in enumerate(self.raw_replicas[gpu_idx].parameters()):
                if p.grad is None:
                    continue
                acc = self._master_params[k].grad if gpu_idx == 0 else bufs[k]
                acc = p.grad.to(torch.float32) if acc is None else acc.add_(p.grad)
                if gpu_idx == 0:
                    self._master_params[k].grad = acc
                else:
                    bufs[k] = acc
                p.grad = None

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
        self._amp_dtype = amp_dtype

        if self.num_gpus <= 1 or batch_size < self.num_gpus:
            dev0 = self.devices[0]
            inp = input_batch.to(dev0)
            tgt = target_batch.to(dev0)
            loss_val = self._compute_chunked_loss(
                0, inp, tgt, chunk_size, amp_dtype,
                activation_checkpointing, is_training, accum_steps, scaler
            )
            return loss_val, is_training

        # torch.chunk puts the remainder of an uneven split in the last chunk: reversed, the primary (fp32 masters, optimizer state, ZeRO-1's full copy) gets the smallest share
        chunks_in = torch.chunk(input_batch, self.num_gpus, dim=0)[::-1]
        chunks_tgt = torch.chunk(target_batch, self.num_gpus, dim=0)[::-1]
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

    def forward_backward_dpo(self, batch: Dict[str, Any], loss_fn: Any, amp_dtype: Optional[torch.dtype] = None, **kwargs) -> Tuple[torch.Tensor, ...]:
        """Data-parallel DPO step: the pairs of the batch are split across the GPUs and each runs loss_fn (compute_dpo_loss_batch or its
        precomputed variant, with the backward inside when kwargs carry backward_accum_steps) on its policy compute copy and its reference
        copy, both on that GPU; the copies' gradients go to the fp32 accumulators as in _compute_chunked_loss. Returns loss_fn's tuple of
        scalars averaged over the GPUs on device 0."""
        is_training = torch.is_grad_enabled() and self.training
        self._amp_dtype = amp_dtype
        n = min(self.num_gpus, batch["chosen"].shape[0])
        keys = [k for k in ("chosen", "rejected", "chosen_mask", "rejected_mask", "ref_chosen_logprob", "ref_rejected_logprob") if k in batch]
        parts = [dict(zip(keys, p)) for p in zip(*(torch.tensor_split(batch[k], n, dim=0) for k in keys))][::-1]  # tensor_split puts the extra pairs of an uneven split first: reversed, the primary gets the smallest share

        def _worker_step(gpu_idx: int) -> Tuple[torch.Tensor, ...]:
            dev = self.devices[gpu_idx]
            ref = {"reference_model": self.ref_replicas[gpu_idx], "ref_device": dev} if self.ref_replicas else {}
            with torch.cuda.device(dev), torch.set_grad_enabled(is_training):  # grad mode is thread-local (see _compute_chunked_loss)
                out = loss_fn(batch=parts[gpu_idx], policy_model=self.raw_replicas[gpu_idx], policy_device=dev, amp_dtype=amp_dtype, **ref, **kwargs)
                if is_training and self.raw_replicas[gpu_idx] is not self.raw_model:
                    self._accumulate_grads(gpu_idx)
            return out

        key = (is_training, tuple(batch["chosen"].shape))
        one_at_a_time = key not in self._compiled_keys and len(self._compiled_keys) < DYNAMO_RECOMPILE_LIMIT
        self._compiled_keys.add(key)
        futures = []
        for i in range(n):
            futures.append(self.executor.submit(_worker_step, i))
            if one_at_a_time:
                futures[-1].result()
        outs = [f.result() for f in futures]
        return tuple(torch.stack([o[j].to(self.devices[0], non_blocking=True) for o in outs]).mean() for j in range(len(outs[0])))

    def _transfer_dtype(self) -> Optional[torch.dtype]:
        """Wire dtype for the _lowp_* tensors: bf16 when training under bf16 autocast (fp32 exponent range, so loss-scaled gradients cannot
        overflow as they could in fp16), which halves the bytes of every reduce/sync over the ~6 GB/s GPU-to-GPU link. The eligible weights arrive
        bit-identical to what autocast computes from fp32 (the upcast is exact); each replica's 2-D gradient sum is rounded once per update to
        ~3 significant digits, far below the mini-batch noise it carries. fp32 and fp16 modes, and every other tensor, use the master dtype."""
        return torch.bfloat16 if self._amp_dtype == torch.bfloat16 else None

    COPY_CHUNK_BYTES: int = 16 << 20  # transfer pipeline granularity: the host-to-device copy of one chunk overlaps the device-to-host copy of the next
    COPY_BATCH_BYTES: int = 256 << 20  # tensors per pipelined transfer; bounds the temporaries (casts, landing buffers) alive at once and the pinned buffer

    def _copy_across(self, pairs: List[Tuple[torch.Tensor, torch.Tensor]], src: int, dst: int) -> None:
        """Copies every (source on device src, destination on device dst) pair of equal shape and dtype through pinned host memory, chunked
        and pipelined on the two side streams. Without peer-to-peer access a plain .to(device) also goes through system RAM, but one
        tensor at a time with the driver's own staging; this keeps the ~6 GB/s link busy end to end (measured on the 350M's 1.3 GB of
        gradients + weights per update: 521 ms -> 250 ms). Ordered after the producers on src and before the consumers on dst."""
        if not pairs:
            return
        s_src, s_dst = self._streams[src], self._streams[dst]
        src_dev, dst_dev = self.devices[src], self.devices[dst]
        jobs, offset = [], 0
        for s, d in pairs:
            sv, dv = s.view(-1), d.view(-1)
            step = max(1, self.COPY_CHUNK_BYTES // sv.element_size())
            for a in range(0, sv.numel(), step):
                b = min(sv.numel(), a + step)
                jobs.append((sv[a:b], dv[a:b], offset))
                offset += -(-((b - a) * sv.element_size()) // 256) * 256  # 256-byte aligned slots so any dtype can view its slot
        if self._pinned is None or self._pinned.numel() < offset:
            self._pinned = torch.empty(offset, dtype=torch.uint8, pin_memory=True)
        s_src.wait_stream(torch.cuda.current_stream(src_dev))  # sources are complete
        s_dst.wait_stream(torch.cuda.current_stream(dst_dev))  # destinations are no longer being read
        if self._pinned_reader is not None:
            s_src.wait_stream(self._pinned_reader)  # the previous transfer has finished reading the pinned buffer
        events = []
        with torch.cuda.stream(s_src):
            for sc, _, off in jobs:
                self._pinned[off:off + sc.numel() * sc.element_size()].view(sc.dtype).copy_(sc, non_blocking=True)
                e = torch.cuda.Event(); e.record(s_src); events.append(e)
        with torch.cuda.stream(s_dst):
            for (sc, dc, off), e in zip(jobs, events):
                s_dst.wait_event(e)
                dc.copy_(self._pinned[off:off + sc.numel() * sc.element_size()].view(sc.dtype), non_blocking=True)
        torch.cuda.current_stream(dst_dev).wait_stream(s_dst)
        torch.cuda.current_stream(src_dev).wait_stream(s_src)  # temporaries freed by the caller are only reused after their copy
        self._pinned_reader = s_dst

    def reduce_gradients(self):
        """Reduces and averages accumulated gradients from all secondary replicas onto primary replica: the 2-D sums cross the bus in the
        wire dtype (_transfer_dtype), everything else in fp32, batched into pipelined transfers (_copy_across). Once per optimizer update,
        not per micro-step."""
        if self.num_gpus <= 1:
            return
        for dev in self.devices:
            torch.cuda.synchronize(dev)
        scale = 1.0 / self.num_gpus
        lowp = self._transfer_dtype()
        with torch.no_grad():
            for i in range(1, self.num_gpus):
                pairs, landed, pending = [], [], 0

                def flush():
                    nonlocal pairs, landed, pending
                    self._copy_across(pairs, i, 0)
                    for m, g in landed:
                        m.grad = g.to(torch.float32) if m.grad is None else m.grad.add_(g)
                    pairs, landed, pending = [], [], 0

                for k, (m, buf) in enumerate(zip(self._master_params, self._grad_bufs[i])):
                    if buf is None:
                        continue
                    g = buf.to(lowp) if lowp is not None and k in self._lowp_grad_idx else buf
                    land = torch.empty_like(g, device=m.device)
                    pairs.append((g, land)); landed.append((m, land))
                    pending += g.numel() * g.element_size()
                    if pending >= self.COPY_BATCH_BYTES:
                        flush()
                flush()
                self._grad_bufs[i] = [None] * len(self._master_params)

            for m in self._master_params:
                if m.grad is not None:
                    m.grad.mul_(scale)

    def sync_weights(self):
        """Propagates updated master weights and buffers to every compute copy: cast on the primary to the copy's dtype (or to the wire dtype for
        eligible weights that a copy still stores in fp32), then across the bus in batched pipelined transfers (_copy_across)."""
        lowp = self._transfer_dtype()
        with torch.no_grad():
            for i, rep in enumerate(self.raw_replicas):
                if rep is self.raw_model:
                    continue
                dev = self.devices[i]
                pairs, landed, pending = [], [], 0

                def flush():
                    nonlocal pairs, landed, pending
                    self._copy_across(pairs, 0, i)
                    for p, w in landed:
                        p.copy_(w)
                    pairs, landed, pending = [], [], 0

                for k, (m, p) in enumerate(zip(self._master_params, rep.parameters())):
                    if dev == m.device:
                        p.copy_(m)
                        continue
                    wire = p.dtype if p.dtype != m.dtype else (lowp if lowp is not None and k in self._lowp_weight_idx else m.dtype)
                    w = m.to(wire) if wire != m.dtype else m
                    if p.dtype == wire:
                        pairs.append((w, p))  # straight into the copy's parameter
                    else:
                        land = torch.empty_like(w, device=dev)
                        pairs.append((w, land)); landed.append((p, land))
                    pending += w.numel() * w.element_size()
                    if pending >= self.COPY_BATCH_BYTES:
                        flush()
                flush()
                for b0, b_other in zip(self.raw_model.buffers(), rep.buffers()):
                    b_other.data.copy_(b0.data.to(dev, non_blocking=True))

    def zero_grad(self, set_to_none: bool = True):
        self.raw_model.zero_grad(set_to_none=set_to_none)
        for r in self.raw_replicas:
            r.zero_grad(set_to_none=set_to_none)
        self._grad_bufs = [[None] * len(self._master_params) for _ in self.devices]
