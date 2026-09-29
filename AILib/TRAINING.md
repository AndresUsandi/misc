# LLM Pre-Training Dynamics, Scaling Laws & Operational Guide

This guide details the mathematical foundations, loss curve dynamics, scaling behaviors across model sizes, and diagnostic indicators for autoregressive Transformer pre-training.

---

## 1. Mathematical Foundations: Loss & Perplexity

Autoregressive language models are trained using **Causal Language Modeling (CLM)**, which minimizes the cross-entropy loss over sequential next-token predictions:

$$\mathcal{L} = -\frac{1}{T} \sum_{t=1}^T \log P(w_t \mid w_1, w_2, \dots, w_{t-1})$$

Where:
* $T$ is the total sequence length (tokens).
* $w_t$ is the ground-truth target token at step $t$.
* $P(w_t \mid \dots)$ is the softmax probability assigned by the model to the target token.

### The Perplexity Metric
**Perplexity ($\text{PPL}$)** represents the exponential of the cross-entropy loss:

$$\text{PPL} = e^{\mathcal{L}} = \exp(\mathcal{L})$$

Perplexity measures the **effective size of the candidate pool** the model is choosing among at each step:

| Cross-Entropy Loss ($\mathcal{L}$) | Perplexity ($e^{\mathcal{L}}$) | Model State / Qualitative Behavior |
| :---: | :---: | :--- |
| **~10.82** | **~50,304** | **Step 0 (Random Guessing)**: Equal probability over entire vocabulary ($V = 50,304$). |
| **~8.00** | **~2,980** | **Subword / Space Calibration**: Knows common prefixes, spaces, punctuation. |
| **~6.50** | **~665** | **Basic Syntax**: Recognizes common stop-words (*the, is, and, of*) and capitalization. |
| **~5.75** | **~315** | **Grammar & Collocation**: Understands sentence framing, subject-verb order, and idioms. |
| **~4.50** | **~90** | **Paragraph Coherence**: Produces grammatical, topically consistent sentences. |
| **~3.50** | **~33** | **Fluent Generation**: Coherent reasoning, structured thought, and context retention. |
| **~2.50** | **~12** | **Near-Human Text Density**: Typical of frontier models on clean domains. |

> **Why did Step 0 loss start at ~10.8?**  
> For vocabulary size $V = 50,304$, a uniformly random prediction assigns probability $P = \frac{1}{50,304}$ to every token:
> $$\mathcal{L}_{\text{random}} = -\ln\left(\frac{1}{50,304}\right) = \ln(50,304) \approx \mathbf{10.8258}$$
> Any properly initialized model (regardless of whether it has 100M or 100B parameters) **must** begin training within $[10.8, 11.5]$.

---

## 2. The 3 Macro Phases of Pre-Training

Pre-training does not follow a linear drop. Instead, it proceeds through three distinct phases:

```
Loss
 11.0 ┼─┐  Phase 1: Rapid Vocabulary/Syntax Calibration (Steps 0 - 500)
 10.0 │ └──┐
  8.0 │    └──┐
  6.5 │       └───────────────────────────────────┐  Phase 2: The Structural Plateau
  5.5 │                                           └────────────┐ (Steps 500 - 50k+)
  4.0 │                                                        └───┐ Phase 3: Cosine Annealing
  3.0 │                                                            └───────────>
      └──────────────────────────────────────────────────────────────────────── Step
```

### Phase 1: Rapid Calibration (Steps 0 – 500 | Loss $11.0 \to 7.0$)
* **Mechanism**: The model rapidly discovers high-frequency unigram statistics. In English text, spaces, punctuation, and a handful of stopwords (*the, of, to, in, and, a*) account for over 30% of all tokens.
* **Trajectory**: Loss plunges vertically within the first few dozen steps.

### Phase 2: The Structural Plateau (Steps 500 – 50,000+ | Loss $7.0 \to 5.5$)
* **Mechanism**: The model learns syntax, agreement, and local phrase dependencies.
* **Why the curve flattens out**:
  1. **High Learning Rate Exploration**: During this phase, the learning rate is at or near its peak (`0.0005`). The optimizer takes large steps across the loss landscape to find wide, generalizable basins rather than settling into narrow local minima.
  2. **Multi-Domain Entropy Variations**: When training files alternate between conversational text (PersonaChat), instruction formats (Alpaca), encyclopedic text (WikiText), and fiction (WritingPrompts), each domain has different entropy. Loss will naturally bounce between `5.4` and `6.1` depending on the complexity of the current batch.
  3. **High-Order Information Density**: Moving from predicting simple grammar to predicting specific factual words or narrative progression is mathematically harder and requires digesting millions of tokens.

### Phase 3: Cosine Annealing & Semantic Convergence (Loss $5.5 \to 3.5$)
* **Mechanism**: As the global step count enters the second half of the schedule, the **Cosine Learning Rate Decay** begins reducing the step size:
  $$\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})\left(1 + \cos\left(\frac{t - t_{\text{warmup}}}{T - t_{\text{warmup}}} \pi\right)\right)$$
