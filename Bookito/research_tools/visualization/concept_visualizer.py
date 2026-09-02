import sys
import os
import time
import json
import random
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# Add parent directory to sys.path to import Bookito modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processors.concept_extractor import ConceptExtractor
from visualization.constants import (
    CLI_ARG_QUERIES_FLAG,
    QUERY_DELIMITER,
    OPENSEARCH_VISUALIZER_FILENAME,
    FINAL_SEARCH_VISUALIZER_FILENAME
)

# ==============================================================================
# TOP-OF-FILE CONFIGURATION & UI CONSTANTS
# ==============================================================================

WINDOW_TITLE = "Bookito Concept Extractor Visualizer"
WINDOW_GEOMETRY = "1280x800"
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 600

WEIGHT_LEFT_PANEL = 1
WEIGHT_RIGHT_PANEL = 1

# Layout Padding Constants
PANED_PADX = 5
PANED_PADY = 5
TITLE_PADX = 5
TITLE_PADY = 5
TEXT_PADX = 5
TEXT_PADY = 5
BUTTON_PADX = (5, 5)
BUTTON_PADY = (5, 5)
CONTROL_FRAME_PADDING = 5
STATUS_BAR_PADDING = (5, 2)

# Font Configuration Constants
FONT_FAMILY_TITLE = "Segoe UI"
FONT_FAMILY_BODY = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"
FONT_SIZE_HEADER = 11
FONT_SIZE_BODY = 10
FONT_SIZE_TEXT = 10
FONT_WEIGHT_BOLD = "bold"

# Color and Styling Constants
COLOR_WHITE = "#FFFFFF"
COLOR_BLACK = "#000000"
TTK_THEME_CLAM = "clam"

# Treeview Column Identifiers
COL_RANK = "rank"
COL_PHRASE = "phrase"
COL_SCORE = "score"
COL_OCCURRENCES = "occurrences"

# Treeview Column Headers
COL_HEADER_RANK = "#"
COL_HEADER_PHRASE = "Extracted Concept Phrase"
COL_HEADER_SCORE = "KeyBERT Score"
COL_HEADER_OCCURRENCES = "Occurrences"

# Treeview Column Widths
WIDTH_RANK = 50
MINWIDTH_RANK = 40
WIDTH_PHRASE = 380
MINWIDTH_PHRASE = 200
WIDTH_SCORE = 110
MINWIDTH_SCORE = 80
WIDTH_OCCURRENCES = 110
MINWIDTH_OCCURRENCES = 80

# UI Labels & Section Headers
HEADER_INPUT_TITLE = "Input Text for Concept Extraction"
HEADER_RESULTS_TITLE = "Extracted Concepts"
HEADER_EXCLUDED_TITLE = "Excluded Concepts"

COL_EXCLUDED_RANK = "ex_rank"
COL_EXCLUDED_PHRASE = "ex_phrase"
COL_EXCLUDED_SCORE = "ex_score"
COL_EXCLUDED_REASON = "ex_reason"

COL_HEADER_EXCLUDED_RANK = "#"
COL_HEADER_EXCLUDED_PHRASE = "Excluded Single-Word Concept"
COL_HEADER_EXCLUDED_SCORE = "Word Score (DF)"
COL_HEADER_EXCLUDED_REASON = "Reason"

WIDTH_EXCLUDED_RANK = 40
MINWIDTH_EXCLUDED_RANK = 30
WIDTH_EXCLUDED_PHRASE = 320
MINWIDTH_EXCLUDED_PHRASE = 180
WIDTH_EXCLUDED_SCORE = 110
MINWIDTH_EXCLUDED_SCORE = 80
WIDTH_EXCLUDED_REASON = 160
MINWIDTH_EXCLUDED_REASON = 100

WEIGHT_TOP_RESULTS_PANEL = 3
WEIGHT_BOTTOM_RESULTS_PANEL = 1

LABEL_EXTRACT_BUTTON = "Extract Concept"
LABEL_RANDOM_PROMPT_BUTTON = "Load Random Prompt"
LABEL_CLEAR_BUTTON = "Clear Text"
LABEL_SEARCH_CONCEPTS_BUTTON = "Concept Search"
LABEL_FINAL_SEARCH_BUTTON = "Final Concept Search"

