import os
import spacy
import re
import random
import csv
import warnings
from nltk.stem import SnowballStemmer
from transformers import pipeline, logging as hf_logging
import torch

# Silence informational sequential pipeline notices
hf_logging.set_verbosity_error()
warnings.filterwarnings("ignore", message=r".*You seem to be using the pipelines sequentially on GPU.*")

# ============================================================================
# Dials and Constants
# ============================================================================
DEFAULT_WORD_PROB = 0.80
DEFAULT_WORD_THRESHOLD = 0.04
SPACY_MODEL_NAME = "en_core_web_sm"
ROBERTA_MODEL_NAME = "distilroberta-base"
MASK_TOKEN = "<mask>"
PLACEHOLDER_TOKEN_REGEX = re.compile(r"\{[a-zA-Z_0-9]+\}")
DEFAULT_BATCH_SIZE = 64
MIN_WORD_LENGTH = 3

# Curated protected technical standards, acronyms, protocols, and architectural benchmarks
PROTECTED_TECHNICAL_ACRONYMS = {
    "soc2", "gdpr", "pci", "pci-dss", "hipaa", "iso27001", "rbac", "abac",
    "oauth2", "jwt", "saml", "oidc", "grpc", "graphql", "rest", "webrtc",
    "mqtt", "amqp", "http", "https", "tcp", "udp", "p99", "p95", "p50",
    "sla", "slo", "sli", "mvp", "rfc", "acid", "raft", "paxos", "bft",
    "fpga", "asic", "dsp", "adc", "dac", "gpio", "i2c", "spi", "uart",
    "can", "ble", "lora", "v1", "v2", "api", "ui", "ux", "sdk", "cli",
    "ram", "cpu", "gpu", "tpu", "aws", "gcp", "azure", "kubernetes",
    "docker", "kafka", "redis", "postgres", "postgresql", "mongodb", "mysql",
    "linux", "html", "css", "json", "yaml", "xml", "protobuf", "tls", "ssl"
}

