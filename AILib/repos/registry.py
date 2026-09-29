from typing import Any, Dict


MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------
    # GPT-2 Models
    # -------------------------------------------------------------
    "gpt2:124m": {
        "family": "gpt2",
        "canonical_name": "gpt2",
        "canonical_size": "124M",
        "repo_url": "https://huggingface.co/rasbt/gpt2-from-scratch-pytorch/resolve/main/gpt2-small-124M.pth",
        "config": {
            "arch_family": "gpt2",
            "vocab_size": 50257,
            "context_length": 1024,
            "emb_dim": 768,
            "n_heads": 12,
            "n_layers": 12,
            "pos_emb_type": "absolute",
            "norm_type": "layernorm",
            "ffn_type": "gelu",
            "drop_rate": 0.0,
            "qkv_bias": True,
        }
    },
    "gpt2:355m": {
        "family": "gpt2",
        "canonical_name": "gpt2",
        "canonical_size": "355M",
        "repo_url": "https://huggingface.co/rasbt/gpt2-from-scratch-pytorch/resolve/main/gpt2-medium-355M.pth",
        "config": {
            "arch_family": "gpt2",
            "vocab_size": 50257,
            "context_length": 1024,
            "emb_dim": 1024,
            "n_heads": 16,
            "n_layers": 24,
            "pos_emb_type": "absolute",
            "norm_type": "layernorm",
            "ffn_type": "gelu",
            "drop_rate": 0.0,
            "qkv_bias": True,
        }
    },
    "gpt2:774m": {
        "family": "gpt2",
        "canonical_name": "gpt2",
        "canonical_size": "774M",
        "repo_url": "https://huggingface.co/rasbt/gpt2-from-scratch-pytorch/resolve/main/gpt2-large-774M.pth",
        "config": {
            "arch_family": "gpt2",
            "vocab_size": 50257,
            "context_length": 1024,
            "emb_dim": 1280,
            "n_heads": 20,
            "n_layers": 36,
            "pos_emb_type": "absolute",
            "norm_type": "layernorm",
            "ffn_type": "gelu",
            "drop_rate": 0.0,
            "qkv_bias": True,
        }
    },
    "gpt2:1d5b": {
        "family": "gpt2",
        "canonical_name": "gpt2",
        "canonical_size": "1d5B",
        "repo_url": "https://huggingface.co/rasbt/gpt2-from-scratch-pytorch/resolve/main/gpt2-xl-1558M.pth",
        "config": {
            "arch_family": "gpt2",
            "vocab_size": 50257,
            "context_length": 1024,
            "emb_dim": 1600,
            "n_heads": 25,
            "n_layers": 48,
            "pos_emb_type": "absolute",
            "norm_type": "layernorm",
            "ffn_type": "gelu",
            "drop_rate": 0.0,
            "qkv_bias": True,
        }
    },

    # -------------------------------------------------------------
    # LLaMA-3 / 3.2 Models
    # -------------------------------------------------------------
    "llama3.2:1b": {
        "family": "llama3",
        "canonical_name": "llama3.2",
        "canonical_size": "1B",
        "repo_url": "https://huggingface.co/rasbt/llama-3.2-from-scratch/resolve/main/llama3.2-1B-instruct.pth",
        "tokenizer_url": "https://huggingface.co/rasbt/llama-3.2-from-scratch/resolve/main/tokenizer.model",
        "config": {
            "arch_family": "llama3",
            "vocab_size": 128256,
            "context_length": 131072,
            "emb_dim": 2048,
            "n_heads": 32,
            "n_layers": 16,
            "hidden_dim": 8192,
            "n_kv_groups": 8,
            "head_dim": 64,
            "pos_emb_type": "rope",
            "norm_type": "rmsnorm",
            "ffn_type": "swiglu",
            "rope_base": 500000.0,
            "rope_freq": {
                "factor": 32.0,
                "low_freq_factor": 1.0,
                "high_freq_factor": 4.0,
                "original_context_length": 8192
            },
            "drop_rate": 0.0,
            "qkv_bias": False,
        }
    },
    "llama3.2:3b": {
        "family": "llama3",
        "canonical_name": "llama3.2",
        "canonical_size": "3B",
        "repo_url": "https://huggingface.co/rasbt/llama-3.2-from-scratch/resolve/main/llama3.2-3B-instruct.pth",
        "tokenizer_url": "https://huggingface.co/rasbt/llama-3.2-from-scratch/resolve/main/tokenizer.model",
        "config": {
            "arch_family": "llama3",
            "vocab_size": 128256,
            "context_length": 131072,
            "emb_dim": 3072,
            "n_heads": 24,
            "n_layers": 28,
            "hidden_dim": 8192,
            "n_kv_groups": 8,
            "head_dim": 128,
            "pos_emb_type": "rope",
            "norm_type": "rmsnorm",
            "ffn_type": "swiglu",
            "rope_base": 500000.0,
            "rope_freq": {
                "factor": 32.0,
                "low_freq_factor": 1.0,
                "high_freq_factor": 4.0,
                "original_context_length": 8192
            },
            "drop_rate": 0.0,
            "qkv_bias": False,
        }
    },
    "llama3:8b": {
        "family": "llama3",
        "canonical_name": "llama3",
        "canonical_size": "8B",
        "repo_url": "https://huggingface.co/rasbt/llama-3-from-scratch/resolve/main/Llama-3-8B.pth",
        "config": {
            "arch_family": "llama3",
            "vocab_size": 128256,
            "context_length": 8192,
            "emb_dim": 4096,
            "n_heads": 32,
            "n_layers": 32,
            "hidden_dim": 14336,
            "n_kv_groups": 8,
            "head_dim": 128,
            "pos_emb_type": "rope",
            "norm_type": "rmsnorm",
            "ffn_type": "swiglu",
            "rope_base": 500000.0,
            "drop_rate": 0.0,
            "qkv_bias": False,
        }
    },

    # -------------------------------------------------------------
    # Qwen-3 / 2.5 Models
    # -------------------------------------------------------------
    "qwen3:0.6b": {
        "family": "qwen3",
        "canonical_name": "qwen3",
        "canonical_size": "0d6B",
        "repo_url": "https://huggingface.co/rasbt/qwen3-from-scratch/resolve/main/qwen3-0.6B.pth",
        "tokenizer_url": "https://huggingface.co/rasbt/qwen3-from-scratch/resolve/main/tokenizer.json",
        "config": {
            "arch_family": "qwen3",
            "vocab_size": 151936,
            "context_length": 40960,
            "emb_dim": 1024,
            "n_heads": 16,
            "n_layers": 28,
            "hidden_dim": 3072,
            "head_dim": 128,
            "qk_norm": True,
            "n_kv_groups": 8,
            "pos_emb_type": "rope",
            "norm_type": "rmsnorm",
            "ffn_type": "swiglu",
            "rope_base": 1000000.0,
            "drop_rate": 0.0,
            "qkv_bias": False,
            "tie_word_embeddings": True,
        }
    },
    "qwen3:1.7b": {
        "family": "qwen3",
        "canonical_name": "qwen3",
        "canonical_size": "1d7B",
        "repo_url": "https://huggingface.co/rasbt/qwen3-from-scratch/resolve/main/qwen3-1.7B.pth",
        "tokenizer_url": "https://huggingface.co/rasbt/qwen3-from-scratch/resolve/main/tokenizer.json",
        "config": {
            "arch_family": "qwen3",
            "vocab_size": 151936,
            "context_length": 40960,
            "emb_dim": 2048,
            "n_heads": 16,
            "n_layers": 28,
            "hidden_dim": 6144,
            "head_dim": 128,
            "qk_norm": True,
            "n_kv_groups": 8,
            "pos_emb_type": "rope",
            "norm_type": "rmsnorm",
            "ffn_type": "swiglu",
            "rope_base": 1000000.0,
            "drop_rate": 0.0,
            "qkv_bias": False,
        }
    },
    "qwen3:4b": {
        "family": "qwen3",
        "canonical_name": "qwen3",
        "canonical_size": "4B",
        "repo_url": "https://huggingface.co/rasbt/qwen3-from-scratch/resolve/main/qwen3-4B.pth",
        "tokenizer_url": "https://huggingface.co/rasbt/qwen3-from-scratch/resolve/main/tokenizer.json",
        "config": {
            "arch_family": "qwen3",
            "vocab_size": 151936,
            "context_length": 40960,
            "emb_dim": 2560,
            "n_heads": 32,
            "n_layers": 36,
            "hidden_dim": 9728,
            "head_dim": 128,
            "qk_norm": True,
            "n_kv_groups": 8,
            "pos_emb_type": "rope",
            "norm_type": "rmsnorm",
            "ffn_type": "swiglu",
            "rope_base": 1000000.0,
            "drop_rate": 0.0,
            "qkv_bias": False,
        }
    },

    # -------------------------------------------------------------
    # Qwen-3.5 / 2.5 Models
    # -------------------------------------------------------------
    "qwen3.5:0.6b": {
        "family": "qwen3.5",
        "canonical_name": "qwen3.5",
        "canonical_size": "0d6B",
        "repo_url": "https://huggingface.co/rasbt/qwen3-from-scratch/resolve/main/qwen3-0.6B.pth",
        "config": {
            "arch_family": "qwen3",
            "vocab_size": 151936,
            "context_length": 40960,
            "emb_dim": 1024,
            "n_heads": 16,
            "n_layers": 28,
            "hidden_dim": 3072,
            "head_dim": 128,
            "qk_norm": True,
            "n_kv_groups": 8,
            "pos_emb_type": "rope",
            "norm_type": "rmsnorm",
            "ffn_type": "swiglu",
            "rope_base": 1000000.0,
            "drop_rate": 0.0,
            "qkv_bias": True,
            "tie_word_embeddings": True,
        }
    },
    "qwen2.5:0.5b": {
        "family": "qwen2.5",
        "canonical_name": "qwen2.5",
        "canonical_size": "0d5B",
        "repo_url": "https://huggingface.co/rasbt/qwen2.5-from-scratch/resolve/main/qwen2.5-0.5B.pth",
        "config": {
            "arch_family": "qwen3",
            "vocab_size": 151936,
            "context_length": 32768,
            "emb_dim": 896,
            "n_heads": 14,
            "n_layers": 24,
            "hidden_dim": 4864,
            "head_dim": 64,
            "qk_norm": True,
            "n_kv_groups": 2,
            "pos_emb_type": "rope",
            "norm_type": "rmsnorm",
            "ffn_type": "swiglu",
            "rope_base": 1000000.0,
            "drop_rate": 0.0,
            "qkv_bias": True,
            "tie_word_embeddings": True,
        }
    },

    # -------------------------------------------------------------
    # Gemma-2 / Gemma-3 Models
    # -------------------------------------------------------------
    "gemma2:2b": {
        "family": "gemma",
        "canonical_name": "gemma2",
        "canonical_size": "2B",
        "repo_url": "https://huggingface.co/rasbt/gemma2-from-scratch/resolve/main/gemma-2-2b.pth",
        "config": {
            "arch_family": "gemma",
            "vocab_size": 256000,
            "context_length": 8192,
            "emb_dim": 2304,
            "n_heads": 8,
            "n_layers": 26,
            "hidden_dim": 9216,
            "head_dim": 256,
            "n_kv_groups": 4,
            "pos_emb_type": "rope",
            "norm_type": "gemma_rmsnorm",
            "ffn_type": "swiglu",
            "rope_base": 10000.0,
            "drop_rate": 0.0,
            "qkv_bias": False,
            "tie_word_embeddings": True,
        }
    },
    "gemma3:1b": {
        "family": "gemma",
        "canonical_name": "gemma3",
        "canonical_size": "1B",
        "repo_url": "https://huggingface.co/rasbt/gemma3-from-scratch/resolve/main/gemma-3-1b.pth",
        "config": {
            "arch_family": "gemma",
            "vocab_size": 256000,
            "context_length": 8192,
            "emb_dim": 1536,
            "n_heads": 6,
            "n_layers": 18,
            "hidden_dim": 6144,
            "head_dim": 256,
            "n_kv_groups": 3,
            "pos_emb_type": "rope",
            "norm_type": "gemma_rmsnorm",
            "ffn_type": "swiglu",
            "rope_base": 10000.0,
            "drop_rate": 0.0,
            "qkv_bias": False,
            "tie_word_embeddings": True,
        }
    },

    # -------------------------------------------------------------
    # OLMo-2 / OLMo-3 Models
    # -------------------------------------------------------------
    "olmo3:1b": {
        "family": "olmo",
        "canonical_name": "olmo3",
        "canonical_size": "1B",
        "repo_url": "https://huggingface.co/rasbt/olmo-from-scratch/resolve/main/olmo-1b.pth",
        "config": {
            "arch_family": "llama3",
            "vocab_size": 50304,
            "context_length": 2048,
            "emb_dim": 2048,
            "n_heads": 16,
            "n_layers": 16,
            "hidden_dim": 8192,
            "pos_emb_type": "rope",
            "norm_type": "rmsnorm",
            "ffn_type": "swiglu",
            "rope_base": 10000.0,
            "drop_rate": 0.0,
            "qkv_bias": False,
        }
    },

    # -------------------------------------------------------------
    # Cohere Aya / Tiny-Aya Models
    # -------------------------------------------------------------
    "tiny-aya:3b": {
        "family": "aya",
        "canonical_name": "tiny-aya",
        "canonical_size": "3B",
        "repo_url": "https://huggingface.co/rasbt/aya-from-scratch/resolve/main/tiny-aya-3b.pth",
        "config": {
            "arch_family": "llama3",
            "vocab_size": 256000,
            "context_length": 8192,
            "emb_dim": 3072,
            "n_heads": 24,
            "n_layers": 28,
            "hidden_dim": 8192,
            "n_kv_groups": 8,
            "pos_emb_type": "rope",
            "norm_type": "rmsnorm",
            "ffn_type": "swiglu",
            "rope_base": 10000.0,
            "drop_rate": 0.0,
            "qkv_bias": False,
        }
    },
}