LABEL_CHECKBOX_WORD_SCORING = "word scoring"
LABEL_CHECKBOX_MULTI_INSTANCE = "multi instance"
LABEL_CHECKBOX_SEMANTIC = "semantic"
LABEL_TOP_N = "Top N:"
DEFAULT_VISUALIZER_TOP_N = 10
ENTRY_TOP_N_WIDTH = 5
CHECKBOX_PADX = (10, 15)
CHECKBOX_FRAME_PADY = (5, 2)

VISUALIZER_MAX_DF_THRESHOLD = 0.90

# Test Prompts JSON Constants
TEST_PROMPTS_FILENAME = "test_prompts.json"
KEY_PROMPTS = "prompts"
KEY_PROMPT = "prompt"
KEY_ID = "id"
KEY_CATEGORY = "category"
FILE_ENCODING_UTF8 = "utf-8"

# Status Messages and Formats
STATUS_READY = "Ready. Type or paste text, or load a random prompt, and click 'Extract Concept' to process."
STATUS_EXTRACTING = "Extracting concepts using ConceptExtractor... Please wait."
STATUS_COMPLETED_FORMAT = "Extraction completed in {elapsed:.4f}s. Extracted {count} concept(s)."
STATUS_PROMPT_LOADED_FORMAT = "Loaded prompt '{id}' ({category}). Click 'Extract Concept' to process."
STATUS_FAILED = "Concept extraction failed."
STATUS_TEXT_EXTRACTION_ERROR_FORMAT = "Failed to initialize ConceptExtractor: {error}"

# Dialog Messages
MSG_TITLE_INPUT_NEEDED = "Input Needed"
MSG_TEXT_INPUT_NEEDED = "Please enter some text to extract concepts from."
MSG_TITLE_EXTRACTION_ERROR = "Extraction Error"
MSG_TEXT_EXTRACTION_ERROR_FORMAT = "Failed to extract concepts:\n{error}"
MSG_TITLE_PROMPTS_FILE_ERROR = "File Error"
MSG_TEXT_PROMPTS_FILE_ERROR_FORMAT = "Could not load test prompts from '{filename}':\n{error}"
MSG_TITLE_NO_CONCEPTS = "No Concepts"
MSG_TEXT_NO_CONCEPTS = "No extracted concepts found. Please extract concepts first."
MSG_TITLE_LAUNCH_ERROR = "Launch Error"
MSG_TEXT_LAUNCH_ERROR_FORMAT = "Failed to launch OpenSearch Visualizer:\n{error}"

# Formatter Templates & Delay Constants
SCORE_FORMAT = "{score:.4f}"
INITIAL_ASYNCHRONOUS_DELAY_MS = 0

# Tkinter Attributes & Event Identifiers
CURSOR_WATCH = "watch"
CURSOR_DEFAULT = ""
STATE_NORMAL = "normal"
STATE_DISABLED = "disabled"
TEXT_START_INDEX = "1.0"
TEXT_END_INDEX = "end"
TREE_INSERT_PARENT_ROOT = ""
TREE_INSERT_POSITION_END = "end"
TREE_SHOW_HEADINGS = "headings"
TREE_SELECTMODE_BROWSE = "browse"
TREE_ITEM_VALUES_KEY = "values"
TREE_COL_INDEX_PHRASE = 1
EVENT_KEY_CTRL_RETURN = "<Control-Return>"

# Environment variable keys for Tcl/Tk subprocess launching
ENV_KEY_TCL_LIBRARY = "TCL_LIBRARY"
ENV_KEY_TK_LIBRARY = "TK_LIBRARY"