* **Trajectory**: As the learning rate "cools", the optimizer settles from broad exploration into the deepest, flattest minima of the loss surface. The loss begins its second descent toward the 3.0 – 4.0 range.

---

## 3. Architecture Scaling: Small vs. Medium vs. Large Models

Model behavior, memory bottlenecks, and stability requirements scale non-linearly with model parameter count:

| Dimension | Small Models (~100M – 350M) | Medium Models (~750M – 1.5B) | Large / Frontier Models (7B – 70B+) |
| :--- | :--- | :--- | :--- |
| **Representative Models** | GPT-2 (124M/355M), `andres1-124M` | GPT-2 (774M/1.5B), **`andres1-s (1B)`** | LLaMA-3 (8B/70B), Qwen-2.5 (7B/72B) |
| **Embedding Dimension ($D$)** | $768 - 1,024$ | $1,280 - 2,048$ | $4,096 - 8,192$ |
| **Transformer Layers ($L$)** | $12 - 24$ | $16 - 36$ | $32 - 80$ |
| **Attention Heads ($H$)** | $12 - 16$ | $16 - 25$ | $32 - 64$ (Grouped-Query Attention) |
| **Peak Learning Rate** | $5.0 \times 10^{-4} - 1.0 \times 10^{-3}$ | $1.5 \times 10^{-4} - 5.0 \times 10^{-4}$ | $1.0 \times 10^{-4} - 3.0 \times 10^{-4}$ |
| **Warmup Sensitivity** | Low ($10 - 50$ steps sufficient) | **Critical** ($20 - 500$ steps) | **Vital** ($1,000 - 5,000$ steps) |
| **Gradient Clipping Norm** | $1.0$ | $1.0$ | $0.5 - 1.0$ |
| **Dominant VRAM Consumer** | Activations ($B \times S \times L \times D$) | **Optimizer States** ($12 \times N$ bytes for AdamW) | Distributed Model Shards (FSDP / ZeRO-3) |
| **Recommended Optimizer** | Fused AdamW | **CustomMuon + AdamW** or Fused AdamW | Muon / AdamW (8-bit or Distributed) |
| **Chinchilla Optimal Tokens** | ~2.5 Billion tokens | **~20 Billion tokens** | ~140B – 2+ Trillion tokens |

### Key Scaling Principles:
1. **The Learning Rate Inversion Law**: Larger models have wider layers ($D = 2048$) and deeper graphs. Large weight updates accumulate larger variance across layers. Therefore, **as model width increases, peak learning rate must decrease**:
   $$\text{LR}_{\text{peak}} \propto \frac{1}{\sqrt{D}} \quad \text{or} \quad \frac{1}{\sqrt{N}}$$
2. **Residual Connection Scaling**: In deep networks ($L \ge 16$), unscaled residual streams cause activation variance to grow as $O(L)$. Scaling residual projection layers (`att.out_proj` and `ffn.fc2/fc3`) by $\frac{0.02}{\sqrt{2L}}$ is required to prevent early layer saturation.
3. **Optimizer Memory Bottleneck at 1B**:
   * For a 1B model, weights take 2 GB (BF16).
   * Gradients take 2 GB (BF16).
   * **AdamW optimizer states take 12 GB (FP32 master weights + 1st moment $m$ + 2nd moment $v$)**.
   * On consumer GPUs (8GB – 12GB), standard AdamW causes OOM. **Muon** solves this by applying Newton-Schulz orthogonalized momentum updates directly to 2D weight matrices using 16-bit buffers, cutting optimizer memory by ~75%.

---

## 4. Hardware Execution & Pipeline Parallelism

Training a 1B model on dual consumer GPUs requires balancing both compute and memory across the PCIe bus:

```
┌────────────────────────────────────────┐       ┌────────────────────────────────────────┐
│                 GPU 0                  │       │                 GPU 1                  │
│  • Token & Position Embeddings         │ PCIe  │  • Transformer Blocks (Remaining 40%)  │
│  • Transformer Blocks (First 60%)      │──────>│  • Final RMSNorm / LayerNorm           │
│  • Micro-batch Stage 1 Forward/Backward│<──────│  • Vocabulary LM Head (50,304 x 2,048) │
│                                        │ Activ │  • Chunked Cross-Entropy Loss          │
└────────────────────────────────────────┘       └────────────────────────────────────────┘
```

### Why the 60/40 Uneven Layer Split is Necessary
* **GPU 1 Bottleneck**: GPU 1 computes the final output projection matrix ($50,304 \times 2,048 = 103\text{M parameters}$) and the high-memory Cross-Entropy softmax over all 50,304 logits.
* **Balancing Strategy**: By placing **60% of the transformer layers on GPU 0** (e.g., 10 layers) and **40% on GPU 1** (e.g., 6 layers), GPU VRAM and compute time are balanced equally (~4.6 GB on GPU 0 vs ~3.1 GB on GPU 1).

