import json
from functools import partial
from pathlib import Path
import mmap
import queue
import random
import re
import sys
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast
import numpy as np
import torch
from torch.utils.data import IterableDataset

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from argsutil import TrainingArgs
from gptio.pathutil import STAGE_OPTIMIZE, STAGE_TRAIN, STAGE_TUNE
from gptio.cache import init_streaming_dataset_cache, calculate_file_steps, normalize_file_key, save_steps_cache, steps_plan_key
from gptio.tokencache import load_token_cache
from gptutils.consoleutils import print

# Length-sorting window for fine-tuning items, in multiples of batch_size items: items are sorted by length within a window and packed
# into token-budget batches, so each batch pads to a similar length (file order padded 2.4x the real tokens on the alpaca data, a
# 64 x batch_size window pads ~1.03x)
LENGTH_GROUP_WINDOW: int = 64
STEP_ESTIMATE_SAMPLE: int = 1024  # items tokenized per unseen file to estimate its padded tokens (and so its steps) before the first pass
PACKING_FILL: float = 0.93  # measured padded-token utilization of length-grouped token-budget batches
CHATML_TURN_RE = re.compile(r"<\|im_start\|>(\w+)\n(.*?)<\|im_end\|>", re.S)  # (role, content) of each ChatML turn


def round_up(n: int, multiple: int) -> int:
    """n rounded up to the next multiple (0 or None: unchanged), see --pad_to_multiple_of."""
    return -(-n // multiple) * multiple if multiple else n


def custom_dpo_collate_fn(
    batch: List[Dict[str, List[int]]],
    pad_token_id: int = 50256,
    allowed_max_length: Optional[int] = None,
    mask_prompt_tokens: bool = True,
    device: Union[str, torch.device] = "cpu",
    pad_to_multiple_of: int = 0,
) -> Dict[str, Any]:
    """
    Collates a batch of preference items into padded tensors and boolean masks.
    Masks out padding tokens and prompt tokens (+2 accounts for the newline tokens before ### Response).
    """
    batch_data: Dict[str, List[torch.Tensor]] = {
        "prompt": [],
        "chosen": [],
        "rejected": [],
        "chosen_mask": [],
        "rejected_mask": []
    }

    max_length_common = 0
    if batch:
        for key in ["chosen", "rejected"]:
            current_max = max(len(item[key]) + 1 for item in batch)
            max_length_common = max(max_length_common, current_max)
    max_length_common = round_up(max_length_common, pad_to_multiple_of)

    for item in batch:
        prompt_tensor = torch.tensor(item["prompt"], dtype=torch.long)
        batch_data["prompt"].append(prompt_tensor)

        for key in ["chosen", "rejected"]:
            sequence = item[key]
            padded = sequence + [pad_token_id] * (max_length_common - len(sequence))
            mask = torch.ones(len(padded), dtype=torch.bool)

            # Mask padding tokens
            mask[len(sequence):] = False

            # Mask prompt tokens (+2 sets the 2 newline tokens before ### Response to False for legacy format)
            if mask_prompt_tokens:
                offset = 0 if item.get("is_chat", True) else 2
                mask[:prompt_tensor.shape[0] + offset] = False

            batch_data[key].append(torch.tensor(padded, dtype=torch.long))
            batch_data[f"{key}_mask"].append(mask)

    result: Dict[str, Any] = {"prompt": batch_data["prompt"]}
    for key in ["chosen", "rejected", "chosen_mask", "rejected_mask"]:
        stacked = torch.stack(batch_data[key])
        if allowed_max_length is not None:
            stacked = stacked[:, :allowed_max_length]
        result[key] = stacked.to(device)

    if batch and "ref_chosen_logprob" in batch[0] and "ref_rejected_logprob" in batch[0]:
        result["ref_chosen_logprob"] = torch.tensor([item["ref_chosen_logprob"] for item in batch], dtype=torch.float32, device=device)
        result["ref_rejected_logprob"] = torch.tensor([item["ref_rejected_logprob"] for item in batch], dtype=torch.float32, device=device)

    return result


class PrefetchIterator:
    """
    Background-threaded queue iterator that prefetches items ahead of time.
    Prefetches batches within files and across file boundaries, ensuring the training
    engine never starves for data while disk I/O, JSON deserialization, or tokenization occurs.
    """
    _SENTINEL = object()

    def __init__(self, generator_func, queue_size: int = 64):
        self.generator_func = generator_func
        self.queue_size = max(1, queue_size)

    def __iter__(self):
        q: queue.Queue = queue.Queue(maxsize=self.queue_size)
        stop_event = threading.Event()

        def producer():
            try:
                for item in self.generator_func():
                    while not stop_event.is_set():
                        try:
                            q.put(item, timeout=0.1)
                            break
                        except queue.Full:
                            continue
                    if stop_event.is_set():
                        break
            except Exception as e:
                q.put((self._SENTINEL, e))
                return
            finally:
                q.put((self._SENTINEL, None))

        worker = threading.Thread(target=producer, daemon=True)
        worker.start()

        try:
            while True:
                item = q.get()
                if isinstance(item, tuple) and len(item) == 2 and item[0] is self._SENTINEL:
                    err = item[1]
                    if err is not None:
                        raise err
                    break
                yield item
        finally:
            stop_event.set()
            while not q.empty():
                try:
                    q.get_nowait()
                except queue.Empty:
                    break


def length_grouped_batches(window: List[Any], batch_size: int, length_key: Callable[[Any], int], rng: random.Random, max_length: int) -> List[List[Any]]:
    """
    Sorts a window of items by length and packs consecutive items into batches under a token budget of batch_size x max_length padded
    tokens: a batch holds batch_size items at max_length and proportionally more when they are shorter, so every micro-step carries the
    same GPU work as the largest batch while peak memory cannot exceed it. The batch order is shuffled (reproducible via rng).
    """
    budget = batch_size * max_length
    batches: List[List[Any]] = []
    batch: List[Any] = []
    for item in sorted(window, key=length_key):  # ascending: the item being added is the longest, so it sets the padded length
        if batch and (len(batch) + 1) * length_key(item) > budget:
            batches.append(batch)
            batch = []
        batch.append(item)
    if batch:
        batches.append(batch)
    rng.shuffle(batches)
    return batches


EVAL_BUFFER_SEED: int = 4242  # the fixed evaluation buffers are the same in every run and after every resume
DATASET_EVAL_BATCHES: int = 2  # batches per source dataset in the per-dataset validation breakdown


class StreamingTextDataset(IterableDataset):
    """
    The pretraining corpus as one pool of fixed context-length windows (stride = context length) drawn from every file: each file is
    tokenized once into a memory-mapped token cache (gptio.tokencache), its windows are split train/val by --train_ratio (the val
    windows are the tail of the file), and an epoch is a seeded permutation of the train windows of all files, so every batch mixes
    all sources. (Streaming one file at a time trained ~130M tokens of a single source in a row, and each file overwrote part of what
    the files before it had taught.) Resume replays the epoch's permutation and skips the steps already done; step counts are exact
    from the first step. Fixed, seeded evaluation buffers sampled across all files replace the per-file evaluation: a held-out val
    set, a train probe drawn the same way (so the Val - Train gap measures memorization, not a change of file), and per-dataset val
    batches for the breakdown by source. Yields (inputs, targets) batches.
    """
    def __init__(
        self,
        files: List[Any],
        tokenizer: Any,
        args: TrainingArgs,
        context_length: int,
        prefetch_size: int = 64,
    ):
        super().__init__()
        self.files = [Path(f) for f in files]
        self.tokenizer = tokenizer
        self.args = args
        self.batch_size = args.batch_size
        self.context_length = context_length
        self.train_ratio = args.train_ratio
        self.prefetch_size = prefetch_size
        self.tokens: List[np.ndarray] = [load_token_cache(f, tokenizer, label=normalize_file_key(f)) for f in self.files]
        self.dataset_names: List[str] = [normalize_file_key(f).split("/")[0] if "/" in normalize_file_key(f) else f.stem for f in self.files]
        self.total_tokens = int(sum(len(t) for t in self.tokens))
        if args.model_name:
            save_steps_cache(args, {normalize_file_key(f): int(len(t)) for f, t in zip(self.files, self.tokens)}, stage=STAGE_TRAIN)
        windows = [max(0, (len(t) - 1) // context_length) for t in self.tokens]
        for f, w in zip(self.files, windows):
            if w == 0:
                print(f"Skipping {f}: fewer than {context_length + 1} tokens.")
        self.n_train = [min(w, max(1, int(round(w * self.train_ratio)))) if w else 0 for w in windows]
        self.n_val = [w - n for w, n in zip(windows, self.n_train)]
        self.train_offsets = np.cumsum([0] + self.n_train)  # global train window id -> file (searchsorted)
        self.val_offsets = np.cumsum([0] + self.n_val)
        self.total_train, self.total_val = int(self.train_offsets[-1]), int(self.val_offsets[-1])
        self.repeats = dataset_repeats(args, self.files)
        self.steps_per_epoch = sum(int(n * r) for n, r in zip(self.n_train, self.repeats)) // self.batch_size
        self._start = (0, 0)  # (epoch, steps to skip) for the next iteration
        gen = torch.Generator().manual_seed(EVAL_BUFFER_SEED)
        n_eval = args.eval_iter * self.batch_size
        self.val_loader = self._batches(torch.randperm(self.total_val, generator=gen)[:n_eval].tolist(), val=True)
        self.train_probe_loader = self._batches(torch.randperm(self.total_train, generator=gen)[:n_eval].tolist(), val=False)
        self._dataset_val_loaders: Optional[Dict[str, List[Tuple[torch.Tensor, torch.Tensor]]]] = None

    def __len__(self) -> int:
        return self.steps_per_epoch

    def seek(self, epoch: int, step_in_epoch: int = 0) -> None:
        """Positions the next iteration: epoch seeds the permutation; step_in_epoch is the checkpoint's count of steps already done in it."""
        self._start = (epoch, step_in_epoch)

    def __iter__(self):
        return iter(PrefetchIterator(self._generate_batches, queue_size=self.prefetch_size))

    def dataset_val_loaders(self) -> Dict[str, List[Tuple[torch.Tensor, torch.Tensor]]]:
        """A few fixed val batches per source dataset (the folder a file sits in), for the per-dataset validation breakdown."""
        if self._dataset_val_loaders is None:
            gen = torch.Generator().manual_seed(EVAL_BUFFER_SEED + 1)
            self._dataset_val_loaders = {}
            for name in dict.fromkeys(self.dataset_names):
                ids = torch.cat([torch.arange(int(self.val_offsets[i]), int(self.val_offsets[i + 1])) for i, n in enumerate(self.dataset_names) if n == name])
                if len(ids):
                    self._dataset_val_loaders[name] = self._batches(ids[torch.randperm(len(ids), generator=gen)[:DATASET_EVAL_BATCHES * self.batch_size]].tolist(), val=True)
        return self._dataset_val_loaders

    def _window(self, gid: int, val: bool) -> np.ndarray:
        """The context_length + 1 tokens of a global train/val window id (val windows follow the train windows inside each file)."""
        offsets = self.val_offsets if val else self.train_offsets
        fi = int(np.searchsorted(offsets, gid, side="right") - 1)
        start = (gid - int(offsets[fi]) + (self.n_train[fi] if val else 0)) * self.context_length
        return self.tokens[fi][start:start + self.context_length + 1]

    def _batch(self, gids: List[int], val: bool = False) -> Tuple[torch.Tensor, torch.Tensor]:
        t = torch.from_numpy(np.stack([self._window(g, val) for g in gids]).astype(np.int64))
        return t[:, :-1].contiguous(), t[:, 1:].contiguous()  # contiguous: the loss flattens targets with .view (CPU batches are used as yielded)

    def _batches(self, gids: List[int], val: bool) -> List[Tuple[torch.Tensor, torch.Tensor]]:
        return [self._batch(gids[i:i + self.batch_size], val) for i in range(0, len(gids), self.batch_size)]

    def _generate_batches(self):
        epoch, skip = self._start
        self._start = (epoch + 1, 0)
        perm = epoch_pool(self.n_train, self.repeats, epoch)
        for step in range(skip, self.steps_per_epoch):
            yield self._batch(perm[step * self.batch_size:(step + 1) * self.batch_size].tolist())


def planned_streaming_steps(cached_steps: List[int], is_train: bool, train_ratio: float) -> int:
    """Planned batches per epoch: token-budget batches carry ~batch_size x max_length tokens, so the steps cache's token-based per-file plan (exact once a file has been seen) applies; the val split is the remaining fraction."""
    if is_train:
        return max(1, int(sum(cached_steps)))
    val_ratio = max(0.01, 1.0 - train_ratio)
    return max(1, int(sum(cached_steps) * (val_ratio / max(0.01, train_ratio))))


def estimate_unseen_file_steps(ds: Any, parse: Callable[[Path], List[Any]], encode: Callable[[Any], Optional[Any]], padded_length: Callable[[Any], int]) -> None:
    """
    First-pass plan for files without a steps-cache entry (the engines fix their LR horizon from len() at start): tokenizes a strided
    sample of items for the padded tokens per item, scales by the file's item count and the packing fill, and plans steps from that.
    """
    for i, (known, file_path) in enumerate(zip(ds.known_steps, ds.files)):
        if known is not None:
            continue
        items = parse(file_path)
        sample = items[::max(1, len(items) // STEP_ESTIMATE_SAMPLE)][:STEP_ESTIMATE_SAMPLE]
        encoded = [x for e in map(encode, sample) if e is not None for x in (e if isinstance(e, list) else [e])]
        tokens_per_item = sum(padded_length(e) for e in encoded) / len(sample) if sample else 0  # dropped items count as 0 tokens
        ds.cached_tokens[i] = int(tokens_per_item * len(items) / PACKING_FILL)
        ds.cached_steps[i] = calculate_file_steps(ds.cached_tokens[i], ds.batch_size, ds.max_length or 1024, ds.train_ratio)


def record_file_steps(ds: Any, file_idx: int, file_steps: int, padded_train_tokens: int, stage: str) -> None:
    """Exact plan for a file after streaming it once: padded tokens (file-level, the quantity the token budget divides) go to the steps cache; unseen files keep their estimates."""
    file_tokens = int(padded_train_tokens / ds.train_ratio) if ds.train_ratio > 0 else padded_train_tokens
    ds.known_steps[file_idx] = ds.cached_steps[file_idx] = file_steps
    ds.known_tokens[file_idx] = ds.cached_tokens[file_idx] = file_tokens
    ds.exact_steps[file_idx] = True
    if ds.args.model_name:
        key = normalize_file_key(ds.files[file_idx])
        save_steps_cache(ds.args, {key: file_tokens}, stage=stage, file_steps={key: file_steps}, plan_key=steps_plan_key(ds.args, ds.max_length))


def record_epoch_file_steps(ds: Any, steps: int, file_tokens: List[int], stage: str) -> None:
    """After a globally shuffled epoch (batches mix files), splits the epoch's batch count across files in proportion to the padded tokens each contributed and records them (per single pass: a file repeated ds.repeats[fi] times per epoch is scaled back)."""
    planned = len(ds)
    total = sum(file_tokens)
    for fi, t in enumerate(file_tokens):
        if t:
            record_file_steps(ds, fi, max(1, round(steps * t / total / ds.repeats[fi])), int(t / ds.repeats[fi]), stage)
    if steps != planned:
        print(f"[Training Plan] This pass streamed {steps:,} batches where the plan said {planned:,} ({100.0 * (steps - planned) / max(1, planned):+.1f}%); the steps cache now holds the exact count and every later plan uses it (a resumed run re-anchors its LR cosine on the new horizon instead of jumping).")


def plan_provenance(ds: Any) -> str:
    """How the step plan (len(), hence the LR horizon) was obtained: exact from the steps cache (a previous pass or --precompute_total_steps), or estimated for files never streamed."""
    unknown = sum(1 for k in ds.known_steps if k is None)
    approx = sum(1 for k, e in zip(ds.known_steps, ds.exact_steps) if k is not None and not e)
    if not unknown and not approx:
        return "exact (steps cache)"
    parts = [f"{approx} of {len(ds.files)} file(s) planned from cached token counts (approximate for token-budget batching)"] * bool(approx) + [f"{unknown} of {len(ds.files)} file(s) estimated from {STEP_ESTIMATE_SAMPLE:,}-item samples"] * bool(unknown)
    return "; ".join(parts) + "; exact after the first pass"


def precompute_streaming_steps(ds: Any, stage_label: str) -> None:
    """--precompute_total_steps for the streaming SFT/DPO datasets: streams the first epoch once without the GPU (the very same seeded order,
    tokenization, length packing and CPU collation as the real pass, nothing yielded) so record_epoch_file_steps stores the exact step and
    token counts before the first step and the LR horizon is exact from the start instead of an estimate corrected after the first pass.
    Costs one epoch of data-loading CPU work the first time a dataset (or batching configuration) is seen; skipped when the steps cache
    already holds exact counts for every file."""
    if all(ds.exact_steps):
        return
    t0 = time.time()
    prefetch, ds.prefetch_size = ds.prefetch_size, max(1, ds.prefetch_size)  # _generate_batches collates on the CPU when prefetching
    n = sum(1 for _ in ds._generate_batches())
    ds.prefetch_size = prefetch
    print(f"[Steps Precompute] {stage_label}: streamed the first epoch's {n:,} batches on the CPU in {time.time() - t0:.1f}s to record the exact step counts of {len(ds.files)} file(s) (steps_cache.json).")


def epoch_permutation(n: int, epoch: int) -> torch.Tensor:
    """Seeded global shuffle of n items for an epoch: every epoch sees a different order, and a resume replays the same one."""
    return torch.randperm(n, generator=torch.Generator().manual_seed(1_000_003 * epoch + 7))


def dataset_repeats(args: TrainingArgs, files: List[Path]) -> List[float]:
    """Per-file multiplier of the regular epochs from num_epochs_dataset_specific ({"wikipedia": 4} or [{"wikipedia": 4}, {"cosmopedia": 3}], keyed
    by the dataset folder a file sits in): under num_epochs 2 a folder listed with 4 repeats 2x in every epoch, one listed with 3 1.5x (all of
    it plus a different half each epoch), one listed with 0 is left out; unlisted folders 1x."""
    names = [normalize_file_key(f).split("/")[0] if "/" in normalize_file_key(f) else f.stem for f in files]
    spec = args.num_epochs_dataset_specific or {}
    spec = {k: v for d in (spec if isinstance(spec, list) else [spec]) for k, v in d.items()}
    for k in spec.keys() - set(names):
        print(f"[Data Warning] num_epochs_dataset_specific: no dataset folder '{k}' among {sorted(set(names))}, ignored.")
    if spec:
        print(f"[Data] Dataset-specific epochs over the {args.num_epochs}-epoch run: " + ", ".join(f"{k} x{v}" for k, v in spec.items()) + " (other datasets x{}).".format(args.num_epochs))
    return [float(spec.get(n, args.num_epochs)) / max(1, args.num_epochs) for n in names]


def epoch_pool(counts: List[int], repeats: List[float], epoch: int) -> torch.Tensor:
    """Shuffled global item ids of one epoch (file i owns the ids from counts[0] + ... + counts[i-1] on): file i contributes counts[i] * repeats[i]
    ids, the next stretch of a virtual stream of back-to-back seeded permutations of its ids, so over the run every item is seen
    num_epochs * repeats[i] times and an epoch never shows an item again before a full pass over the file. All repeats 1: the plain epoch_permutation."""
    if all(r == 1.0 for r in repeats):
        return epoch_permutation(sum(counts), epoch)
    pool, base = [], 0
    for fi, (n, r) in enumerate(zip(counts, repeats)):
        v = torch.arange(epoch * int(n * r), (epoch + 1) * int(n * r))  # positions in the file's virtual stream
        ids = torch.empty(len(v), dtype=torch.long)
        for k in torch.unique(v // max(n, 1)).tolist():  # the pass(es) the stretch spans, each its own permutation
            m = v // max(n, 1) == k
            ids[m] = torch.randperm(n, generator=torch.Generator().manual_seed(1_000_003 * k + 7919 * fi + 13))[v[m] % n]
        pool.append(ids + base)
        base += n
    pool = torch.cat(pool)
    return pool[epoch_permutation(len(pool), epoch)]


def pair_padded_length(item: Dict[str, Any], pad_to_multiple_of: int = 0) -> int:
    """Padded tokens a preference pair costs: both sequences are padded to the longer one plus the collate's trailing token, and both run."""
    return 2 * round_up(max(len(item["chosen"]), len(item["rejected"])) + 1, pad_to_multiple_of)


def instruction_padded_length(item: Tuple[List[int], List[bool]], pad_to_multiple_of: int = 0) -> int:
    """Padded tokens an instruction item costs: the collate pads to the longest item plus one and shifts, so the model sees its length."""
    return round_up(len(item[0]), pad_to_multiple_of)


def parse_preference_file(file_path: Path) -> List[Dict[str, Any]]:
    """Loads a JSON / JSONL preference file and keeps only entries with prompt, chosen and rejected fields."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content.startswith("["):
                entries = json.loads(content)
            else:
                entries = [json.loads(line) for line in content.splitlines() if line.strip()]
    except Exception as e:
        print(f"[Data Warning] Could not parse '{file_path.name}': {e}")
        return []

    valid_entries = []
    for e in entries:
        has_instr = bool(e.get("instruction") or e.get("prompt"))
        has_chosen = bool(e.get("chosen") or e.get("output"))
        has_rejected = bool(e.get("rejected"))
        if has_instr and has_chosen and has_rejected:
            valid_entries.append(e)
    return valid_entries


class StreamingPreferenceDataset(IterableDataset):
    """
    Streams multi-file preference datasets file-by-file without loading all files
    or tokenized pairs into memory simultaneously.
    Caches per-file step and token counts, tracking running averages for unvisited files.
    """
    def __init__(
        self,
        files: List[Path],
        tokenizer: Any,
        args: TrainingArgs,
        max_length: int = 1024,
        is_train: bool = True,
        device: Union[str, torch.device] = "cpu",
        prefetch_size: int = 64,
    ):
        super().__init__()
        self.files = [Path(f) for f in files]
        self.tokenizer = tokenizer
        self.args = args
        self.batch_size = args.batch_size
        self.max_length = max_length
        self.train_ratio = args.train_ratio
        self.is_train = is_train
        self.device = device
        self.prefetch_size = prefetch_size
        self.pad_to_multiple_of = args.pad_to_multiple_of
        self._padded_length = partial(pair_padded_length, pad_to_multiple_of=args.pad_to_multiple_of)

        self.known_steps, self.known_tokens, self.cached_steps, self.cached_tokens, self.exact_steps = init_streaming_dataset_cache(
            files=self.files,
            args=args,
            context_length=max_length,
            stage=STAGE_OPTIMIZE,
        )
        self._stratified_batches: Optional[List[Any]] = None
        self.epoch = 0
        self.repeats = dataset_repeats(args, self.files) if is_train else [1.0] * len(self.files)
        if not self.is_train:
            self._stratified_batches = self._build_stratified_validation_buffer()
        else:
            estimate_unseen_file_steps(self, parse_preference_file, self._encode_pair, self._padded_length)

    def seek(self, epoch: int) -> None:
        """Selects the epoch whose seeded global shuffle the next iteration streams."""
        self.epoch = epoch

    def _build_stratified_validation_buffer(self) -> List[Any]:
        per_file_items: List[List[Dict[str, Any]]] = []
        for file_path in self.files:
            valid_entries = parse_preference_file(file_path)
            if not valid_entries:
                continue
            split_idx = max(1, int(len(valid_entries) * self.train_ratio))
            val_items = valid_entries[split_idx:] if split_idx < len(valid_entries) else valid_entries[-1:]
            per_file_items.append(val_items)

        if not per_file_items:
            return []

        max_samples_per_file = 32
        interleaved_entries: List[Dict[str, Any]] = []
        for i in range(max_samples_per_file):
            for file_list in per_file_items:
                if i < len(file_list):
                    interleaved_entries.append(file_list[i])

        encoded_items: List[Dict[str, Any]] = []
        for entry in interleaved_entries:
            encoded = self._encode_pair(entry)
            if encoded is not None:
                encoded_items.append(encoded)

        collate_fn = partial(
            custom_dpo_collate_fn,
            pad_token_id=self.tokenizer.pad_id,
            allowed_max_length=self.max_length,
            mask_prompt_tokens=True,
            device="cpu",
            pad_to_multiple_of=self.pad_to_multiple_of,
        )

        batches = []
        for i in range(0, len(encoded_items), self.batch_size):
            chunk = encoded_items[i:i + self.batch_size]
            if chunk:
                batches.append(collate_fn(chunk))

        print(f"[Validation Buffer] Built fixed stratified DPO validation buffer: {len(batches)} batches across {len(per_file_items)} file(s).")
        return batches

    def __len__(self) -> int:
        if not self.is_train and self._stratified_batches is not None:
            return len(self._stratified_batches)
        return planned_streaming_steps([s * r for s, r in zip(self.cached_steps, self.repeats)], self.is_train, self.train_ratio)

    def _encode_pair(self, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Tokenizes a preference entry into prompt/chosen/rejected ids (None when a sequence exceeds max_length)."""
        prompt_text = format_input(entry)
        is_chat = "<|assistant|>" in prompt_text or "<|im_start|>" in prompt_text
        chosen_text = entry.get("chosen") or entry.get("output") or ""
        rejected_text = entry.get("rejected") or ""

        if not is_chat:
            chosen_full = f"{prompt_text}\n\n### Response:\n{chosen_text}"
            rejected_full = f"{prompt_text}\n\n### Response:\n{rejected_text}"
        else:
            end = "<|im_end|>" if "<|im_start|>" in prompt_text else ""  # ChatML responses end with <|im_end|>, as in SFT
            chosen_full = f"{prompt_text}{chosen_text}{end}"
            rejected_full = f"{prompt_text}{rejected_text}{end}"

        prompt_tokens = self.tokenizer.encode(prompt_text, allowed_special="all")
        chosen_tokens = self.tokenizer.encode(chosen_full, allowed_special="all")
        rejected_tokens = self.tokenizer.encode(rejected_full, allowed_special="all")

        if self.max_length is not None:
            budget = self.max_length - 1  # the collate keeps one slot
            if len(prompt_tokens) >= self.max_length:
                return None
            if getattr(self.args, "dpo_truncate_long_pairs", False):
                # Keep the pair, cut the answer: the prompt plus the head of the answer, with the end marker put back as the last token
                # when the answer had one. Pairs whose prompt leaves fewer than 32 answer tokens are still dropped.
                if len(prompt_tokens) + 32 > budget:
                    return None
                end_ids = self.tokenizer.encode(end, allowed_special="all") if is_chat and end else []
                def fit(t: List[int]) -> List[int]:
                    if len(t) <= budget:
                        return t
                    return t[:budget - len(end_ids)] + end_ids if end_ids and t[-len(end_ids):] == end_ids else t[:budget]
                chosen_tokens, rejected_tokens = fit(chosen_tokens), fit(rejected_tokens)
            elif len(chosen_tokens) > budget or len(rejected_tokens) > budget:
                return None

        encoded_item: Dict[str, Any] = {
            "prompt": prompt_tokens,
            "chosen": chosen_tokens,
            "rejected": rejected_tokens,
            "is_chat": is_chat
        }
        if "ref_chosen_logprob" in entry:
            encoded_item["ref_chosen_logprob"] = entry["ref_chosen_logprob"]
        if "ref_rejected_logprob" in entry:
            encoded_item["ref_rejected_logprob"] = entry["ref_rejected_logprob"]
        return encoded_item

    def __iter__(self):
        if not self.is_train and self._stratified_batches is not None:
            return iter(self._stratified_batches)
        if self.prefetch_size > 0:
            return iter(PrefetchIterator(self._generate_batches, queue_size=self.prefetch_size))
        return self._generate_batches()

    def _generate_batches(self):
        collate_device = "cpu" if self.prefetch_size > 0 else self.device
        collate_fn = partial(
            custom_dpo_collate_fn,
            pad_token_id=self.tokenizer.pad_id,
            allowed_max_length=self.max_length,
            mask_prompt_tokens=True,
            device=collate_device,
            pad_to_multiple_of=self.pad_to_multiple_of,
        )
        # Global shuffle: the train split of every file is pooled and permuted per epoch (preference files are small enough to hold as parsed entries)
        items: List[Tuple[Dict[str, Any], int]] = []
        counts: List[int] = []  # train items per file, in file order (the pool's id blocks)
        for file_idx, file_path in enumerate(self.files):
            valid_entries = parse_preference_file(file_path)
            items += [(e, file_idx) for e in valid_entries[:max(1, int(len(valid_entries) * self.train_ratio))]]
            counts.append(len(items) - sum(counts))

        steps = 0
        file_tokens = [0] * len(self.files)  # padded tokens the model processes, per source file
        window: List[Tuple[Dict[str, Any], int]] = []
        rng = random.Random(self.epoch)  # deterministic batch order: resume fast-forwards by replaying the same order

        def flush(window_items):
            nonlocal steps
            for batch_items in length_grouped_batches(window_items, self.batch_size, lambda it: self._padded_length(it[0]), rng, self.max_length):
                batch_dict = collate_fn([it[0] for it in batch_items])
                steps += 1
                for _, fi in batch_items:
                    file_tokens[fi] += 2 * batch_dict["chosen"].shape[1]  # chosen + rejected, both padded to the batch length
                yield batch_dict

        for i in epoch_pool(counts, self.repeats, self.epoch).tolist():
            encoded_item = self._encode_pair(items[i][0])
            if encoded_item is None:
                continue
            window.append((encoded_item, items[i][1]))
            if len(window) == LENGTH_GROUP_WINDOW * self.batch_size:
                yield from flush(window)
                window = []
        yield from flush(window)
        record_epoch_file_steps(self, steps, file_tokens, STAGE_OPTIMIZE)


def custom_collate_fn(
    batch: List[Tuple[List[int], List[bool]]],
    pad_token_id: int = 50256,
    ignore_index: int = -100,
    allowed_max_length: Optional[int] = None,
    device: Union[str, torch.device] = "cpu",
    return_unmasked: bool = False,
    pad_to_multiple_of: int = 0,
) -> Union[Tuple[torch.Tensor, torch.Tensor], Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
    """
    Pads variable-length sequences, shifts inputs/targets by 1, and masks prompt and padding
    tokens in targets with `ignore_index` (-100) so loss is strictly calculated on response tokens.
    When return_unmasked is True, also returns seq_targets where prompt tokens are kept for sequence loss evaluation.
    """
    batch_max_length = round_up(max(len(item[0]) for item in batch), pad_to_multiple_of) + 1  # the shifted inputs/targets are one shorter: they get the rounded length
    if allowed_max_length is not None:
        batch_max_length = min(batch_max_length, allowed_max_length + 1)

    inputs_lst, targets_lst, seq_targets_lst = [], [], []
    for full_tokens, loss_mask in batch:
        new_item = list(full_tokens)
        new_item.append(pad_token_id)

        # Truncate if necessary
        if len(new_item) > batch_max_length:
            new_item = new_item[:batch_max_length]

        # Pad sequence
        padded = new_item + [pad_token_id] * (batch_max_length - len(new_item))
        inputs = torch.tensor(padded[:-1], dtype=torch.long)
        targets = torch.tensor(padded[1:], dtype=torch.long)
        seq_targets = targets.clone() if return_unmasked else None

        # 1. Mask prompt tokens in target (loss only on the tokens loss_mask marks: the assistant response(s))
        n = min(len(loss_mask) - 1, len(targets))
        targets[:n][~torch.tensor(loss_mask[1:n + 1], dtype=torch.bool)] = ignore_index

        # 2. Mask trailing padding tokens except the first endoftext token
        mask = (targets == pad_token_id)
        indices = torch.nonzero(mask, as_tuple=False).squeeze()
        if indices.numel() > 1:
            targets[indices[1:]] = ignore_index

        if return_unmasked and seq_targets is not None:
            seq_mask = (seq_targets == pad_token_id)
            seq_indices = torch.nonzero(seq_mask, as_tuple=False).squeeze()
            if seq_indices.numel() > 1:
                seq_targets[seq_indices[1:]] = ignore_index
            seq_targets_lst.append(seq_targets)

        inputs_lst.append(inputs)
        targets_lst.append(targets)

    inputs_tensor = torch.stack(inputs_lst)
    targets_tensor = torch.stack(targets_lst)

    if device != "cpu":
        inputs_tensor = inputs_tensor.to(device, non_blocking=True)
        targets_tensor = targets_tensor.to(device, non_blocking=True)

    if return_unmasked:
        seq_targets_tensor = torch.stack(seq_targets_lst)
        if device != "cpu":
            seq_targets_tensor = seq_targets_tensor.to(device, non_blocking=True)
        return inputs_tensor, targets_tensor, seq_targets_tensor

    return inputs_tensor, targets_tensor


def parse_instruction_text_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parses clean text files prepared by gptdata.py formatted with:
      - <|user|> ... <|assistant|> ... <|endoftext|>
      - ### Instruction: ... ### Response: ... <|endoftext|>
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(f"[Data] Warning: Error reading {file_path.name}: {e}")
        return []

    return [parse_instruction_doc(d.strip()) for d in text.split("<|endoftext|>") if d.strip()]


def parse_instruction_doc(doc: str) -> Dict[str, Any]:
    """Parses one <|endoftext|>-delimited document (LLaMA, ChatML, Phi or Alpaca formatted) into a prompt/response entry."""
    if "<|start_header_id|>assistant<|end_header_id|>" in doc:
        parts = doc.rsplit("<|start_header_id|>assistant<|end_header_id|>", 1)
        prompt_text = parts[0].strip() + "\n<|start_header_id|>assistant<|end_header_id|>\n\n"
        resp_text = parts[1].lstrip("\n")
        if not resp_text.endswith("<|eot_id|>"):
            resp_text = resp_text.rstrip() + "<|eot_id|>"
        return {"prompt": prompt_text, "response": resp_text, "format": "llama"}
    elif "<|im_start|>assistant" in doc:
        parts = doc.rsplit("<|im_start|>assistant", 1)
        prompt_text = parts[0].strip() + "\n<|im_start|>assistant\n"
        resp_text = parts[1].lstrip("\n")
        if not resp_text.endswith("<|im_end|>"):
            resp_text = resp_text.rstrip() + "<|im_end|>"
        return {"prompt": prompt_text, "response": resp_text, "turns": CHATML_TURN_RE.findall(doc), "format": "chatml"}
    elif "<|assistant|>" in doc:
        parts = doc.rsplit("<|assistant|>", 1)
        prompt_text = parts[0].strip() + "\n<|assistant|>\n"
        resp_text = parts[1].lstrip("\n")
        return {"prompt": prompt_text, "response": resp_text, "format": "phi"}
    elif "### Response:" in doc:
        parts = doc.rsplit("### Response:", 1)
        prompt_text = parts[0].strip() + "\n### Response:\n"
        resp_text = parts[1].lstrip("\n")
        return {"prompt": prompt_text, "response": resp_text, "format": "alpaca"}
    # Fallback single prompt
    return {"prompt": doc, "response": "", "format": "raw"}


def format_input(entry: Dict[str, Any]) -> str:
    """
    Returns the prompt context (user/system turns) for instruction or chat generation.
    Supports native ChatML, Phi, and generic instruction entries.
    """
    if "prompt" in entry:
        return entry["prompt"]
    instruction = str(entry.get("instruction") or "").strip()
    input_ctx = str(entry.get("input") or entry.get("context") or "").strip()
    user_content = f"{instruction}\n\n{input_ctx}" if input_ctx else instruction
    return f"<|im_start|>user\n{user_content}<|im_end|>\n<|im_start|>assistant\n"


def format_full_entry(entry: Dict[str, Any]) -> Tuple[str, str]:
    """
    Formats prompt and response separately to allow precise prompt target masking.
    Returns: (prompt_text, response_text)
    """
    if "prompt" in entry and "response" in entry:
        return entry["prompt"], entry["response"]
    prompt = format_input(entry)
    output = str(entry.get("output") or entry.get("response") or "").strip()
    return prompt, output


class StreamingInstructionDataset(IterableDataset):
    """
    Streams multi-file instruction datasets file-by-file without loading all files
    or tokenized arrays into memory simultaneously.
    Caches per-file step and token counts, tracking running averages for unvisited files.
    """
    def __init__(
        self,
        files: List[Path],
        tokenizer: Any,
        args: TrainingArgs,
        max_length: Optional[int] = None,
        is_train: bool = True,
        device: Union[str, torch.device] = "cpu",
        prefetch_size: int = 64,
    ):
        super().__init__()
        self.files = [Path(f) for f in files]
        self.tokenizer = tokenizer
        self.args = args
        self.batch_size = args.batch_size
        self.max_length = max_length
        self.train_ratio = args.train_ratio
        self.is_train = is_train
        self.mask_prompt = args.mask_prompt
        self.device = device
        self.prefetch_size = prefetch_size
        self.pad_to_multiple_of = args.pad_to_multiple_of
        self._padded_length = partial(instruction_padded_length, pad_to_multiple_of=args.pad_to_multiple_of)

        self.known_steps, self.known_tokens, self.cached_steps, self.cached_tokens, self.exact_steps = init_streaming_dataset_cache(
            files=self.files,
            args=args,
            context_length=max_length or 1024,
            stage=STAGE_TUNE,
        )
        self._stratified_batches: Optional[List[Any]] = None
        self.epoch = 0
        self._spans: Optional[torch.Tensor] = None  # (file_idx, byte_start, byte_end) of every train doc across all files
        self._mmaps: List[mmap.mmap] = []
        self.repeats = dataset_repeats(args, self.files) if is_train else [1.0] * len(self.files)
        if not self.is_train:
            self._stratified_batches = self._build_stratified_validation_buffer()
        else:
            estimate_unseen_file_steps(self, parse_instruction_text_file, self._encode_item, self._padded_length)

    def seek(self, epoch: int) -> None:
        """Selects the epoch whose seeded global shuffle the next iteration streams."""
        self.epoch = epoch

    def _train_spans(self) -> torch.Tensor:
        """Indexes the train split of every file as (file_idx, byte_start, byte_end) document spans: the units the global shuffle permutes, read back through mmap so no file is held in memory."""
        spans: List[Tuple[int, int, int]] = []
        for fi, file_path in enumerate(self.files):
            with open(file_path, "rb") as f:
                self._mmaps.append(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ))
            docs, prev = [], 0
            for m in re.finditer(rb"<\|endoftext\|>", self._mmaps[fi]):
                docs.append((prev, m.start()))
                prev = m.end()
            docs.append((prev, len(self._mmaps[fi])))
            docs = [(s, e) for s, e in docs if self._mmaps[fi][s:e].strip()]  # same non-empty filter and split as parse_instruction_text_file
            spans += [(fi, s, e) for s, e in docs[:max(1, int(len(docs) * self.train_ratio))]]
        return torch.tensor(spans, dtype=torch.long)

    def _build_stratified_validation_buffer(self) -> List[Any]:
        per_file_items: List[List[Dict[str, Any]]] = []
        for file_path in self.files:
            file_items = parse_instruction_text_file(file_path)
            if not file_items:
                continue
            split_idx = max(1, int(len(file_items) * self.train_ratio))
            val_items = file_items[split_idx:] if split_idx < len(file_items) else file_items[-1:]
            per_file_items.append(val_items)

        if not per_file_items:
            return []

        # Interleave samples across files up to 32 items per file for balanced representation
        max_samples_per_file = 32
        interleaved_entries: List[Dict[str, Any]] = []
        for i in range(max_samples_per_file):
            for file_list in per_file_items:
                if i < len(file_list):
                    interleaved_entries.append(file_list[i])

        encoded_items: List[Tuple[List[int], List[bool]]] = []
        for entry in interleaved_entries:
            encoded_items.extend(self._encode_item(entry))

        collate = partial(
            custom_collate_fn,
            pad_token_id=self.tokenizer.pad_id,
            ignore_index=-100,
            allowed_max_length=self.max_length,
            device="cpu",
            return_unmasked=True,
            pad_to_multiple_of=self.pad_to_multiple_of,
        )

        batches = []
        for i in range(0, len(encoded_items), self.batch_size):
            chunk = encoded_items[i:i + self.batch_size]
            if chunk:
                batches.append(collate(chunk))

        print(f"[Validation Buffer] Built fixed stratified SFT validation buffer: {len(batches)} batches across {len(per_file_items)} file(s).")
        return batches

    def __len__(self) -> int:
        if not self.is_train and self._stratified_batches is not None:
            return len(self._stratified_batches)
        return planned_streaming_steps([s * r for s, r in zip(self.cached_steps, self.repeats)], self.is_train, self.train_ratio)

    def _encode_item(self, entry: Dict[str, Any]) -> List[Tuple[List[int], List[bool]]]:
        """
        Tokenizes an instruction entry into (full_tokens, loss_mask) items, loss_mask marking the graded (response) tokens. A ChatML entry
        yields one item per chunk of consecutive whole user/assistant pairs that fit max_length (as many pairs per chunk as fit, the system
        turn pinned to every chunk, loss on every assistant turn); a pair that does not fit even alone is dropped. Other entries yield one
        item; empty responses or items exceeding max_length yield none.
        """
        enc = lambda s: self.tokenizer.encode(s, allowed_special="all")
        budget = (self.max_length or 1 << 30) - 1  # one slot is kept for the end token the collate appends
        if "turns" not in entry:
            prompt_tokens, resp_tokens = map(enc, format_full_entry(entry))
            if not resp_tokens or len(prompt_tokens) + len(resp_tokens) > budget:
                return []
            return [(prompt_tokens + resp_tokens, [not self.mask_prompt] * len(prompt_tokens) + [True] * len(resp_tokens))]
        nl, pm = enc("\n"), not self.mask_prompt
        turns = [(role, enc(f"<|im_start|>{role}\n"), enc(f"{content}<|im_end|>")) for role, content in entry["turns"]]
        sys_t = turns[0][1] + turns[0][2] if turns and turns[0][0] == "system" else []
        pairs = [(u[1] + u[2] + nl + a[1] + a[2], [pm] * (len(u[1]) + len(u[2]) + len(nl) + len(a[1])) + [True] * len(a[2]))
                 for u, a in zip(turns, turns[1:]) if u[0] == "user" and a[0] == "assistant"]
        items: List[Tuple[List[int], List[bool]]] = []
        cur_t, cur_m = list(sys_t), [pm] * len(sys_t)
        for p_t, p_m in pairs:
            sep = nl if cur_t else []
            if len(cur_t) + len(sep) + len(p_t) > budget and len(cur_t) > len(sys_t):  # chunk full: emit it and start the next one
                items.append((cur_t, cur_m))
                cur_t, cur_m, sep = list(sys_t), [pm] * len(sys_t), nl if sys_t else []
            if len(cur_t) + len(sep) + len(p_t) > budget:  # the pair does not fit even alone
                continue
            cur_t, cur_m = cur_t + sep + p_t, cur_m + [pm] * len(sep) + p_m
        if len(cur_t) > len(sys_t):
            items.append((cur_t, cur_m))
        return items

    def __iter__(self):
        if not self.is_train and self._stratified_batches is not None:
            return iter(self._stratified_batches)
        if self.prefetch_size > 0:
            return iter(PrefetchIterator(self._generate_batches, queue_size=self.prefetch_size))
        return self._generate_batches()

    def _generate_batches(self):
        collate_device = "cpu" if self.prefetch_size > 0 else self.device
        collate = partial(
            custom_collate_fn,
            pad_token_id=self.tokenizer.pad_id,
            ignore_index=-100,
            allowed_max_length=self.max_length,
            device=collate_device,
            pad_to_multiple_of=self.pad_to_multiple_of,
        )
        if self._spans is None:
            self._spans = self._train_spans()

        steps = 0
        file_tokens = [0] * len(self.files)  # padded tokens the model processes, per source file
        window: List[Tuple[Tuple[List[int], List[bool]], int]] = []
        rng = random.Random(self.epoch)  # deterministic batch order: resume fast-forwards by replaying the same order

        def flush(window_items):
            nonlocal steps
            for batch_items in length_grouped_batches(window_items, self.batch_size, lambda it: self._padded_length(it[0]), rng, self.max_length or 1024):
                batch_tensor = collate([it[0] for it in batch_items])
                steps += 1
                for _, fi in batch_items:
                    file_tokens[fi] += batch_tensor[0].shape[1]
                yield batch_tensor

        # Global shuffle: documents from all files in a seeded per-epoch order, each read from its file by byte offset
        for i in epoch_pool(torch.bincount(self._spans[:, 0], minlength=len(self.files)).tolist(), self.repeats, self.epoch).tolist():
            fi, start, end = self._spans[i].tolist()
            doc = self._mmaps[fi][start:end].decode("utf-8", errors="replace").replace("\r\n", "\n").strip()  # text-mode reads translate CRLF; the mmap bytes do not
            for encoded_item in self._encode_item(parse_instruction_doc(doc)):
                window.append((encoded_item, fi))
                if len(window) == LENGTH_GROUP_WINDOW * self.batch_size:
                    yield from flush(window)
                    window = []
        yield from flush(window)
        record_epoch_file_steps(self, steps, file_tokens, STAGE_TUNE)