def _build_tcl_env():
    """Builds an environment dict with TCL_LIBRARY and TK_LIBRARY paths set from the
    current process's tkinter installation. This ensures subprocesses can find Tcl/Tk
    even when launched from debuggers or non-standard Python interpreters."""
    env = os.environ.copy()
    try:
        tcl_dir = os.path.join(os.path.dirname(os.path.dirname(tk.__file__)), "tcl")
        tcl_version_dir = os.path.join(tcl_dir, f"tcl{tk.TclVersion}")
        tk_version_dir = os.path.join(tcl_dir, f"tk{tk.TkVersion}")
        if os.path.isdir(tcl_version_dir):
            env[ENV_KEY_TCL_LIBRARY] = tcl_version_dir
        if os.path.isdir(tk_version_dir):
            env[ENV_KEY_TK_LIBRARY] = tk_version_dir
    except Exception:
        pass
    return env

class ConceptVisualizerApp:
    """GUI application for interactive concept extraction from user-provided text or benchmark prompts."""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.concept_extractor = None

        self.use_word_scoring_var = tk.BooleanVar(value=True)
        self.use_multi_instance_var = tk.BooleanVar(value=True)
        self.use_semantic_boost_var = tk.BooleanVar(value=True)

        self.style = ttk.Style()
        try:
            self.style.theme_use(TTK_THEME_CLAM)
        except Exception:
            pass

        self._create_status_bar()
        self._create_layout()

        # Asynchronously initialize ConceptExtractor in background thread to keep GUI instant
        threading.Thread(target=self._async_init_extractor, daemon=True).start()

    def _async_init_extractor(self):
        try:
            self.concept_extractor = ConceptExtractor(
                use_word_scoring=self.use_word_scoring_var.get(),
                use_multi_instance_boost=self.use_multi_instance_var.get(),
                use_semantic_boost=self.use_semantic_boost_var.get(),
                max_df_threshold=VISUALIZER_MAX_DF_THRESHOLD
            )
            self.root.after(INITIAL_ASYNCHRONOUS_DELAY_MS, lambda: self.status_var.set(STATUS_READY))
        except Exception as e:
            err_msg = STATUS_TEXT_EXTRACTION_ERROR_FORMAT.format(error=e)
            self.root.after(INITIAL_ASYNCHRONOUS_DELAY_MS, lambda: self.status_var.set(err_msg))

    def _create_layout(self):
        # Top Options Bar: 3 horizontally sequential checkboxes
        self.top_options_frame = ttk.Frame(self.root, padding=CONTROL_FRAME_PADDING)
        self.top_options_frame.pack(side=tk.TOP, fill=tk.X, padx=PANED_PADX, pady=CHECKBOX_FRAME_PADY)

        self.chk_word_scoring = ttk.Checkbutton(
            self.top_options_frame,
            text=LABEL_CHECKBOX_WORD_SCORING,
            variable=self.use_word_scoring_var
        )
        self.chk_word_scoring.pack(side=tk.LEFT, padx=CHECKBOX_PADX)

        self.chk_multi_instance = ttk.Checkbutton(
            self.top_options_frame,
            text=LABEL_CHECKBOX_MULTI_INSTANCE,
            variable=self.use_multi_instance_var
        )
        self.chk_multi_instance.pack(side=tk.LEFT, padx=CHECKBOX_PADX)

        self.chk_semantic = ttk.Checkbutton(
            self.top_options_frame,
            text=LABEL_CHECKBOX_SEMANTIC,
            variable=self.use_semantic_boost_var
        )
        self.chk_semantic.pack(side=tk.LEFT, padx=CHECKBOX_PADX)

        top_n_label = ttk.Label(self.top_options_frame, text=LABEL_TOP_N, font=(FONT_FAMILY_BODY, FONT_SIZE_BODY))
        top_n_label.pack(side=tk.LEFT, padx=(15, 5))

        self.top_n_entry = ttk.Entry(self.top_options_frame, width=ENTRY_TOP_N_WIDTH, font=(FONT_FAMILY_MONO, FONT_SIZE_BODY))
        self.top_n_entry.insert(0, str(DEFAULT_VISUALIZER_TOP_N))
        self.top_n_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=PANED_PADX, pady=PANED_PADY)

        # ----------------------------------------------------
        # Left Panel: Multi-line Input Text Area & Control Buttons
        # ----------------------------------------------------
        self.left_frame = ttk.Frame(self.paned)
        self.paned.add(self.left_frame, weight=WEIGHT_LEFT_PANEL)

        input_title = ttk.Label(
            self.left_frame,
            text=HEADER_INPUT_TITLE,
            font=(FONT_FAMILY_TITLE, FONT_SIZE_HEADER, FONT_WEIGHT_BOLD)
        )
        input_title.pack(side=tk.TOP, anchor=tk.W, padx=TITLE_PADX, pady=TITLE_PADY)

        text_container = ttk.Frame(self.left_frame)
        text_container.pack(fill=tk.BOTH, expand=True, padx=TEXT_PADX, pady=TEXT_PADY)

        self.input_text_area = tk.Text(
            text_container,
            wrap=tk.WORD,
            font=(FONT_FAMILY_MONO, FONT_SIZE_TEXT),
            bg=COLOR_WHITE,
            fg=COLOR_BLACK,
            padx=TEXT_PADX,
            pady=TEXT_PADY
        )
        text_vscroll = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=self.input_text_area.yview)
        self.input_text_area.configure(yscrollcommand=text_vscroll.set)

        text_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind Ctrl+Enter to trigger extraction
        self.input_text_area.bind(EVENT_KEY_CTRL_RETURN, lambda event: self.on_extract_submit())

        # Control frame at bottom of left panel
        control_frame = ttk.Frame(self.left_frame, padding=CONTROL_FRAME_PADDING)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.extract_button = ttk.Button(
            control_frame,
            text=LABEL_EXTRACT_BUTTON,
            command=self.on_extract_submit
        )
        self.extract_button.pack(side=tk.LEFT, padx=BUTTON_PADX, pady=BUTTON_PADY)

        self.random_prompt_button = ttk.Button(
            control_frame,
            text=LABEL_RANDOM_PROMPT_BUTTON,
            command=self.on_load_random_prompt
        )
        self.random_prompt_button.pack(side=tk.LEFT, padx=BUTTON_PADX, pady=BUTTON_PADY)

        self.clear_button = ttk.Button(
            control_frame,
            text=LABEL_CLEAR_BUTTON,
            command=self.on_clear_text
        )
        self.clear_button.pack(side=tk.RIGHT, padx=BUTTON_PADX, pady=BUTTON_PADY)

        # ----------------------------------------------------
        # Right Panel: Results Paned Window (Top 75% Extracted, Bottom 25% Excluded)
        # ----------------------------------------------------
        self.right_frame = ttk.Frame(self.paned)
        self.paned.add(self.right_frame, weight=WEIGHT_RIGHT_PANEL)

        results_control_frame = ttk.Frame(self.right_frame, padding=CONTROL_FRAME_PADDING)
        results_control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.final_search_button = ttk.Button(
            results_control_frame,
            text=LABEL_FINAL_SEARCH_BUTTON,
            command=self.on_final_search_submit
        )
        self.final_search_button.pack(side=tk.RIGHT, padx=BUTTON_PADX, pady=BUTTON_PADY)

        self.search_concepts_button = ttk.Button(
            results_control_frame,
            text=LABEL_SEARCH_CONCEPTS_BUTTON,
            command=self.on_search_concepts
        )
        self.search_concepts_button.pack(side=tk.RIGHT, padx=BUTTON_PADX, pady=BUTTON_PADY)

        self.right_paned = ttk.PanedWindow(self.right_frame, orient=tk.VERTICAL)
        self.right_paned.pack(fill=tk.BOTH, expand=True, padx=TEXT_PADX, pady=TEXT_PADY)

        # Top section: 75% height for Extracted Concepts
        top_results_frame = ttk.Frame(self.right_paned)
        self.right_paned.add(top_results_frame, weight=WEIGHT_TOP_RESULTS_PANEL)

        results_title = ttk.Label(
            top_results_frame,
            text=HEADER_RESULTS_TITLE,
            font=(FONT_FAMILY_TITLE, FONT_SIZE_HEADER, FONT_WEIGHT_BOLD)
        )
        results_title.pack(side=tk.TOP, anchor=tk.W, padx=TITLE_PADX, pady=TITLE_PADY)

        tree_container = ttk.Frame(top_results_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=TEXT_PADX, pady=TEXT_PADY)

        cols = (COL_RANK, COL_PHRASE, COL_SCORE, COL_OCCURRENCES)
        self.concepts_tree = ttk.Treeview(
            tree_container,
            selectmode=TREE_SELECTMODE_BROWSE,
            show=TREE_SHOW_HEADINGS,
            columns=cols
        )

        self.concepts_tree.heading(COL_RANK, text=COL_HEADER_RANK, anchor=tk.CENTER)
        self.concepts_tree.heading(COL_PHRASE, text=COL_HEADER_PHRASE, anchor=tk.W)
        self.concepts_tree.heading(COL_SCORE, text=COL_HEADER_SCORE, anchor=tk.E)
        self.concepts_tree.heading(COL_OCCURRENCES, text=COL_HEADER_OCCURRENCES, anchor=tk.E)

        self.concepts_tree.column(COL_RANK, width=WIDTH_RANK, minwidth=MINWIDTH_RANK, anchor=tk.CENTER)
        self.concepts_tree.column(COL_PHRASE, width=WIDTH_PHRASE, minwidth=MINWIDTH_PHRASE, anchor=tk.W)
        self.concepts_tree.column(COL_SCORE, width=WIDTH_SCORE, minwidth=MINWIDTH_SCORE, anchor=tk.E)
        self.concepts_tree.column(COL_OCCURRENCES, width=WIDTH_OCCURRENCES, minwidth=MINWIDTH_OCCURRENCES, anchor=tk.E)

        tree_vscroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.concepts_tree.yview)
        tree_hscroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.concepts_tree.xview)
        self.concepts_tree.configure(yscrollcommand=tree_vscroll.set, xscrollcommand=tree_hscroll.set)

        tree_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.concepts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bottom section: 25% height for Excluded Concepts
        bottom_results_frame = ttk.Frame(self.right_paned)
        self.right_paned.add(bottom_results_frame, weight=WEIGHT_BOTTOM_RESULTS_PANEL)

        excluded_title = ttk.Label(
            bottom_results_frame,
            text=HEADER_EXCLUDED_TITLE,
            font=(FONT_FAMILY_TITLE, FONT_SIZE_HEADER, FONT_WEIGHT_BOLD)
        )
        excluded_title.pack(side=tk.TOP, anchor=tk.W, padx=TITLE_PADX, pady=TITLE_PADY)

        ex_tree_container = ttk.Frame(bottom_results_frame)
        ex_tree_container.pack(fill=tk.BOTH, expand=True, padx=TEXT_PADX, pady=TEXT_PADY)

        ex_cols = (COL_EXCLUDED_RANK, COL_EXCLUDED_PHRASE, COL_EXCLUDED_SCORE, COL_EXCLUDED_REASON)
        self.excluded_tree = ttk.Treeview(
            ex_tree_container,
            selectmode=TREE_SELECTMODE_BROWSE,
            show=TREE_SHOW_HEADINGS,
            columns=ex_cols
        )

        self.excluded_tree.heading(COL_EXCLUDED_RANK, text=COL_HEADER_EXCLUDED_RANK, anchor=tk.CENTER)
        self.excluded_tree.heading(COL_EXCLUDED_PHRASE, text=COL_HEADER_EXCLUDED_PHRASE, anchor=tk.W)
        self.excluded_tree.heading(COL_EXCLUDED_SCORE, text=COL_HEADER_EXCLUDED_SCORE, anchor=tk.E)
        self.excluded_tree.heading(COL_EXCLUDED_REASON, text=COL_HEADER_EXCLUDED_REASON, anchor=tk.W)

        self.excluded_tree.column(COL_EXCLUDED_RANK, width=WIDTH_EXCLUDED_RANK, minwidth=MINWIDTH_EXCLUDED_RANK, anchor=tk.CENTER)
        self.excluded_tree.column(COL_EXCLUDED_PHRASE, width=WIDTH_EXCLUDED_PHRASE, minwidth=MINWIDTH_EXCLUDED_PHRASE, anchor=tk.W)
        self.excluded_tree.column(COL_EXCLUDED_SCORE, width=WIDTH_EXCLUDED_SCORE, minwidth=MINWIDTH_EXCLUDED_SCORE, anchor=tk.E)
        self.excluded_tree.column(COL_EXCLUDED_REASON, width=WIDTH_EXCLUDED_REASON, minwidth=MINWIDTH_EXCLUDED_REASON, anchor=tk.W)

        ex_tree_vscroll = ttk.Scrollbar(ex_tree_container, orient=tk.VERTICAL, command=self.excluded_tree.yview)
        ex_tree_hscroll = ttk.Scrollbar(ex_tree_container, orient=tk.HORIZONTAL, command=self.excluded_tree.xview)
        self.excluded_tree.configure(yscrollcommand=ex_tree_vscroll.set, xscrollcommand=ex_tree_hscroll.set)

        ex_tree_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        ex_tree_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.excluded_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set(STATUS_READY)
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=STATUS_BAR_PADDING
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_load_random_prompt(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), TEST_PROMPTS_FILENAME)
        try:
            with open(json_path, "r", encoding=FILE_ENCODING_UTF8) as f:
                data = json.load(f)

            prompts = data.get(KEY_PROMPTS, [])
            if not prompts:
                return

            selected_item = random.choice(prompts)
            prompt_text = selected_item.get(KEY_PROMPT, "")
            prompt_id = selected_item.get(KEY_ID, "")
            prompt_category = selected_item.get(KEY_CATEGORY, "")

            self.input_text_area.delete(TEXT_START_INDEX, tk.END)
            self.input_text_area.insert(TEXT_START_INDEX, prompt_text)

            status_msg = STATUS_PROMPT_LOADED_FORMAT.format(id=prompt_id, category=prompt_category)
            self.status_var.set(status_msg)
        except Exception as e:
            messagebox.showerror(
                MSG_TITLE_PROMPTS_FILE_ERROR,
                MSG_TEXT_PROMPTS_FILE_ERROR_FORMAT.format(filename=TEST_PROMPTS_FILENAME, error=str(e))
            )

    def on_clear_text(self):
        self.input_text_area.delete(TEXT_START_INDEX, tk.END)
        for item in self.concepts_tree.get_children():
            self.concepts_tree.delete(item)
        for item in self.excluded_tree.get_children():
            self.excluded_tree.delete(item)
        self.status_var.set(STATUS_READY)

    def on_search_concepts(self):
        concept_items = self.concepts_tree.get_children()
        if not concept_items:
            messagebox.showwarning(MSG_TITLE_NO_CONCEPTS, MSG_TEXT_NO_CONCEPTS)
            return

        concept_phrases = []
        for item in concept_items:
            values = self.concepts_tree.item(item, TREE_ITEM_VALUES_KEY)
            if values and len(values) > TREE_COL_INDEX_PHRASE:
                phrase = str(values[TREE_COL_INDEX_PHRASE]).strip()
                if phrase:
                    concept_phrases.append(phrase)

        if not concept_phrases:
            messagebox.showwarning(MSG_TITLE_NO_CONCEPTS, MSG_TEXT_NO_CONCEPTS)
            return

        query_string = QUERY_DELIMITER.join(concept_phrases)
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OPENSEARCH_VISUALIZER_FILENAME)

        try:
            subprocess.Popen([sys.executable, script_path, CLI_ARG_QUERIES_FLAG, query_string], env=_build_tcl_env())
        except Exception as e:
            messagebox.showerror(
                MSG_TITLE_LAUNCH_ERROR,
                MSG_TEXT_LAUNCH_ERROR_FORMAT.format(error=str(e))
            )

    def on_final_search_submit(self):
        concept_items = self.concepts_tree.get_children()
        if not concept_items:
            messagebox.showwarning(MSG_TITLE_NO_CONCEPTS, MSG_TEXT_NO_CONCEPTS)
            return

        concept_phrases = []
        for item in concept_items:
            values = self.concepts_tree.item(item, TREE_ITEM_VALUES_KEY)
            if values and len(values) > TREE_COL_INDEX_PHRASE:
                phrase = str(values[TREE_COL_INDEX_PHRASE]).strip()
                if phrase:
                    concept_phrases.append(phrase)

        if not concept_phrases:
            messagebox.showwarning(MSG_TITLE_NO_CONCEPTS, MSG_TEXT_NO_CONCEPTS)
            return

        query_string = QUERY_DELIMITER.join(concept_phrases)
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FINAL_SEARCH_VISUALIZER_FILENAME)

        try:
            subprocess.Popen([sys.executable, script_path, CLI_ARG_QUERIES_FLAG, query_string], env=_build_tcl_env())
        except Exception as e:
            messagebox.showerror(
                MSG_TITLE_LAUNCH_ERROR,
                MSG_TEXT_LAUNCH_ERROR_FORMAT.format(error=str(e))
            )

    def on_extract_submit(self):
        text_content = self.input_text_area.get(TEXT_START_INDEX, tk.END).strip()
        if not text_content:
            messagebox.showwarning(MSG_TITLE_INPUT_NEEDED, MSG_TEXT_INPUT_NEEDED)
            return

        try:
            top_n_val = int(self.top_n_entry.get().strip())
        except ValueError:
            top_n_val = DEFAULT_VISUALIZER_TOP_N

        self.concept_extractor = ConceptExtractor(
            use_word_scoring=self.use_word_scoring_var.get(),
            use_multi_instance_boost=self.use_multi_instance_var.get(),
            use_semantic_boost=self.use_semantic_boost_var.get(),
            max_df_threshold=VISUALIZER_MAX_DF_THRESHOLD
        )

        start_time = time.time()
        self.status_var.set(STATUS_EXTRACTING)
        self.extract_button.config(state=STATE_DISABLED)
        self.root.config(cursor=CURSOR_WATCH)

        threading.Thread(
            target=self._async_extract_concepts,
            args=(text_content, top_n_val, start_time),
            daemon=True
        ).start()

    def _async_extract_concepts(self, text_content: str, top_n_val: int, start_time: float):
        try:
            kept_results, excluded_results = self.concept_extractor.extract_with_details(text_content, top_n=top_n_val)
            elapsed = time.time() - start_time
            self.root.after(
                INITIAL_ASYNCHRONOUS_DELAY_MS,
                lambda: self._display_concepts_results(kept_results, excluded_results, elapsed)
            )
        except Exception as e:
            self.root.after(
                INITIAL_ASYNCHRONOUS_DELAY_MS,
                lambda: self._on_extraction_error(str(e))
            )

    def _on_extraction_error(self, err_msg: str):
        self.root.config(cursor=CURSOR_DEFAULT)
        self.extract_button.config(state=STATE_NORMAL)
        self.status_var.set(STATUS_FAILED)
        messagebox.showerror(
            MSG_TITLE_EXTRACTION_ERROR,
            MSG_TEXT_EXTRACTION_ERROR_FORMAT.format(error=err_msg)
        )

    def _display_concepts_results(self, results: list, excluded_results: list, elapsed: float):
        self.root.config(cursor=CURSOR_DEFAULT)
        self.extract_button.config(state=STATE_NORMAL)

        for item in self.concepts_tree.get_children():
            self.concepts_tree.delete(item)
        for item in self.excluded_tree.get_children():
            self.excluded_tree.delete(item)

        for idx, concept_tuple in enumerate(results, start=1):
            phrase, score, occurrences = concept_tuple
            score_str = SCORE_FORMAT.format(score=score)
            self.concepts_tree.insert(
                TREE_INSERT_PARENT_ROOT,
                TREE_INSERT_POSITION_END,
                values=(idx, phrase, score_str, occurrences)
            )

        for idx, ex_tuple in enumerate(excluded_results, start=1):
            phrase, df_score, occurrences, reason = ex_tuple
            df_score_str = SCORE_FORMAT.format(score=df_score)
            self.excluded_tree.insert(
                TREE_INSERT_PARENT_ROOT,
                TREE_INSERT_POSITION_END,
                values=(idx, phrase, df_score_str, reason)
            )

        status_msg = STATUS_COMPLETED_FORMAT.format(elapsed=elapsed, count=len(results))
        self.status_var.set(status_msg)

def main():
    root = tk.Tk()
    app = ConceptVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
