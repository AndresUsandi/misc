# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Unified visualization and telemetry plotting for Pretraining, SFT, and DPO stages.

from pathlib import Path
import sys
from typing import List, Optional, Union

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import TrainingArgs
from gptio.pathutil import resolve_path, TARGET_PLOT, STAGE_TRAIN, STAGE_TUNE, STAGE_OPTIMIZE
from gptutils.consoleutils import print


def plot_training_losses(
    tokens_seen: List[int],
    train_losses: List[float],
    val_losses: List[float],
    args: TrainingArgs,
    epochs_seen: Optional[List[float]] = None,
) -> None:
    """Plots pretraining loss curves against epochs and tokens seen."""
    if not train_losses or not val_losses:
        return

    min_len = min(len(train_losses), len(val_losses))
    train_losses = train_losses[:min_len]
    val_losses = val_losses[:min_len]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    x_axis = epochs_seen[:min_len] if (epochs_seen and len(epochs_seen) >= min_len) else list(range(1, min_len + 1))
    x_label = "Epochs" if (epochs_seen and len(epochs_seen) >= min_len) else "Evaluation Steps"

    ax1.plot(x_axis, train_losses, label="Training Loss", color="royalblue", lw=2)
    ax1.plot(x_axis, val_losses, label="Validation Loss", linestyle="-.", color="coral", lw=2)
    ax1.set_xlabel(x_label)
    ax1.set_ylabel("Loss")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper right")

    if tokens_seen and len(tokens_seen) >= min_len:
        tokens_plot = tokens_seen[:min_len]
        ax2 = ax1.twiny()
        ax2.plot(tokens_plot, train_losses, alpha=0)
        ax2.set_xlabel("Tokens Seen")

    fig.tight_layout()
    plot_file = resolve_path(args.model_name, target=TARGET_PLOT, stage=STAGE_TRAIN, models_dir=args.models_base_dir)
    plot_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(plot_file))
    print(f"\n[Plot] Saved pretraining loss curves to '{plot_file}'.")
    plt.close()


def plot_tuning_losses(
    epochs_seen: List[float],
    tokens_seen: List[int],
    train_losses: List[float],
    val_losses: List[float],
    args: TrainingArgs,
) -> None:
    """Plots fine-tuning loss curves against epochs and tokens seen."""
    if not train_losses or not val_losses:
        return

    min_len = min(len(train_losses), len(val_losses))
    train_losses = train_losses[:min_len]
    val_losses = val_losses[:min_len]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    x_axis = epochs_seen[:min_len] if len(epochs_seen) >= min_len else list(range(1, min_len + 1))
    x_label = "Epochs" if len(epochs_seen) >= min_len else "Evaluation Steps"

    ax1.plot(x_axis, train_losses, label="Training Loss", color="royalblue", lw=2)
    ax1.plot(x_axis, val_losses, label="Validation Loss", linestyle="-.", color="coral", lw=2)
    ax1.set_xlabel(x_label)
    ax1.set_ylabel("Loss")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper right")

    if tokens_seen and len(tokens_seen) >= min_len:
        tokens_plot = tokens_seen[:min_len]
        ax2 = ax1.twiny()
        ax2.plot(tokens_plot, train_losses, alpha=0)
        ax2.set_xlabel("Tokens Seen")

    fig.tight_layout()
    plot_file = resolve_path(args.model_name, target=TARGET_PLOT, stage=STAGE_TUNE, models_dir=args.models_base_dir)
    plot_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(plot_file))
    print(f"\n[Plot] Saved fine-tuning loss curves to '{plot_file}'.")
    plt.close()


def plot_dpo_losses_and_margins(
    epochs_seen: List[float],
    tokens_seen: List[int],
    train_losses: List[float],
    val_losses: List[float],
    train_margins: List[float],
    val_margins: List[float],
    args: TrainingArgs,
) -> None:
    """Plots DPO loss curves and reward margin progressions side-by-side."""
    if not train_losses or not val_losses:
        return

    plot_file = resolve_path(args.model_name, target=TARGET_PLOT, stage=STAGE_OPTIMIZE, models_dir=args.models_base_dir)

    min_len = min(len(train_losses), len(val_losses), len(train_margins), len(val_margins))
    train_losses = train_losses[:min_len]
    val_losses = val_losses[:min_len]
    train_margins = train_margins[:min_len]
    val_margins = val_margins[:min_len]

    if len(epochs_seen) != min_len:
        epochs_seen = [i / max(1, min_len - 1) if min_len > 1 else 1.0 for i in range(min_len)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Panel 1: DPO Loss Progression
    ax1.plot(epochs_seen, train_losses, label="Train DPO Loss", color="#1f77b4", linewidth=2)
    ax1.plot(epochs_seen, val_losses, linestyle="--", label="Val DPO Loss", color="#ff7f0e", linewidth=2)
    ax1.set_xlabel("Epochs")
    ax1.set_ylabel("DPO Loss")
    ax1.set_title("DPO Loss Curves")
    ax1.legend(loc="upper right")
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Panel 2: Reward Margins Progression
    ax2.plot(epochs_seen, train_margins, label="Train Reward Margin", color="#2ca02c", linewidth=2)
    ax2.plot(epochs_seen, val_margins, linestyle="--", label="Val Reward Margin", color="#d62728", linewidth=2)
    ax2.axhline(0.0, color="gray", linestyle=":", alpha=0.7)
    ax2.set_xlabel("Epochs")
    ax2.set_ylabel("Margin (Chosen - Rejected)")
    ax2.set_title("Reward Margins")
    ax2.legend(loc="lower right")
    ax2.grid(True, linestyle=":", alpha=0.6)

    fig.tight_layout()
    try:
        plot_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(plot_file))
        print(f"[Plot] Saved DPO telemetry curves to '{plot_file}'.")
    except Exception as e:
        print(f"[Plot Warning] Could not save plot: {e}")
    finally:
        plt.close()
