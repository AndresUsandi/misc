# LLM Architecture Sizing & GPU VRAM Guide

This guide details the mathematical foundations of LLM parameter calculation, memory allocation, and hardware VRAM requirements for pretraining and fine-tuning.

---

## 1. Parameter Count Formula

The total parameter count ($N$) of a standard autoregressive transformer model is calculated from its hyperparameters:

$$\text{Total Parameters} \approx (\text{vocab\_size} \times \text{emb\_dim}) + \Big(\text{n\_layers} \times 12 \times \text{emb\_dim}^2\Big)$$

### Where does $12 \times \text{emb\_dim}^2$ per layer come from?

Every Transformer block contains two core modules:

#### A. Multi-Head Attention ($4 \times \text{emb\_dim}^2$)
* **Query, Key, Value Projections ($W_q, W_k, W_v$)**:
  $$3 \times (\text{emb\_dim} \times \text{emb\_dim}) = 3 \times \text{emb\_dim}^2$$
* **Output Projection ($W_{out}$)**:
  $$\text{emb\_dim} \times \text{emb\_dim} = 1 \times \text{emb\_dim}^2$$
* **Total Attention Weights**: $4 \times \text{emb\_dim}^2$ *(Biases add $4 \times \text{emb\_dim}$, which is negligible)*

#### B. Feed-Forward Network / MLP ($8 \times \text{emb\_dim}^2$)
* **Linear 1 (4× expansion)**:
  $$\text{emb\_dim} \times (4 \times \text{emb\_dim}) = 4 \times \text{emb\_dim}^2$$
* **Linear 2 (projection down)**:
  $$(4 \times \text{emb\_dim}) \times \text{emb\_dim} = 4 \times \text{emb\_dim}^2$$
* **Total MLP Weights**: $8 \times \text{emb\_dim}^2$

#### C. Normalization & Embeddings
* **Token Embeddings**: $\text{vocab\_size} \times \text{emb\_dim}$
* **Positional Embeddings**: $\text{context\_length} \times \text{emb\_dim}$
* **LayerNorm / RMSNorm**: $4 \times \text{emb\_dim} \times \text{n\_layers}$ *(negligible)*
* **Output LM Head**: Weight-tied with token embedding (0 extra) or explicit ($\text{vocab\_size} \times \text{emb\_dim}$).

---

## 2. Standard Model Size Presets

| Model Size | Layers (`n_layers`) | Hidden Dim (`emb_dim`) | Heads (`n_heads`) | Head Dim | Context | Total Params |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **124M (Small)** | 12 | 768 | 12 | 64 | 1024 | **~124 Million** |
| **355M (Medium)** | 24 | 1024 | 16 | 64 | 1024 | **~355 Million** |
| **774M (Large)** | 36 | 1280 | 20 | 64 | 1024 | **~774 Million** |
| **1.0B (Balanced)** | 16 | 2048 | 16 | 128 | 2048 | **~1.01 Billion** |
| **1.0B (Ultra-Wide)** | 12 | 2560 | 20 | 128 | 2048 | **~1.07 Billion** |
| **1.5B (XL)** | 48 | 1600 | 25 | 64 | 1024 | **~1.55 Billion** |

---

## 3. GPU VRAM Requirements During Training

Total VRAM required for training is split into **Static Memory** (model + optimizer) and **Dynamic Memory** (activations during the forward pass):

$$\text{Total VRAM} = \text{Model Weights} + \text{Gradients} + \text{Optimizer States} + \text{Activations} + \text{CUDA Overhead}$$

### A. Static Memory (Fixed by Model Size $N$)

In standard 16-bit Mixed Precision training (BF16 or FP16 with AMP):

| Component | Precision | Bytes / Param | For 124M Model | For 1.0B Model |
| :--- | :--- | :---: | :---: | :---: |
| **Model Weights** | FP16 / BF16 | 2 bytes | 0.25 GB | 2.0 GB |
| **Gradients** | FP16 / BF16 | 2 bytes | 0.25 GB | 2.0 GB |
| **AdamW Optimizer** | FP32 master weights (4B) + 1st moment $m$ (4B) + 2nd moment $v$ (4B) | 8 – 12 bytes | 1.00 – 1.50 GB | 8.0 – 12.0 GB |
| **Static Memory Subtotal** | — | **~14 – 16 bytes** | **~1.7 – 2.0 GB** | **~14.0 – 16.0 GB** |

> **Inference Note**: During pure inference (no backward pass, no optimizer), only the **Model Weights (2 bytes / param = ~2.0 GB for 1B)** plus KV cache are needed.

---

### B. Dynamic Memory (Activations)

Activations are the intermediate tensors stored during the forward pass so backpropagation can calculate gradients.

$$\text{Activation VRAM} \approx \text{Batch Size } (B) \times \text{Context Length } (S) \times \text{Layers } (L) \times \text{emb\_dim } (D)$$

Key scaling behaviors:
* **Context Length ($S$)**: Standard Self-Attention maps scale **quadratically** with sequence length ($S^2$). Doubling context from 1024 $\to$ 2048 increases attention matrix memory by **4×**.
* **Batch Size ($B$)**: Activation memory scales **linearly** with physical batch size.

---

## 4. Hardware Optimization Strategies

When training larger models (e.g. 1B+) on consumer or workstation GPUs (12GB – 24GB VRAM):

### 1. Activation Checkpointing (Gradient Checkpointing)
* Drops intermediate activation tensors from VRAM during the forward pass and recomputes them on-demand during the backward pass.
* **Savings**: Reduces activation memory by **~75% to 80%** at the cost of only ~15% to 20% compute overhead.

### 2. Gradient Accumulation
* Simulates large batch sizes without storing large activation batches simultaneously:
  $$\text{Effective Batch Size} = \text{batch\_size} \times \text{accum\_steps}$$
* Allows using physical `batch_size = 1` or `2` to keep peak activation memory under 2 GB.

### 3. Flash Attention / SDPA (`torch.nn.functional.scaled_dot_product_attention`)
* Computes exact attention in fast GPU SRAM tiles without materializing the $S \times S$ attention matrix in global VRAM.
* Eliminates the $O(S^2)$ memory bottleneck.

### 4. Tensor Core Vocabulary Padding
* Padding `vocab_size` from `50,257` to `50,304` (multiple of 64/128) aligns matrix dimensions to Nvidia Tensor Core warps, increasing GEMM matrix-multiply throughput by up to **1.5×–2.0×**.
