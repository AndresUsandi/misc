import os
import re
import random
from prompt_data_generator_v1 import (
    TEMPLATED_CATEGORY_PARAGRAPHS,
    TYPED_TEMPLATE_SLOTS,
    CATEGORY_DOMAIN_PROJECTS,
    TEMPLATE_VALUES
)

# ============================================================================
# Constants & Configuration Defaults (Phase 3: Combinatorics & Concept Swapping)
# ============================================================================
DEFAULT_SIMILARITY_THRESHOLD = 0.35
DEFAULT_TOP_K = 8
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"

DEFAULT_MIN_OPTIONAL_PARAGRAPHS = 0
DEFAULT_MAX_OPTIONAL_PARAGRAPHS = 5
DEFAULT_OPTIONAL_PARAGRAPH_PROB = 1.0
DEFAULT_EXECUTIVE_LEAD_PROB = 0.20
DEFAULT_SECTION_SHUFFLE_PROB = 1.0
DEFAULT_TEMPLATE_VALUE_PROB = 1.0

DOUBLE_NEWLINE = "\n\n"
PLACEHOLDER_REGEX_PATTERN = r"\{([a-zA-Z_0-9]+)\}"
PLACEHOLDER_REGEX = re.compile(PLACEHOLDER_REGEX_PATTERN)

MANDATORY_CONTEXT_TYPES = ("background_project_info", "specific_project_details", "current_architecture")
MANDATORY_REQUEST_TYPES = ("the_request",)
MANDATORY_REQUIREMENTS_TYPES = ("problem_overview", "constraints_and_limitations", "success_criteria")

OPTIONAL_PARAGRAPH_TYPES = (
    "background_project_info",
    "current_architecture",
    "tech_stack",
    "target_audience",
    "caveats_and_considerations",
    "expected_output_format",
    "success_criteria",
    "assumptions",
    "alternative_approaches_rejected"
)

SECTION_CONTEXT = "context"
SECTION_MIDDLE = "middle"
SECTION_REQUEST = "request"

PARAGRAPH_TYPE_TO_SECTION = {
    "specific_project_details": SECTION_CONTEXT,
    "background_project_info": SECTION_CONTEXT,
    "current_architecture": SECTION_CONTEXT,
    "problem_overview": SECTION_MIDDLE,
    "constraints_and_limitations": SECTION_MIDDLE,
    "success_criteria": SECTION_MIDDLE,
    "tech_stack": SECTION_MIDDLE,
    "target_audience": SECTION_MIDDLE,
    "caveats_and_considerations": SECTION_MIDDLE,
    "assumptions": SECTION_MIDDLE,
    "alternative_approaches_rejected": SECTION_MIDDLE,
    "the_request": SECTION_REQUEST,
    "expected_output_format": SECTION_REQUEST,
}

_KNN_LOOKUP = None

def _build_knn_lookup(similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD, top_k: int = DEFAULT_TOP_K):
    """
    Precomputes dense embedding cosine similarity neighbors for each concept in TYPED_TEMPLATE_SLOTS
    and CATEGORY_DOMAIN_PROJECTS, preserving strict slot and category boundaries.
    """
    global _KNN_LOOKUP
    if _KNN_LOOKUP is not None:
        return _KNN_LOOKUP

    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
        
        model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
        lookup = {}

        # 1. Precompute k-NN for universal typed slots
        for slot_name, items in TYPED_TEMPLATE_SLOTS.items():
            if not items:
                continue

            if len(items) == 1:
                lookup[f"slot_{slot_name}"] = tuple(items)
                continue

            embeddings = model.encode(items, convert_to_tensor=False, normalize_embeddings=True)
            sim_matrix = np.dot(embeddings, embeddings.T)

            for i, text in enumerate(items):
                sims = sim_matrix[i]
                sorted_indices = np.argsort(-sims)
                
                neighbors = []
                for idx in sorted_indices:
                    if idx != i and sims[idx] >= similarity_threshold:
                        neighbors.append(items[idx])
                    if len(neighbors) >= top_k:
                        break

                lookup[f"slot_{slot_name}_{i}"] = tuple(neighbors) if neighbors else (items[i],)

        # 2. Precompute k-NN for category domain projects
        for cat_name, projects in CATEGORY_DOMAIN_PROJECTS.items():
            if not projects:
                continue

            if len(projects) == 1:
                lookup[f"cat_{cat_name}"] = tuple(projects)
                continue

            embeddings = model.encode(projects, convert_to_tensor=False, normalize_embeddings=True)
            sim_matrix = np.dot(embeddings, embeddings.T)

            for i, text in enumerate(projects):
                sims = sim_matrix[i]
                sorted_indices = np.argsort(-sims)
                
                neighbors = []
                for idx in sorted_indices:
                    if idx != i and sims[idx] >= similarity_threshold:
                        neighbors.append(projects[idx])
                    if len(neighbors) >= top_k:
                        break

                lookup[f"cat_{cat_name}_{i}"] = tuple(neighbors) if neighbors else (projects[i],)

        _KNN_LOOKUP = lookup
        return _KNN_LOOKUP
    except Exception:
        # Fallback to direct candidate pool
        lookup = {}
        for slot_name, items in TYPED_TEMPLATE_SLOTS.items():
            for i, text in enumerate(items):
                lookup[f"slot_{slot_name}_{i}"] = tuple(items)
        for cat_name, projects in CATEGORY_DOMAIN_PROJECTS.items():
            for i, text in enumerate(projects):
                lookup[f"cat_{cat_name}_{i}"] = tuple(projects)
        _KNN_LOOKUP = lookup
        return _KNN_LOOKUP