### Micro-Batching & Pipelined Execution
Instead of executing the entire physical batch ($B=4$) sequentially, multi-stage micro-batching divides the batch into $K$ chunks (e.g., $K=4$). While GPU 1 computes Stage 2 for Micro-Batch 1, GPU 0 is already computing Stage 1 for Micro-Batch 2, eliminating idle pipeline bubbles.

---

## 5. Diagnostic Log Analysis: How to Read Training Metrics

When monitoring real-time logs:

```text
[2026-09-03 19:18:19] Ep 1/3 (Step 000831/013886 | Global 016575/249948): Train 5.597, Val 5.785 | Step tok/sec: 14,597, Avg tok/sec: 14,110 | Eval: 0.52s | LR: 0.000480 | VRAM: [cuda:0: 4.6G, cuda:1: 3.1G]
```

### Health Checklist:
1. **$\text{Val Loss} \approx \text{Train Loss}$ (Generalization)**:
   * **Healthy**: Validation loss is equal to or slightly lower than train loss (`Val 5.78` vs `Train 5.59 – 5.99`). Because validation batches have no dropout/noise and evaluate smoothly, this confirms the model is generalizing rather than memorizing.
   * **Overfitting Alert**: Train loss drops to `~2.0` while Val loss starts climbing upward (`5.8` $\to$ `6.5` $\to$ `7.2`).
2. **Throughput Stability**:
   * Average throughput should remain consistent (~14,000 tokens/sec). Sudden drops to <5,000 tok/sec indicate CPU dataloader bottlenecks, thermal throttling, or disk read stalls.
3. **Memory Ceiling**:
   * VRAM should establish a fixed ceiling on Step 1 (e.g., `cuda:0: 4.6G, cuda:1: 3.1G`) and never grow over time. Increasing VRAM indicates tensor retention leaks in python collections.
4. **Learning Rate Trajectory**:
   * Steps $0 \to 20$: Ramping from `0.0` to `0.0005` (Linear Warmup).
   * Steps $20 \to 250,000$: Smooth downward cosine curve toward `0.00001` (Cosine Annealing).

---

## 6. Common Failure Modes & Solutions

| Failure Mode | Symptoms | Root Cause | Solution |
| :--- | :--- | :--- | :--- |
| **Mode Collapse** | Outputs infinite repeated punctuation (e.g., `.......`); Step 0 loss starts at $>50.0$. | Uninitialized weights; embeddings starting at PyTorch default $\mathcal{N}(0, 1.0)$ ($2,500\times$ too high). | Implement `_init_weights` with $\mathcal{N}(0, 0.02)$ and residual scaling $\frac{0.02}{\sqrt{2L}}$. |
| **Loss Explosion (NaN / Inf)** | Loss suddenly spikes from $5.0 \to \text{NaN}$; gradients evaluate to `inf`. | Learning rate too high for model width; missing gradient clipping. | Set `--learning_rate 1.5e-4 - 2e-4`, ensure `clip_grad_norm_ = 1.0`, and use `--warmup_steps 20+`. |
| **CUDA Out of Memory (OOM)** | Process crashes on forward/backward pass with `CUDA out of memory`. | Activation memory explosion ($B \times S$) or AdamW states ($12 \times N$). | 1. Enable `--use_muon` to cut optimizer VRAM by 3x.<br>2. Reduce `--batch_size` to 2 and increase `--accum_steps` to 4.<br>3. Enable `--activation_checkpointing`. |
| **Pipeline Bubble Stalling** | Low GPU utilization (<50%) despite high compute capability. | GPUs waiting on each other across sequential forward/backward passes. | Enable `--multi_stage_micro_batching 4` and `--async_pcie` to overlap communication with compute. |

---

## 7. Pre-Training Milestone Expectations (1B Model)

| Total Tokens Processed | Approximate Loss | Model Capabilities & Text Quality |
| :---: | :---: | :--- |
| **0 – 1 Million** | $11.0 \to 8.0$ | Pure noise transitioning to random English words with spaces and basic punctuation. |
| **1M – 50 Million** | $8.0 \to 6.0$ | Common grammatical structures appear; phrases like *"The company announced that..."* form, but semantic meaning drifts after 5 words. |
| **50M – 500 Million** | $6.0 \to 5.0$ | *(Current Run)* Solid sentence-level syntax, realistic dialogue cadence, topic consistency across 1–2 sentences. |
| **500M – 2 Billion** | $5.0 \to 4.0$ | Full paragraph coherence; factual knowledge retrieval; logical continuation of stories and instructions. |
| **2B – 20+ Billion** | $4.0 \to 3.0$ | High-precision knowledge representation, complex syntactic nesting, zero-shot question answering capability. |
