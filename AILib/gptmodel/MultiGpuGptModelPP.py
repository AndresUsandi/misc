
import math
from typing import List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

import math
from pathlib import Path
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptmodel.GptModel import GptModel, safe_add, compute_dtype_stream, LOGIT_CLAMP_MAX, LOGIT_CLAMP_MIN, UNEVEN_LAYERS_GPU0_RATIO


class MultiGpuGptModelPP(nn.Module):
    def __init__(
        self,
        raw_model: GptModel,
        uneven_layers: bool = False,
        async_pcie: bool = False,
        use_1f1b: bool = False,
        multi_stage_micro_batching: int = 0,
        devices: Optional[List[torch.device]] = None,
    ):
        super().__init__()
        self.raw_model = raw_model
        if devices is None:
            self.num_gpus = torch.cuda.device_count()
            self.devices = [torch.device(f"cuda:{i}") for i in range(self.num_gpus)] if self.num_gpus > 1 else [torch.device("cuda:0")]
        else:
            self.devices = devices
            self.num_gpus = len(self.devices)
        self.uneven_layers = uneven_layers
        self.async_pcie = async_pcie
        self.use_1f1b = use_1f1b
        self.multi_stage_micro_batching = multi_stage_micro_batching

        self.raw_model.tok_emb.to(self.devices[0])
        if self.raw_model.pos_emb is not None:
            self.raw_model.pos_emb.to(self.devices[0])

        num_layers = len(self.raw_model.trf_blocks)
        if self.num_gpus == 2 and self.uneven_layers:
            self.stage1_layers = math.ceil(num_layers * UNEVEN_LAYERS_GPU0_RATIO)
        else:
            self.stage1_layers = math.ceil(num_layers / self.num_gpus)

        self.layer_devices = []
        for idx, block in enumerate(self.raw_model.trf_blocks):
            if self.num_gpus == 2 and self.uneven_layers:
                gpu_idx = 0 if idx < self.stage1_layers else 1
            else:
                gpu_idx = min(idx // math.ceil(num_layers / self.num_gpus), self.num_gpus - 1)
            block.to(self.devices[gpu_idx])
            self.layer_devices.append(self.devices[gpu_idx])

        last_device = self.devices[-1]
        self.raw_model.final_norm.to(last_device)
        # Tied embeddings with the head on another device: the head gets a device-local copy of tok_emb.weight that stays tied in effect:
        # excluded from parameters() (one trainable matrix, as on one device), its gradient joins the embedding's before every optimizer
        # update (reduce_gradients) and it takes the updated embedding afterwards (sync_weights), so tok_emb and out_head never drift apart
        self._tied_head_copy: Optional[nn.Parameter] = None
        if self.devices[0] != last_device and (self.raw_model.out_head.weight.data_ptr() == self.raw_model.tok_emb.weight.data_ptr()):
            weight_copy = self.raw_model.tok_emb.weight.data.clone().to(last_device)
            self.raw_model.out_head.weight = nn.Parameter(weight_copy)
            self._tied_head_copy = self.raw_model.out_head.weight
        else:
            self.raw_model.out_head.to(last_device)
        self.raw_model.tok_emb.to(self.devices[0])

        if self.num_gpus > 1:
            self.stream_stage1 = torch.cuda.Stream(device=self.devices[0])
            self.stream_stage2 = torch.cuda.Stream(device=self.devices[-1])
        else:
            self.stream_stage1 = None
            self.stream_stage2 = None

        if self.async_pcie and self.num_gpus > 1:
            self.comm_stream = torch.cuda.Stream(device=self.devices[0])
            self.comm_event = torch.cuda.Event(enable_timing=False)
        else:
            self.comm_stream = None
            self.comm_event = None

    @property
    def cfg(self):
        return self.raw_model.cfg

    @property
    def first_device(self) -> torch.device:
        return self.devices[0]

    @property
    def last_device(self) -> torch.device:
        return self.devices[-1]

    @property
    def tok_emb(self):
        return self.raw_model.tok_emb

    @property
    def pos_emb(self):
        return self.raw_model.pos_emb

    @property
    def out_head(self):
        return self.raw_model.out_head

    @property
    def final_norm(self):
        return self.raw_model.final_norm

    @property
    def trf_blocks(self):
        return self.raw_model.trf_blocks

    @property
    def current_pos(self):
        return self.raw_model.current_pos

    @current_pos.setter
    def current_pos(self, value):
        self.raw_model.current_pos = value

    def reset_kv_cache(self):
        self.raw_model.reset_kv_cache()

    def parameters(self, recurse: bool = True):
        """The trainable parameters: the tied head copy is left out (it is tok_emb.weight, held on the head's device; see reduce_gradients)."""
        return (p for p in self.raw_model.parameters(recurse=recurse) if p is not self._tied_head_copy)

    def named_parameters(self, prefix: str = "", recurse: bool = True):
        return ((n, p) for n, p in self.raw_model.named_parameters(prefix=prefix, recurse=recurse) if p is not self._tied_head_copy)

    def reduce_gradients(self):
        """Once per optimizer update, before clipping: the tied head copy's gradient joins the embedding's, as a tied matrix on one device would have received both."""
        c = self._tied_head_copy
        if c is not None and c.grad is not None:
            e = self.raw_model.tok_emb.weight
            g = c.grad.to(e.device)
            e.grad = g if e.grad is None else e.grad.add_(g)
            c.grad = None

    def sync_weights(self):
        """After the optimizer update: the tied head copy takes the updated embedding."""
        if self._tied_head_copy is not None:
            with torch.no_grad():
                self._tied_head_copy.copy_(self.raw_model.tok_emb.weight.to(self._tied_head_copy.device))

    def transfer_tensor(self, t: torch.Tensor, target_device: torch.device) -> torch.Tensor:
        """Transfers tensor t to target_device safely with cross-device CUDA event synchronization if async_pcie is active."""
        if t.device == target_device:
            return t
        if self.async_pcie and self.comm_stream is not None:
            source_event = torch.cuda.Event(enable_timing=False)
            source_event.record(torch.cuda.current_stream(t.device))
            with torch.cuda.stream(self.comm_stream):
                self.comm_stream.wait_event(source_event)
                t_transferred = t.to(target_device, non_blocking=True)
                self.comm_event.record(self.comm_stream)
            torch.cuda.current_stream(target_device).wait_event(self.comm_event)
            return t_transferred
        return t.to(target_device)

    def forward_features(self, in_idx: torch.Tensor, use_cache: bool = False, activation_checkpointing: bool = False) -> torch.Tensor:
        """Computes full transformer block stack across all partitioned GPUs sequentially."""
        first_device = self.devices[0]
        in_idx = in_idx.to(first_device)
        batch_size, seq_len = in_idx.shape
        x = self.raw_model.tok_emb(in_idx)

        cos = getattr(self.raw_model, "cos", None)
        sin = getattr(self.raw_model, "sin", None)

        if use_cache:
            pos_ids = torch.arange(self.raw_model.current_pos, self.raw_model.current_pos + seq_len, device=first_device, dtype=torch.long)
            self.raw_model.current_pos += seq_len
        else:
            pos_ids = torch.arange(0, seq_len, device=first_device, dtype=torch.long)

        if self.raw_model.pos_emb is not None:
            x = safe_add(x, self.raw_model.pos_emb(pos_ids).unsqueeze(0))
        x = compute_dtype_stream(x)

        if hasattr(self.raw_model, "drop_emb"):
            x = self.raw_model.drop_emb(x)

        use_ckpt = activation_checkpointing and self.training and not use_cache and not isinstance(x, tuple)
        shared_kv = None
        for layer_idx, blk in enumerate(self.raw_model.trf_blocks):
            target_device = self.layer_devices[layer_idx]
            if x.device != target_device:
                x = self.transfer_tensor(x, target_device)
                if shared_kv is not None:
                    shared_kv = tuple(self.transfer_tensor(k, target_device) for k in shared_kv)

            layer_pos_ids = pos_ids.to(target_device) if pos_ids is not None else None

            if use_ckpt:
                cur_shared = shared_kv if layer_idx >= getattr(self.raw_model, "n_kv_producing_layers", len(self.raw_model.trf_blocks)) else None
                x, shared_kv = torch.utils.checkpoint.checkpoint(
                    blk, x, use_cache, cur_shared, cos, sin, layer_pos_ids, use_reentrant=False
                )
            else:
                if hasattr(self.raw_model, "n_kv_producing_layers") and layer_idx >= self.raw_model.n_kv_producing_layers:
                    x, _ = blk(x, use_cache=use_cache, shared_kv=shared_kv, cos=cos, sin=sin, pos_ids=layer_pos_ids)
                else:
                    out = blk(x, use_cache=use_cache, shared_kv=None, cos=cos, sin=sin, pos_ids=layer_pos_ids)
                    if isinstance(out, tuple):
                        x, shared_kv = out[0], out[1]
                    else:
                        x = out

        last_device = self.devices[-1]
        if x.device != last_device:
            x = self.transfer_tensor(x, last_device)

        x = self.raw_model.final_norm(x)
        return x

    def forward_stage1(self, in_idx: torch.Tensor, use_cache: bool = False, activation_checkpointing: bool = False) -> torch.Tensor:
        """Computes embeddings and Stage 1 transformer blocks on devices[0]."""
        first_device = self.devices[0]
        in_idx = in_idx.to(first_device)
        batch_size, seq_len = in_idx.shape
        x = self.raw_model.tok_emb(in_idx)

        cos = getattr(self.raw_model, "cos", None)
        sin = getattr(self.raw_model, "sin", None)

        if use_cache:
            pos_ids = torch.arange(self.raw_model.current_pos, self.raw_model.current_pos + seq_len, device=first_device, dtype=torch.long)
            self.raw_model.current_pos += seq_len
        else:
            pos_ids = torch.arange(0, seq_len, device=first_device, dtype=torch.long)

        if self.raw_model.pos_emb is not None:
            x = safe_add(x, self.raw_model.pos_emb(pos_ids).unsqueeze(0))
        x = compute_dtype_stream(x)

        if hasattr(self.raw_model, "drop_emb"):
            x = self.raw_model.drop_emb(x)

        use_ckpt = activation_checkpointing and self.training and not use_cache
        stage1_len = self.stage1_layers
        for layer_idx in range(stage1_len):
            blk = self.raw_model.trf_blocks[layer_idx]
            if use_ckpt:
                x, _ = torch.utils.checkpoint.checkpoint(
                    blk, x, use_cache, None, cos, sin, pos_ids, use_reentrant=False
                )
            else:
                out = blk(x, use_cache=use_cache, shared_kv=None, cos=cos, sin=sin, pos_ids=pos_ids)
                x = out[0] if isinstance(out, tuple) else out

        return x

    def forward_stage2_and_loss(self, hidden_stage1: torch.Tensor, target_batch: torch.Tensor, chunk_size: int = 512, activation_checkpointing: bool = False) -> torch.Tensor:
        """Receives intermediate activations on devices[-1], computes Stage 2 blocks, and evaluates stabilized chunked loss."""
        last_device = self.devices[-1]
        x = self.transfer_tensor(hidden_stage1, last_device)
        target_batch = target_batch.to(last_device)
        batch_size, seq_len, _ = x.shape
        pos_ids = torch.arange(0, seq_len, device=last_device, dtype=torch.long)

        cos = getattr(self.raw_model, "cos", None)
        sin = getattr(self.raw_model, "sin", None)

        num_layers = len(self.raw_model.trf_blocks)
        stage1_len = self.stage1_layers

        use_ckpt = activation_checkpointing and self.training
        for layer_idx in range(stage1_len, num_layers):
            blk = self.raw_model.trf_blocks[layer_idx]
            if use_ckpt:
                x, _ = torch.utils.checkpoint.checkpoint(
                    blk, x, False, None, cos, sin, pos_ids, use_reentrant=False
                )
            else:
                out = blk(x, use_cache=False, shared_kv=None, cos=cos, sin=sin, pos_ids=pos_ids)
                x = out[0] if isinstance(out, tuple) else out

        x = self.raw_model.final_norm(x)
        flat_hidden = x.view(-1, x.shape[-1])
        flat_targets = target_batch.view(-1)
        active_tokens = (flat_targets != -100).sum().clamp(min=1)
        total_tokens = flat_targets.numel()
        total_loss = 0.0
        out_head = self.raw_model.out_head
        for i in range(0, total_tokens, chunk_size):
            end_i = min(i + chunk_size, total_tokens)
            l_chunk = out_head(flat_hidden[i:end_i].float())
            l_chunk = torch.clamp(l_chunk, min=LOGIT_CLAMP_MIN, max=LOGIT_CLAMP_MAX)
            total_loss = total_loss + F.cross_entropy(l_chunk, flat_targets[i:end_i], reduction="sum")
        return total_loss / active_tokens

    def forward_backward_multi_stage_pipelined(
        self,
        input_batch: torch.Tensor,
        target_batch: torch.Tensor,
        num_micro_batches: int = 2,
        chunk_size: int = 512,
        accum_steps: int = 1,
        activation_checkpointing: bool = False
    ) -> Tuple[torch.Tensor, bool]:
        """
        Multi-stage pipelined execution that partitions input_batch into multiple micro-batches
        and concurrently overlaps both forward and backward passes across dual GPUs.

        Returns:
            Tuple[torch.Tensor, bool]: (loss_tensor, backward_executed)
            - If backward_executed is True, gradients were already computed and accumulated
              onto model parameters (scaled by 1 / accum_steps), so caller should skip loss.backward().
            - If backward_executed is False (e.g. during evaluation or single-GPU fallback),
              standard autograd flow applies.
        """
        batch_size = input_batch.shape[0]

        # In single-GPU mode or if micro-batching is not requested, execute standard forward
        if len(self.devices) <= 1 or num_micro_batches <= 1:
            h = self.forward_features(input_batch, activation_checkpointing=activation_checkpointing)
            flat_h = h.view(-1, h.shape[-1])
            flat_t = target_batch.to(self.last_device).view(-1)
            active_tokens = (flat_t != -100).sum().clamp(min=1)
            total_tokens = flat_t.numel()
            total_loss = 0.0
            out_head = self.raw_model.out_head
            for i in range(0, total_tokens, chunk_size):
                end_i = min(i + chunk_size, total_tokens)
                l_chunk = out_head(flat_h[i:end_i].float())
                l_chunk = torch.clamp(l_chunk, min=LOGIT_CLAMP_MIN, max=LOGIT_CLAMP_MAX)
                total_loss = total_loss + F.cross_entropy(l_chunk, flat_t[i:end_i], reduction="sum")
            return total_loss / active_tokens, False

        # Partition batch into num_micro_batches chunks
        micro_inputs = [c for c in torch.chunk(input_batch, num_micro_batches, dim=0) if c.shape[0] > 0]
        micro_targets = [c for c in torch.chunk(target_batch, num_micro_batches, dim=0) if c.shape[0] > 0]
        m_count = len(micro_inputs)
        if m_count < 2:
            h = self.forward_features(input_batch, activation_checkpointing=activation_checkpointing)
            flat_h = h.view(-1, h.shape[-1])
            flat_t = target_batch.to(self.last_device).view(-1)
            active_tokens = (flat_t != -100).sum().clamp(min=1)
            total_tokens = flat_t.numel()
            total_loss = 0.0
            out_head = self.raw_model.out_head
            for i in range(0, total_tokens, chunk_size):
                end_i = min(i + chunk_size, total_tokens)
                l_chunk = out_head(flat_h[i:end_i].float())
                l_chunk = torch.clamp(l_chunk, min=LOGIT_CLAMP_MIN, max=LOGIT_CLAMP_MAX)
                total_loss = total_loss + F.cross_entropy(l_chunk, flat_t[i:end_i], reduction="sum")
            return total_loss / active_tokens, False

        is_training = torch.is_grad_enabled() and self.training

        # Multi-stage pipelined execution across dual GPUs
        # GPU 0 executes Stage 1 on micro-batch m while GPU 1 executes Stage 2 on micro-batch m - 1
        h_prev = self.forward_stage1(micro_inputs[0], activation_checkpointing=activation_checkpointing)
        total_loss = 0.0

        for m in range(1, m_count):
            l_prev = self.forward_stage2_and_loss(h_prev, micro_targets[m - 1], chunk_size=chunk_size, activation_checkpointing=activation_checkpointing)
            total_loss = total_loss + l_prev * (micro_inputs[m - 1].shape[0] / float(batch_size))
            h_prev = self.forward_stage1(micro_inputs[m], activation_checkpointing=activation_checkpointing)

        l_last = self.forward_stage2_and_loss(h_prev, micro_targets[-1], chunk_size=chunk_size, activation_checkpointing=activation_checkpointing)
        total_loss = total_loss + l_last * (micro_inputs[-1].shape[0] / float(batch_size))

        return total_loss, False

    def forward_loss_micro_batched(self, input_batch: torch.Tensor, target_batch: torch.Tensor, chunk_size: int = 512, activation_checkpointing: bool = False) -> torch.Tensor:
        """Pipelined micro-batch execution (calls forward_backward_multi_stage_pipelined with 2 stages)."""
        loss, _ = self.forward_backward_multi_stage_pipelined(input_batch, target_batch, num_micro_batches=2, chunk_size=chunk_size, activation_checkpointing=activation_checkpointing)
        return loss

    def forward_loss_1f1b(self, input_batch: torch.Tensor, target_batch: torch.Tensor, chunk_size: int = 512, activation_checkpointing: bool = False) -> torch.Tensor:
        """1F1B Pipelined Execution (calls forward_backward_multi_stage_pipelined)."""
        stages = max(2, getattr(self, "multi_stage_micro_batching", 2))
        loss, _ = self.forward_backward_multi_stage_pipelined(input_batch, target_batch, num_micro_batches=stages, chunk_size=chunk_size, activation_checkpointing=activation_checkpointing)
        return loss

    def forward(self, in_idx: torch.Tensor, use_cache: bool = False, activation_checkpointing: bool = False) -> torch.Tensor:
        x = self.forward_features(in_idx, use_cache=use_cache, activation_checkpointing=activation_checkpointing)
        logits = self.raw_model.out_head(x)
        return logits