# Synonyms and aliases
MODEL_ALIASES = {
    # GPT-2
    "gpt2": "gpt2:124m",
    "gpt2:small": "gpt2:124m",
    "gpt2:124": "gpt2:124m",
    "gpt2:medium": "gpt2:355m",
    "gpt2:355": "gpt2:355m",
    "gpt2:large": "gpt2:774m",
    "gpt2:774": "gpt2:774m",
    "gpt2:xl": "gpt2:1d5b",
    "gpt2:1.5b": "gpt2:1d5b",
    "gpt2:1558m": "gpt2:1d5b",

    # LLaMA
    "llama3:1b": "llama3.2:1b",
    "llama3.2": "llama3.2:1b",
    "llama3:3b": "llama3.2:3b",
    "llama3": "llama3:8b",
    "llama2": "llama3:8b",

    # Qwen
    "qwen3": "qwen3:0.6b",
    "qwen3:0.6": "qwen3:0.6b",
    "qwen3:1.7": "qwen3:1.7b",
    "qwen3:4": "qwen3:4b",
    "qwen3.5": "qwen3.5:0.6b",
    "qwen2.5": "qwen2.5:0.5b",

    # Gemma
    "gemma2": "gemma2:2b",
    "gemma:2b": "gemma2:2b",
    "gemma3": "gemma3:1b",

    # OLMo & Aya
    "olmo3": "olmo3:1b",
    "olmo": "olmo3:1b",
    "aya": "tiny-aya:3b",
    "tiny-aya": "tiny-aya:3b",
}

