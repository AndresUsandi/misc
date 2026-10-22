import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataset.cleanup import clean_standard_entry, clean_wikipedia_entry


REGISTRY_TRAIN_SCI: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # 5. Scientific Textbooks & Educational Foundations (Pretraining)
    # --------------------------------------------------------------------------
    "openstax_textbooks": {
        "category": "Science",
        "sub_category": "Science - Multiple",
        "hf_path": "crumb/openstax-text",
        "split": "train",
        "extracted_size": "~180 MB",
        "item_count": "45M tokens (estimate)",
        "description": "76 peer-reviewed OpenStax college textbooks covering foundational Physics, Chemistry, Biology, Astronomy, and Calculus.",
        "cleaner": clean_standard_entry,
    },
    "libretexts_science": {
        "category": "Science",
        "sub_category": "Science - Multiple",
        "hf_path": "princeton-nlp/TextbooksBySubject",
        "split": "train",
        "extracted_size": "~2.4 GB",
        "item_count": "600M tokens (estimate)",
        "description": "LibreTexts academic textbook collection across Geosciences, Oceanography, Materials Science, Physics, and Chemistry.",
        "cleaner": clean_standard_entry,
    },
    "cosmopedia_openstax": {
        "category": "Science",
        "sub_category": "Science - Multiple",
        "hf_path": "HuggingFaceTB/cosmopedia",
        "hf_name": "openstax",
        "split": "train",
        "extracted_size": "~0.55 GB",
        "item_count": "130M tokens (estimate)",
        "description": "Pedagogical synthetic textbooks grounded on OpenStax course curricula covering STEM subjects.",
        "cleaner": clean_standard_entry,
    },
    "cosmopedia_khan": {
        "category": "Science",
        "sub_category": "Science - Multiple",
        "hf_path": "HuggingFaceTB/cosmopedia",
        "hf_name": "khanacademy",
        "split": "train",
        "extracted_size": "~0.08 GB",
        "item_count": "20M tokens (estimate)",
        "description": "Beginner-friendly educational tutorials and step-by-step explanations structured from Khan Academy course outlines.",
        "cleaner": clean_standard_entry,
    },
    "cosmopedia_math": {
        "category": "Science",
        "sub_category": "Mathematics",
        "hf_path": "HuggingFaceTB/cosmopedia",
        "hf_name": "auto_math_text",
        "split": "train",
        "extracted_size": "~6.8 GB",
        "item_count": "1.7B tokens (estimate)",
        "description": "Pedagogical synthetic mathematics courseware and textbooks generated from math curricula.",
        "cleaner": clean_standard_entry,
    },
    "science_theory_textbooks": {
        "category": "Science",
        "sub_category": "Science - Multiple",
        "hf_path": "Nbardy/science-theory-textbooks",
        "split": "train",
        "extracted_size": "~320 MB",
        "item_count": "80M tokens (estimate)",
        "description": "Structured university lecture modules and scientific theory textbooks across physics, chemistry, and biology.",
        "cleaner": clean_standard_entry,
    },
    "proof_pile_2": {
        "category": "Science",
        "sub_category": "Mathematics",
        "hf_path": "EleutherAI/proof-pile-2",
        "hf_name": "open-web-math",
        "split": "train",
        "extracted_size": "~28 GB",
        "item_count": "14B tokens (estimate)",
        "description": "Massive high-quality open mathematical web and textbook corpus for mathematical reasoning.",
        "cleaner": clean_standard_entry,
    },
    "simple_wikipedia": {
        "category": "Science",
        "sub_category": "Science - Multiple",
        "hf_path": "wikipedia",
        "hf_name": "20220301.simple",
        "split": "train",
        "extracted_size": "~245 MB",
        "item_count": "60M tokens (estimate)",
        "description": "Simple English Wikipedia articles providing clear, foundational definitions of core science, earth, and math concepts without heavy jargon.",
        "cleaner": clean_wikipedia_entry,
    },
    "arxiv_physics": {
        "category": "Science",
        "sub_category": "Physics",
        "hf_path": "arxiv-community/arxiv_dataset",
        "split": "train",
        "extracted_size": "~15 GB",
        "item_count": "3.5B tokens (estimate)",
        "description": "arXiv preprints in physics, quantum physics, and high-energy physics for foundational scientific pretraining.",
        "cleaner": clean_standard_entry,
    },
}