class WordReplacerV2:
    """
    Phase 1: Neural Masked Language Model Word Replacer.
    Uses DistilRoBERTa fill-mask with balanced, surgical protection for technical acronyms,
    proper nouns, and units while allowing descriptive context words to be smoothly randomized.
    """
    def __init__(
        self,
        prob: float = DEFAULT_WORD_PROB,
        threshold: float = DEFAULT_WORD_THRESHOLD,
        batch_size: int = DEFAULT_BATCH_SIZE
    ):
        self.prob = prob
        self.threshold = threshold
        self.batch_size = batch_size
        
        print(f"Loading spaCy model ({SPACY_MODEL_NAME})...")
        try:
            self.nlp = spacy.load(SPACY_MODEL_NAME)
        except OSError:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", SPACY_MODEL_NAME], check=True)
            self.nlp = spacy.load(SPACY_MODEL_NAME)
            
        print("Loading NLTK stemmer...")
        self.stemmer = SnowballStemmer("english")
        
        print(f"Loading HuggingFace {ROBERTA_MODEL_NAME} pipeline...")
        device = 0 if torch.cuda.is_available() else -1
        self.unmasker = pipeline('fill-mask', model=ROBERTA_MODEL_NAME, device=device)
        print("Models loaded successfully.")
        
    def process_prompts_batch(self, prompts: list) -> list:
        """
        Processes a batch of prompts using parallel GPU tensor batching across all
        masked sentences to maximize GPU throughput and prevent sequential pipeline warnings.
        """
        if not prompts:
            return []

        prompt_tasks = []
        all_masked_sentences = []

        for p_idx, text in enumerate(prompts):
            placeholder_spans = [m.span() for m in PLACEHOLDER_TOKEN_REGEX.finditer(text)]
            doc = self.nlp(text)
            
            tasks_for_prompt = []
            for i, token in enumerate(doc):
                # Only replace content words (Nouns, Verbs, Adjectives, Adverbs)
                if token.is_stop or token.is_punct or token.is_space or token.pos_ not in ["NOUN", "VERB", "ADJ", "ADV"]:
                    continue
                
                # Protect tokens inside template placeholders (e.g. {domain_project_concept})
                is_inside_placeholder = any(start <= token.idx < end for start, end in placeholder_spans)
                if is_inside_placeholder or "{" in token.text or "}" in token.text:
                    continue
                
                # Protect short words, numbers, and units (e.g. 10ms, 256MB, 3)
                if len(token.text) < MIN_WORD_LENGTH or any(c.isdigit() for c in token.text):
                    continue
                
                word_lower = token.text.lower()
                # Protect recognized technical acronyms and standards
                if word_lower in PROTECTED_TECHNICAL_ACRONYMS:
                    continue
                    
                # Protect proper nouns (technology names, brand entities)
                if token.pos_ == "PROPN":
                    continue
                    
                if random.random() <= self.prob:
                    original_word = token.text
                    masked_sentence = text[:token.idx] + MASK_TOKEN + text[token.idx + len(original_word):]
                    tasks_for_prompt.append({
                        "char_start": token.idx,
                        "char_end": token.idx + len(original_word),
                        "original_word": original_word,
                        "word_pos": token.pos_,
                        "global_idx": len(all_masked_sentences)
                    })
                    all_masked_sentences.append(masked_sentence)

            prompt_tasks.append((text, tasks_for_prompt))

        # If no tokens were selected for replacement across the whole batch, return as-is
        if not all_masked_sentences:
            return list(prompts)

        # Execute batched GPU forward pass
        try:
            raw_predictions = self.unmasker(all_masked_sentences, batch_size=self.batch_size, top_k=20)
            if len(all_masked_sentences) == 1:
                predictions_batch = [raw_predictions]
            else:
                predictions_batch = raw_predictions
        except Exception:
            predictions_batch = [[] for _ in all_masked_sentences]

        randomized_prompts = []
        for text, tasks in prompt_tasks:
            # Sort tasks by char_start in reverse order to preserve string slicing offsets
            tasks.sort(key=lambda t: t["char_start"], reverse=True)
            new_text = text
            for task in tasks:
                preds = predictions_batch[task["global_idx"]]
                original_word = task["original_word"]
                word_lower = original_word.lower()
                word_stem = self.stemmer.stem(word_lower)
                target_pos = task["word_pos"]
                
                for pred in preds:
                    syn = pred['token_str'].strip().lower()
                    score = pred['score']
                    
                    if not syn.isalpha():
                        continue
                    
                    if score >= self.threshold and syn != word_lower and syn not in word_lower and word_lower not in syn:
                        if self.stemmer.stem(syn) == word_stem:
                            continue
                            
                        # Contextual POS verification
                        syn_token = self.nlp(syn)[0]
                        if syn_token.pos_ != target_pos and not (target_pos in ["ADJ", "VERB"] and syn_token.pos_ in ["ADJ", "VERB"]):
                            continue
                            
                        # Preserve original casing
                        if original_word.istitle():
                            syn = syn.title()
                        elif original_word.isupper():
                            syn = syn.upper()
                            
                        new_text = new_text[:task["char_start"]] + syn + new_text[task["char_end"]:]
                        break

            randomized_prompts.append(new_text)

        return randomized_prompts

    def process_prompt(self, text: str) -> str:
        """Processes a single prompt using the batched pipeline."""
        return self.process_prompts_batch([text])[0]

if __name__ == "__main__":
    replacer = WordReplacerV2(prob=0.80)
    sample = "We need a comprehensive feature design for a drag-and-drop workflow visualizer for pipeline step configuration.\n\nThis component will run in an edge environment with limited memory (256 MB) and intermittent network connectivity."
    print("\nOriginal:\n", sample)
    print("\nRandomized:\n", replacer.process_prompt(sample))