def randomize_template_values(
    text: str,
    category_name: str = "",
    template_value_prob: float = DEFAULT_TEMPLATE_VALUE_PROB,
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    top_k: int = DEFAULT_TOP_K
) -> str:
    """
    Replaces {slot_name} placeholders with semantically closest concepts
    (highest cosine similarity embedding neighbors) within that specific typed slot or category project pool.
    """
    if not text:
        return ""

    knn_map = _build_knn_lookup(similarity_threshold=similarity_threshold, top_k=top_k)
    category_projects = CATEGORY_DOMAIN_PROJECTS.get(category_name, [])

    def replace_match(match):
        slot_name = match.group(1)

        # Category Domain Project Slot
        if slot_name == "domain_project_concept":
            if random.random() <= template_value_prob and category_projects:
                candidates = knn_map.get(f"cat_{category_name}_0") or category_projects
                return random.choice(candidates)
            return category_projects[0] if category_projects else match.group(0)

        # Universal Typed Syntactic Slots
        if slot_name in TYPED_TEMPLATE_SLOTS:
            candidates_all = TYPED_TEMPLATE_SLOTS[slot_name]
            if random.random() <= template_value_prob and candidates_all:
                candidates = knn_map.get(f"slot_{slot_name}_0") or candidates_all
                return random.choice(candidates)
            return candidates_all[0] if candidates_all else match.group(0)

        return match.group(0)

    return PLACEHOLDER_REGEX.sub(replace_match, text)

