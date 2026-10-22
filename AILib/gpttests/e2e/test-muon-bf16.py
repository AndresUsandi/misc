#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("muon-bf16", "--use_bf16_for_muon_momentum: bf16 Muon momentum buffers, VRAM saving, resume both ways, --use_muon guard")


def main():
    t.clean()
    t.train("[1/8] Running Pre-training with fp32 Muon momentum (reference for the VRAM comparison)...", "Training", "--resume", "false", "--use_bf16_for_muon_momentum", "false")

    t.delete("*.pth")
    t.train("[2/8] Running Pre-training again from scratch with bf16 Muon momentum...", "Training", "--resume", "false", "--use_bf16_for_muon_momentum", "true")
    t.memcheck("momentum", t.model_dir / f"{t.model}.chk.trn", "bfloat16")
    # the fp32 -> bf16 buffers of this 25M model are 96 -> 48 MiB; the optimizer-state figure of the [VRAM] report must drop by at least 0.04 GB
    t.memcheck("gpu0", t.log, 1, 2, "optim", 0.04)

    t.train("[3/8] Running Fine-Tuning with bf16 momentum (fresh, stops at step 5)...", "Fine-Tuning", "--resume", "false", "--use_bf16_for_muon_momentum", "true")
    t.memcheck("momentum", t.model_dir / f"{t.model}.chk.sft", "bfloat16")

    t.train("[4/8] Running Fine-Tuning again, resumed with the flag on (buffers load as fp32 and are cast back to bf16)...", "Fine-Tuning", "--resume", "true", "--use_bf16_for_muon_momentum", "true")
    t.memcheck("momentum", t.model_dir / f"{t.model}.chk.sft", "bfloat16")

    t.train("[5/8] Running Fine-Tuning again, resumed with the flag off (the flag is authoritative: bf16 buffers come back as fp32)...", "Fine-Tuning", "--resume", "true", "--use_bf16_for_muon_momentum", "false")
    t.memcheck("momentum", t.model_dir / f"{t.model}.chk.sft", "float32")

    t.train("[6/8] Running Optimizing with the flag set in the options file...", "Optimizing")
    t.memcheck("momentum", t.model_dir / f"{t.model}.chk.dpo", "bfloat16")

    t.train_rejected("[7/8] The flag without --use_muon must be rejected at parse time (exit code 2)...", "requires --use_muon true",
                     "--training_process", "Training", "--use_muon", "false", "--use_bf16_for_muon_momentum", "true")

    t.infer("[8/8] Running Inference...")
    t.assert_log("[Low-VRAM Optimization] Muon momentum buffers stored in bf16 (halves the Muon optimizer state; weights and Newton-Schulz stay fp32).",
                 "Optimizers Configured: 2 ([CustomMuon (2D matrices), Fused AdamW (1D/Norms)])",
                 "[Optimizer] Selected Hybrid CustomMuon (2D weights) + Fused AdamW (1D/Norms/Embeddings).",
                 "[Resume] Successfully loaded active TUNE checkpoint at Global Step 5", "[Resume] Successfully loaded active TUNE checkpoint at Global Step 10",
                 "Saved OPTIMIZE checkpoint")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
