import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataset.cleanup import (
    clean_story_entry, clean_standard_entry, clean_gutenberg_entry,
    clean_wikipedia_entry, clean_chatml_entry,
)


REGISTRY_TRAIN_CORE: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # 1. Formal Books & Literature (Pretraining Foundations)
    # --------------------------------------------------------------------------
    "writingprompts": {
        "category": "Formal Books & Literature",
        "sub_category": "",
        "hf_path": "euclaise/writingprompts",
        "split": "train",
        "extracted_size": "~823 MB",
        "item_count": "~210M tokens",
        "description": "FAIR WritingPrompts creative fiction stories & modern narrative novels across all genres.",
        "cleaner": clean_story_entry,
    },
    "bookcorpus": {
        "category": "Formal Books & Literature",
        "sub_category": "",
        "hf_path": "lucadiliello/bookcorpusopen",
        "split": "train",
        "extracted_size": "~6.25 GB",
        "item_count": "~1.63B tokens",
        "description": "BookCorpus open collection of ~74k diverse unpublished novels (used for original GPT/BERT pretraining).",
        "cleaner": clean_standard_entry,
    },
    "gutenberg": {
        "category": "Formal Books & Literature",
        "sub_category": "",
        "hf_path": "sedthh/gutenberg_english",
        "split": "train",
        "extracted_size": "~16.76 GB",
        "item_count": "~5.08B tokens",
        "description": "Project Gutenberg English public domain books (high-quality formal grammar & prose).",
        "cleaner": clean_gutenberg_entry,
    },
    "gutenberg_clean_en": {
        "category": "Formal Books & Literature",
        "sub_category": "",
        "hf_path": "nikolina-p/gutenberg_clean_en_splits",
        "split": "train",
        "extracted_size": "~12.19 GB",
        "item_count": "~3.10B tokens",
        "description": "Clean English Project Gutenberg books with train/val/test splits (38,026 books total).",
        "cleaner": clean_gutenberg_entry,
    },
    "gutenberg_manu": {
        "category": "Formal Books & Literature",
        "sub_category": "",
        "hf_path": "manu/project_gutenberg",
        "split": "en",
        "extracted_size": "~23.15 GB",
        "item_count": "~6.37B tokens",
        "description": "Extensive collection of 61k+ English Project Gutenberg books (by manu).",
        "cleaner": clean_gutenberg_entry,
    },
    "pg19": {
        "category": "Formal Books & Literature",
        "sub_category": "",
        "hf_path": "deepmind/pg19",
        "split": "train",
        "extracted_size": "~10.85 GB",
        "item_count": "~3.24B tokens",
        "description": "DeepMind PG-19 dataset of full-length English books published before 1919.",
        "cleaner": clean_gutenberg_entry,
    },

    # --------------------------------------------------------------------------
    # 2. World Knowledge & Encyclopedias (Factual Knowledge)
    # --------------------------------------------------------------------------
    "cosmopedia": {
        "category": "World Knowledge & Facts",
        "sub_category": "",
        "hf_path": "HuggingFaceTB/cosmopedia-100k",
        "split": "train",
        "extracted_size": "~361 MB",
        "item_count": "~73.5M tokens",
        "description": "Cosmopedia-100k synthetic textbooks, encyclopedic articles, and educational course material by Hugging Face.",
        "cleaner": clean_standard_entry,
    },
    "wikipedia": {
        "category": "World Knowledge & Facts",
        "sub_category": "",
        "hf_path": "wikimedia/wikipedia",
        "hf_name": "20231101.en",
        "split": "train",
        "extracted_size": "~18.61 GB",
        "item_count": "~4.36B tokens",
        "description": "Full English Wikipedia snapshot (Wikimedia 20231101.en, dense factual world knowledge).",
        "cleaner": clean_wikipedia_entry,
    },
    "wikipedia_simple": {
        "category": "World Knowledge & Facts",
        "sub_category": "",
        "hf_path": "wikimedia/wikipedia",
        "hf_name": "20231101.simple",
        "split": "train",
        "extracted_size": "~267 MB",
        "item_count": "~63.8M tokens",
        "description": "Simple English Wikipedia articles written in clean, accessible language.",
        "cleaner": clean_wikipedia_entry,
    },
    "wikitext": {
        "category": "World Knowledge & Facts",
        "sub_category": "",
        "hf_path": "wikitext",
        "hf_name": "wikitext-103-raw-v1",
        "split": "train",
        "extracted_size": "~532 MB",
        "item_count": "~127M tokens",
        "description": "WikiText-103 benchmark collection of verified Good and Featured English Wikipedia articles.",
        "cleaner": clean_standard_entry,
    },

    # --------------------------------------------------------------------------
    # 3. Conversational & Multi-Turn Dialogue (Chit-Chat & Real-Life Dialogues)
    # --------------------------------------------------------------------------
    "personachat": {
        "category": "Conversational & Multi-Turn Dialogue",
        "sub_category": "",
        "hf_path": "bavard/personachat_truecased",
        "split": "train",
        "extracted_size": "~73.3 MB",
        "item_count": "~27.8M tokens",
        "description": "True-cased PersonaChat multi-turn personality-driven casual conversations and chit-chat.",
        "cleaner": clean_chatml_entry,
    },
    "dailydialog": {
        "category": "Conversational & Multi-Turn Dialogue",
        "sub_category": "",
        "hf_path": "roskoN/dailydialog",
        "split": "train",
        "extracted_size": "~7.9 MB",
        "item_count": "~2.8M tokens",
        "description": "DailyDialog clean multi-turn human conversations covering daily life, emotions, and common topics.",
        "cleaner": clean_chatml_entry,
    },
    "dialogsum": {
        "category": "Conversational & Multi-Turn Dialogue",
        "sub_category": "",
        "hf_path": "knkarthick/dialogsum",
        "split": "train",
        "extracted_size": "~9.1 MB",
        "item_count": "~2.8M tokens",
        "description": "Multi-turn everyday human dialogues covering real-life situations (work, shopping, hobbies).",
        "cleaner": clean_chatml_entry,
    },

    # --------------------------------------------------------------------------
    # 4. Informal Web & Synthetic Stories (Pretraining Prose & Fiction)
    # --------------------------------------------------------------------------
    "openwebtext": {
        "category": "Informal Web & Synthetic Stories",
        "sub_category": "",
        "hf_path": "openwebtext",
        "split": "train",
        "extracted_size": "~37.43 GB",
        "item_count": "~9.09B tokens",
        "description": "Open clone of OpenAI WebText (Reddit-vetted links with 3+ karma; colloquial modern English).",
        "cleaner": clean_standard_entry,
    },
    "tinystories": {
        "category": "Informal Web & Synthetic Stories",
        "sub_category": "",
        "hf_path": "roneneldan/TinyStories",
        "split": "train",
        "extracted_size": "~1.82 GB",
        "item_count": "~495M tokens",
        "description": "Synthetic short stories with simple grammar and 3-4 year old vocabulary (great for testing).",
        "cleaner": clean_standard_entry,
    },
}