class ParagraphAssemblerV2:
    """
    Assembles coherent combinations of templated paragraphs per category for V2 pipeline,
    enforcing core architectural requirements and configurable paragraph combinatorics and ordering knobs.
    """
    def __init__(
        self,
        min_optional_paragraphs: int = DEFAULT_MIN_OPTIONAL_PARAGRAPHS,
        max_optional_paragraphs: int = DEFAULT_MAX_OPTIONAL_PARAGRAPHS,
        optional_paragraph_prob: float = DEFAULT_OPTIONAL_PARAGRAPH_PROB,
        executive_lead_prob: float = DEFAULT_EXECUTIVE_LEAD_PROB,
        section_shuffle_prob: float = DEFAULT_SECTION_SHUFFLE_PROB,
        template_value_prob: float = DEFAULT_TEMPLATE_VALUE_PROB,
        templated_data=None
    ):
        self.min_optional_paragraphs = min_optional_paragraphs
        self.max_optional_paragraphs = max_optional_paragraphs
        self.optional_paragraph_prob = optional_paragraph_prob
        self.executive_lead_prob = executive_lead_prob
        self.section_shuffle_prob = section_shuffle_prob
        self.template_value_prob = template_value_prob

        self.templated_data = templated_data or TEMPLATED_CATEGORY_PARAGRAPHS
        self.categories = list(self.templated_data.keys())
        self.placeholder_regex = re.compile(PLACEHOLDER_REGEX_PATTERN)

    def sample_paragraphs_for_category(self, category_name: str) -> list:
        """
        Samples a valid subset of paragraphs for a given category:
        - 1 mandatory Specific Project Details paragraph (the domain anchor)
        - 1 mandatory Request paragraph
        - 1 mandatory Requirements/Problem paragraph
        - min_optional_paragraphs to max_optional_paragraphs optional paragraphs
        """
        cat_dict = self.templated_data.get(category_name, {})
        if not cat_dict:
            return []

        selected_types = []

        # 1. Primary Anchor: Specific Project Details
        if "specific_project_details" in cat_dict and cat_dict["specific_project_details"]:
            selected_types.append("specific_project_details")
        else:
            available_context = [t for t in MANDATORY_CONTEXT_TYPES if t in cat_dict and cat_dict[t]]
            if available_context:
                selected_types.append(random.choice(available_context))

        # 2. Select 1 Request Paragraph
        available_request = [t for t in MANDATORY_REQUEST_TYPES if t in cat_dict and cat_dict[t]]
        if available_request:
            selected_types.append(random.choice(available_request))

        # 3. Select 1 Requirements/Problem Paragraph
        available_reqs = [t for t in MANDATORY_REQUIREMENTS_TYPES if t in cat_dict and cat_dict[t]]
        if available_reqs:
            selected_types.append(random.choice(available_reqs))

        # 4. Sample Optional Paragraph Types using probability knob and min/max limits
        available_optional = [
            t for t in OPTIONAL_PARAGRAPH_TYPES
            if t in cat_dict and cat_dict[t] and t not in selected_types
        ]
        eligible_optional = [
            t for t in available_optional
            if random.random() <= self.optional_paragraph_prob
        ]
        
        effective_min = min(self.min_optional_paragraphs, len(eligible_optional))
        effective_max = min(self.max_optional_paragraphs, len(eligible_optional))
        if effective_max >= effective_min and len(eligible_optional) > 0:
            num_optional = random.randint(effective_min, effective_max)
            if num_optional > 0:
                selected_types.extend(random.sample(eligible_optional, num_optional))

        # 5. Order paragraphs coherently into logical sections
        context_paragraphs = []
        middle_paragraphs = []
        request_paragraphs = []

        for p_type in selected_types:
            options = cat_dict[p_type]
            p_text = random.choice(options)
            section = PARAGRAPH_TYPE_TO_SECTION.get(p_type, SECTION_MIDDLE)

            if section == SECTION_CONTEXT:
                context_paragraphs.append(p_text)
            elif section == SECTION_REQUEST:
                request_paragraphs.append(p_text)
            else:
                middle_paragraphs.append(p_text)

        # Shuffle paragraphs within their respective sections according to section_shuffle_prob
        if random.random() <= self.section_shuffle_prob:
            random.shuffle(context_paragraphs)
            random.shuffle(middle_paragraphs)
            random.shuffle(request_paragraphs)

        # Assemble final ordered sequence according to executive_lead_prob
        if random.random() < self.executive_lead_prob:
            ordered_paragraphs = request_paragraphs + context_paragraphs + middle_paragraphs
        else:
            ordered_paragraphs = context_paragraphs + middle_paragraphs + request_paragraphs

        return ordered_paragraphs

    def fill_template_placeholders(self, text: str, category_name: str = "") -> str:
        """
        Replaces template placeholders with semantically closest concept peers using Cosine k-NN Embedding Similarity.
        """
        return randomize_template_values(text, category_name, template_value_prob=self.template_value_prob)

    def render_original_prompt(self, templated_text: str, category_name: str = "") -> str:
        """
        Substitutes each placeholder with its baseline value from TYPED_TEMPLATE_SLOTS
        or CATEGORY_DOMAIN_PROJECTS in the original sequence of paragraphs without randomization.
        """
        category_projects = CATEGORY_DOMAIN_PROJECTS.get(category_name, [])

        def replace_exact(match):
            slot_name = match.group(1)
            if slot_name == "domain_project_concept":
                return category_projects[0] if category_projects else match.group(0)
            if slot_name in TYPED_TEMPLATE_SLOTS:
                return TYPED_TEMPLATE_SLOTS[slot_name][0]
            return match.group(0)

        return self.placeholder_regex.sub(replace_exact, templated_text)

    def generate_prompt(self, category_name: str = None) -> tuple:
        """
        Generates a full assembled prompt with its primary category.
        Returns (category_name, assembled_templated_text)
        """
        if not category_name or category_name not in self.categories:
            category_name = random.choice(self.categories)

        paragraphs = self.sample_paragraphs_for_category(category_name)
        assembled_templated = DOUBLE_NEWLINE.join(paragraphs)
        return category_name, assembled_templated

if __name__ == "__main__":
    assembler = ParagraphAssemblerV2()
    cat, templated = assembler.generate_prompt("Software Feature")
    print(f"--- Testing Merged Phase 3 Module ({cat}) ---")
    print("\nOriginal Rendered:\n", assembler.render_original_prompt(templated, cat))
    print("\nRandomized Filled:\n", assembler.fill_template_placeholders(templated, cat))

