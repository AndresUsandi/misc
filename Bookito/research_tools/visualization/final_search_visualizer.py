import sys
import os
import time
import threading
import concurrent.futures
import argparse
import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict
from typing import List, Dict, Any, Tuple, Set

# Add parent directory to sys.path to import Bookito modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processors.augmented_content_generator import (
    AugmentedContentGenerator,
    RESULT_KEY_TOTAL_AGGREGATED_SCORE,
    RESULT_KEY_CHUNKS,
    RESULT_KEY_MATCHED_CONCEPTS
)
from database.query_manager import (
    DEFAULT_TOP_K,
    RESULT_KEY_SCORE,
    RESULT_KEY_CHUNK_ID,
    RESULT_KEY_CHUNK_INDEX,
    RESULT_KEY_CHUNK_TEXT,
    RESULT_KEY_CHAPTER_ID,
    RESULT_KEY_CHAPTER_NUMBER,
    RESULT_KEY_CHAPTER_TITLE,
    RESULT_KEY_BOOK_ID,
    RESULT_KEY_BOOK_NAME,
    RESULT_KEY_FILE_LINK
)
from visualization.constants import (
    CLI_ARG_QUERIES_FLAG,
    CLI_ARG_QUERIES_SHORT_FLAG,
    CLI_ARG_QUERIES_HELP,
    CLI_ARG_MAX_CONCURRENT_FLAG,
    CLI_ARG_MAX_CONCURRENT_SHORT_FLAG,
    CLI_ARG_MAX_CONCURRENT_HELP,
    CLI_DESCRIPTION,
    QUERY_DELIMITER,
    DEFAULT_MAX_CONCURRENT_QUERIES,
    DEFAULT_CONTEXT_EXPANSION_CHUNKS,
    MATCH_TYPE_SYNTACTIC,
    MATCH_TYPE_SEMANTIC,
    FORMAT_MATCHED_CONCEPT
)

# ==============================================================================
# TOP-OF-FILE CONFIGURATION & UI CONSTANTS
# ==============================================================================

WINDOW_TITLE = "Bookito Final Concept Search Visualizer"
WINDOW_GEOMETRY = "1380x880"
WINDOW_MIN_WIDTH = 950
WINDOW_MIN_HEIGHT = 650
INITIAL_ASYNCHRONOUS_DELAY_MS = 0

SEARCH_PAGE_SIZE = 50
MAX_SNIPPET_LENGTH = 90
SCORE_ROUND_DECIMALS = 4
DEFAULT_INITIAL_PAGE = 1

WEIGHT_TOP_PANEL = 1
WEIGHT_BOTTOM_PANEL = 1
WEIGHT_CHUNKS_CONTAINER = 3
WEIGHT_CONCEPTS_CONTAINER = 2

# Layout Padding Constants
PANED_PADX = 5
PANED_PADY = 5
TITLE_PADX = 5
TITLE_PADY = 2
DETAIL_LABEL_PADX = 2
DETAIL_LABEL_PADY = 1
DETAIL_TEXT_PADX = 5
DETAIL_TEXT_PADY = 5
CONTROL_FRAME_PADDING = 5
LABEL_PADX = (5, 5)
ENTRY_PADX = 5
BUTTON_PADX = (5, 5)
STATUS_BAR_PADDING = (5, 2)

# Font Configuration Constants
FONT_FAMILY_TITLE = "Segoe UI"
FONT_FAMILY_BODY = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"
FONT_SIZE_HEADER = 11
FONT_SIZE_BODY = 10
FONT_SIZE_DETAIL_LABEL = 9
FONT_SIZE_DETAIL_TEXT = 9
FONT_WEIGHT_BOLD = "bold"

# Color and Styling Constants
COLOR_WHITE = "#FFFFFF"
COLOR_BLACK = "#000000"
TTK_THEME_CLAM = "clam"

# Master Table Identifiers & Headers
COL_MASTER_RANK = "rank"
COL_MASTER_SCORE = "total_score"
COL_MASTER_BOOK = "book"
COL_MASTER_CHAPTER = "chapter"
COL_MASTER_CONCEPTS_COUNT = "concepts_count"
COL_MASTER_CHUNKS_COUNT = "chunks_count"
COL_MASTER_CONCEPTS_SUMMARY = "concepts_summary"

COL_HEADER_MASTER_RANK = "#"
COL_HEADER_MASTER_SCORE = "Total Aggregated Score"
COL_HEADER_MASTER_BOOK = "Book Name"
COL_HEADER_MASTER_CHAPTER = "Chapter"
COL_HEADER_MASTER_CONCEPTS_COUNT = "Matched Concepts"
COL_HEADER_MASTER_CHUNKS_COUNT = "Total Chunks"
COL_HEADER_MASTER_CONCEPTS_SUMMARY = "Concepts Summary"

WIDTH_MASTER_RANK = 45
MINWIDTH_MASTER_RANK = 35
WIDTH_MASTER_SCORE = 140
MINWIDTH_MASTER_SCORE = 100
WIDTH_MASTER_BOOK = 240
MINWIDTH_MASTER_BOOK = 140
WIDTH_MASTER_CHAPTER = 200
MINWIDTH_MASTER_CHAPTER = 120
WIDTH_MASTER_CONCEPTS_COUNT = 120
MINWIDTH_MASTER_CONCEPTS_COUNT = 90
WIDTH_MASTER_CHUNKS_COUNT = 100
MINWIDTH_MASTER_CHUNKS_COUNT = 75
WIDTH_MASTER_CONCEPTS_SUMMARY = 350
MINWIDTH_MASTER_CONCEPTS_SUMMARY = 180

# Chunks Detail Table Identifiers & Headers
COL_CHUNK_RANK = "c_rank"
COL_CHUNK_INDEX = "c_index"
COL_CHUNK_SCORE = "c_score"
COL_CHUNK_SNIPPET = "c_snippet"

COL_HEADER_CHUNK_RANK = "#"
COL_HEADER_CHUNK_INDEX = "Chunk Index"
COL_HEADER_CHUNK_SCORE = "Chunk Score"
COL_HEADER_CHUNK_SNIPPET = "Text Snippet"

WIDTH_CHUNK_RANK = 40
MINWIDTH_CHUNK_RANK = 30
WIDTH_CHUNK_INDEX = 90
MINWIDTH_CHUNK_INDEX = 70
WIDTH_CHUNK_SCORE = 100
MINWIDTH_CHUNK_SCORE = 75
WIDTH_CHUNK_SNIPPET = 400
MINWIDTH_CHUNK_SNIPPET = 200

# Matched Concepts Detail Table Identifiers & Headers
COL_CONCEPT_RANK = "m_rank"
COL_CONCEPT_PHRASE = "m_phrase"
COL_CONCEPT_TYPE = "m_type"

COL_HEADER_CONCEPT_RANK = "#"
COL_HEADER_CONCEPT_PHRASE = "Concept Phrase"
COL_HEADER_CONCEPT_TYPE = "Match Type"

WIDTH_CONCEPT_RANK = 35
MINWIDTH_CONCEPT_RANK = 25
WIDTH_CONCEPT_PHRASE = 220
MINWIDTH_CONCEPT_PHRASE = 130
WIDTH_CONCEPT_TYPE = 110
MINWIDTH_CONCEPT_TYPE = 80

# UI Labels & Titles
HEADER_MASTER_TITLE = "Aggregated Concept Search Results"
HEADER_CHUNKS_TITLE = "Expanded Contiguous Chunks (+/- 5 Context)"
HEADER_CONCEPTS_TITLE = "Matched Concepts & Search Types"
LABEL_CONCEPTS_ENTRY = "Concepts (Semicolon Delimited):"
LABEL_CONCURRENCY = "Max Concurrent:"
LABEL_TOP_N = "Top N:"
ENTRY_TOP_N_WIDTH = 5
LABEL_SEARCH_BUTTON = "Run Final Search"
LABEL_TEXT_PREVIEW = "Full Chunk Text Preview:"

STATUS_READY = "Ready. Enter concepts (semicolon-delimited) and click 'Run Final Search'."
STATUS_SEARCHING = "Performing concurrent syntactic & semantic searches and context expansion... Please wait."
STATUS_COMPLETED_FORMAT = "Final search completed in {elapsed:.2f}s. Aggregated {count} result group(s)."
STATUS_FAILED = "Final concept search failed."
STATUS_ERROR_FORMAT = "Search error: {error}"

MSG_TITLE_INPUT_NEEDED = "Input Needed"
MSG_TEXT_INPUT_NEEDED = "Please enter at least one concept to search."

ENTRY_CONCURRENCY_WIDTH = 5
TREE_SELECTMODE_BROWSE = "browse"
TREE_ITEM_VALUES_KEY = "values"
TEXT_START_INDEX = "1.0"
STATE_DISABLED = "disabled"
STATE_NORMAL = "normal"
CURSOR_WATCH = "watch"
CURSOR_DEFAULT = ""

# ==============================================================================
# TKINTER GUI APPLICATION
# ==============================================================================

class FinalSearchVisualizerApp:
    """GUI application for multi-concept final search visualization."""
    def __init__(self, root: tk.Tk, initial_queries: List[str] = None, max_concurrent: int = DEFAULT_MAX_CONCURRENT_QUERIES):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.initial_queries = initial_queries or []
        self.max_concurrent = max_concurrent
        self.content_generator = None
        self.current_results = []
        self.selected_master_result = None

        self.style = ttk.Style()
        try:
            self.style.theme_use(TTK_THEME_CLAM)
        except Exception:
            pass

        self._create_top_control_bar()
        self._create_status_bar()
        self._create_layout()

        # Asynchronously initialize QueryManager in background thread
        threading.Thread(target=self._async_init_manager, daemon=True).start()

    def _async_init_manager(self):
        try:
            self.content_generator = AugmentedContentGenerator()
            self.root.after(INITIAL_ASYNCHRONOUS_DELAY_MS, lambda: self.status_var.set(STATUS_READY))
            if self.initial_queries:
                self.root.after(INITIAL_ASYNCHRONOUS_DELAY_MS, self.on_search_submit)
        except Exception as e:
            err_msg = STATUS_ERROR_FORMAT.format(error=e)
            self.root.after(INITIAL_ASYNCHRONOUS_DELAY_MS, lambda: self.status_var.set(err_msg))

    def _create_top_control_bar(self):
        self.control_frame = ttk.Frame(self.root, padding=CONTROL_FRAME_PADDING)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)

        concepts_label = ttk.Label(
            self.control_frame,
            text=LABEL_CONCEPTS_ENTRY,
            font=(FONT_FAMILY_BODY, FONT_SIZE_BODY, FONT_WEIGHT_BOLD)
        )
        concepts_label.pack(side=tk.LEFT, padx=LABEL_PADX)

        initial_text = QUERY_DELIMITER.join(self.initial_queries) if self.initial_queries else ""
        self.concepts_entry = ttk.Entry(self.control_frame, font=(FONT_FAMILY_MONO, FONT_SIZE_BODY))
        self.concepts_entry.insert(0, initial_text)
        self.concepts_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=ENTRY_PADX)

        conc_label = ttk.Label(self.control_frame, text=LABEL_CONCURRENCY, font=(FONT_FAMILY_BODY, FONT_SIZE_BODY))
        conc_label.pack(side=tk.LEFT, padx=LABEL_PADX)

        self.concurrency_entry = ttk.Entry(self.control_frame, width=ENTRY_CONCURRENCY_WIDTH, font=(FONT_FAMILY_MONO, FONT_SIZE_BODY))
        self.concurrency_entry.insert(0, str(self.max_concurrent))
        self.concurrency_entry.pack(side=tk.LEFT, padx=ENTRY_PADX)

        top_n_label = ttk.Label(self.control_frame, text=LABEL_TOP_N, font=(FONT_FAMILY_BODY, FONT_SIZE_BODY))
        top_n_label.pack(side=tk.LEFT, padx=LABEL_PADX)

        self.top_n_entry = ttk.Entry(self.control_frame, width=ENTRY_TOP_N_WIDTH, font=(FONT_FAMILY_MONO, FONT_SIZE_BODY))
        self.top_n_entry.insert(0, str(DEFAULT_TOP_K))
        self.top_n_entry.pack(side=tk.LEFT, padx=ENTRY_PADX)

        self.search_button = ttk.Button(
            self.control_frame,
            text=LABEL_SEARCH_BUTTON,
            command=self.on_search_submit
        )
        self.search_button.pack(side=tk.LEFT, padx=BUTTON_PADX)

    def _create_status_bar(self):
        self.status_var = tk.StringVar(value=STATUS_READY)
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            font=(FONT_FAMILY_BODY, FONT_SIZE_DETAIL_LABEL),
            relief=tk.SUNKEN,
            padding=STATUS_BAR_PADDING
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_layout(self):
        # Vertical PanedWindow: 50% Top Master Table, 50% Bottom Details
        self.vertical_paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.vertical_paned.pack(fill=tk.BOTH, expand=True, padx=PANED_PADX, pady=PANED_PADY)

        # ----------------------------------------------------------------------
        # Top Panel (50% Height): Master Results Table
        # ----------------------------------------------------------------------
        self.top_frame = ttk.Frame(self.vertical_paned)
        self.vertical_paned.add(self.top_frame, weight=WEIGHT_TOP_PANEL)

        master_title = ttk.Label(
            self.top_frame,
            text=HEADER_MASTER_TITLE,
            font=(FONT_FAMILY_TITLE, FONT_SIZE_HEADER, FONT_WEIGHT_BOLD)
        )
        master_title.pack(side=tk.TOP, anchor=tk.W, padx=TITLE_PADX, pady=TITLE_PADY)

        master_tree_container = ttk.Frame(self.top_frame)
        master_tree_container.pack(fill=tk.BOTH, expand=True, padx=PANED_PADX, pady=PANED_PADY)

        master_columns = (
            COL_MASTER_RANK,
            COL_MASTER_SCORE,
            COL_MASTER_BOOK,
            COL_MASTER_CHAPTER,
            COL_MASTER_CONCEPTS_COUNT,
            COL_MASTER_CHUNKS_COUNT,
            COL_MASTER_CONCEPTS_SUMMARY
        )

        self.master_tree = ttk.Treeview(
            master_tree_container,
            columns=master_columns,
            show="headings",
            selectmode=TREE_SELECTMODE_BROWSE
        )

        self.master_tree.heading(COL_MASTER_RANK, text=COL_HEADER_MASTER_RANK)
        self.master_tree.heading(COL_MASTER_SCORE, text=COL_HEADER_MASTER_SCORE)
        self.master_tree.heading(COL_MASTER_BOOK, text=COL_HEADER_MASTER_BOOK)
        self.master_tree.heading(COL_MASTER_CHAPTER, text=COL_HEADER_MASTER_CHAPTER)
        self.master_tree.heading(COL_MASTER_CONCEPTS_COUNT, text=COL_HEADER_MASTER_CONCEPTS_COUNT)
        self.master_tree.heading(COL_MASTER_CHUNKS_COUNT, text=COL_HEADER_MASTER_CHUNKS_COUNT)
        self.master_tree.heading(COL_MASTER_CONCEPTS_SUMMARY, text=COL_HEADER_MASTER_CONCEPTS_SUMMARY)

        self.master_tree.column(COL_MASTER_RANK, width=WIDTH_MASTER_RANK, minwidth=MINWIDTH_MASTER_RANK, anchor=tk.CENTER)
        self.master_tree.column(COL_MASTER_SCORE, width=WIDTH_MASTER_SCORE, minwidth=MINWIDTH_MASTER_SCORE, anchor=tk.E)
        self.master_tree.column(COL_MASTER_BOOK, width=WIDTH_MASTER_BOOK, minwidth=MINWIDTH_MASTER_BOOK, anchor=tk.W)
        self.master_tree.column(COL_MASTER_CHAPTER, width=WIDTH_MASTER_CHAPTER, minwidth=MINWIDTH_MASTER_CHAPTER, anchor=tk.W)
        self.master_tree.column(COL_MASTER_CONCEPTS_COUNT, width=WIDTH_MASTER_CONCEPTS_COUNT, minwidth=MINWIDTH_MASTER_CONCEPTS_COUNT, anchor=tk.CENTER)
        self.master_tree.column(COL_MASTER_CHUNKS_COUNT, width=WIDTH_MASTER_CHUNKS_COUNT, minwidth=MINWIDTH_MASTER_CHUNKS_COUNT, anchor=tk.CENTER)
        self.master_tree.column(COL_MASTER_CONCEPTS_SUMMARY, width=WIDTH_MASTER_CONCEPTS_SUMMARY, minwidth=MINWIDTH_MASTER_CONCEPTS_SUMMARY, anchor=tk.W)

        master_vscroll = ttk.Scrollbar(master_tree_container, orient=tk.VERTICAL, command=self.master_tree.yview)
        master_hscroll = ttk.Scrollbar(master_tree_container, orient=tk.HORIZONTAL, command=self.master_tree.xview)
        self.master_tree.configure(yscrollcommand=master_vscroll.set, xscrollcommand=master_hscroll.set)

        master_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        master_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.master_tree.pack(fill=tk.BOTH, expand=True)

        self.master_tree.bind("<<TreeviewSelect>>", self._on_master_select)

        # ----------------------------------------------------------------------
        # Bottom Panel (50% Height): Horizontal Split (Left: Chunks, Right: Concepts)
        # ----------------------------------------------------------------------
        self.bottom_frame = ttk.Frame(self.vertical_paned)
        self.vertical_paned.add(self.bottom_frame, weight=WEIGHT_BOTTOM_PANEL)

        self.horizontal_paned = ttk.PanedWindow(self.bottom_frame, orient=tk.HORIZONTAL)
        self.horizontal_paned.pack(fill=tk.BOTH, expand=True)

        # ----------------------------------------------------
        # Bottom Left: Contiguous Chunks & Text Preview (65% width)
        # ----------------------------------------------------
        self.chunks_frame = ttk.Frame(self.horizontal_paned)
        self.horizontal_paned.add(self.chunks_frame, weight=WEIGHT_CHUNKS_CONTAINER)

        chunks_title = ttk.Label(
            self.chunks_frame,
            text=HEADER_CHUNKS_TITLE,
            font=(FONT_FAMILY_TITLE, FONT_SIZE_HEADER, FONT_WEIGHT_BOLD)
        )
        chunks_title.pack(side=tk.TOP, anchor=tk.W, padx=TITLE_PADX, pady=TITLE_PADY)

        chunks_tree_container = ttk.Frame(self.chunks_frame)
        chunks_tree_container.pack(fill=tk.BOTH, expand=True, padx=PANED_PADX, pady=PANED_PADY)

        chunk_columns = (
            COL_CHUNK_RANK,
            COL_CHUNK_INDEX,
            COL_CHUNK_SCORE,
            COL_CHUNK_SNIPPET
        )

        self.chunks_tree = ttk.Treeview(
            chunks_tree_container,
            columns=chunk_columns,
            show="headings",
            selectmode=TREE_SELECTMODE_BROWSE
        )

        self.chunks_tree.heading(COL_CHUNK_RANK, text=COL_HEADER_CHUNK_RANK)
        self.chunks_tree.heading(COL_CHUNK_INDEX, text=COL_HEADER_CHUNK_INDEX)
        self.chunks_tree.heading(COL_CHUNK_SCORE, text=COL_HEADER_CHUNK_SCORE)
        self.chunks_tree.heading(COL_CHUNK_SNIPPET, text=COL_HEADER_CHUNK_SNIPPET)

        self.chunks_tree.column(COL_CHUNK_RANK, width=WIDTH_CHUNK_RANK, minwidth=MINWIDTH_CHUNK_RANK, anchor=tk.CENTER)
        self.chunks_tree.column(COL_CHUNK_INDEX, width=WIDTH_CHUNK_INDEX, minwidth=MINWIDTH_CHUNK_INDEX, anchor=tk.CENTER)
        self.chunks_tree.column(COL_CHUNK_SCORE, width=WIDTH_CHUNK_SCORE, minwidth=MINWIDTH_CHUNK_SCORE, anchor=tk.E)
        self.chunks_tree.column(COL_CHUNK_SNIPPET, width=WIDTH_CHUNK_SNIPPET, minwidth=MINWIDTH_CHUNK_SNIPPET, anchor=tk.W)

        chunks_vscroll = ttk.Scrollbar(chunks_tree_container, orient=tk.VERTICAL, command=self.chunks_tree.yview)
        chunks_hscroll = ttk.Scrollbar(chunks_tree_container, orient=tk.HORIZONTAL, command=self.chunks_tree.xview)
        self.chunks_tree.configure(yscrollcommand=chunks_vscroll.set, xscrollcommand=chunks_hscroll.set)

        chunks_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        chunks_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.chunks_tree.pack(fill=tk.BOTH, expand=True)

        self.chunks_tree.bind("<<TreeviewSelect>>", self._on_chunk_select)

        # Full Chunk Text Preview Box below chunks_tree
        preview_label = ttk.Label(self.chunks_frame, text=LABEL_TEXT_PREVIEW, font=(FONT_FAMILY_BODY, FONT_SIZE_DETAIL_LABEL, FONT_WEIGHT_BOLD))
        preview_label.pack(side=tk.TOP, anchor=tk.W, padx=TITLE_PADX, pady=(2, 0))

        preview_container = ttk.Frame(self.chunks_frame)
        preview_container.pack(fill=tk.X, padx=PANED_PADX, pady=(0, PANED_PADY))

        self.chunk_text_preview = tk.Text(
            preview_container,
            wrap=tk.WORD,
            height=4,
            font=(FONT_FAMILY_MONO, FONT_SIZE_DETAIL_TEXT),
            bg=COLOR_WHITE,
            fg=COLOR_BLACK
        )
        preview_vscroll = ttk.Scrollbar(preview_container, orient=tk.VERTICAL, command=self.chunk_text_preview.yview)
        self.chunk_text_preview.configure(yscrollcommand=preview_vscroll.set)
        preview_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chunk_text_preview.pack(fill=tk.BOTH, expand=True)

        # ----------------------------------------------------
        # Bottom Right: Matched Concepts & Search Types (35% width)
        # ----------------------------------------------------
        self.concepts_frame = ttk.Frame(self.horizontal_paned)
        self.horizontal_paned.add(self.concepts_frame, weight=WEIGHT_CONCEPTS_CONTAINER)

        concepts_title = ttk.Label(
            self.concepts_frame,
            text=HEADER_CONCEPTS_TITLE,
            font=(FONT_FAMILY_TITLE, FONT_SIZE_HEADER, FONT_WEIGHT_BOLD)
        )
        concepts_title.pack(side=tk.TOP, anchor=tk.W, padx=TITLE_PADX, pady=TITLE_PADY)

        concepts_tree_container = ttk.Frame(self.concepts_frame)
        concepts_tree_container.pack(fill=tk.BOTH, expand=True, padx=PANED_PADX, pady=PANED_PADY)

        concept_columns = (
            COL_CONCEPT_RANK,
            COL_CONCEPT_PHRASE,
            COL_CONCEPT_TYPE
        )

        self.concepts_tree = ttk.Treeview(
            concepts_tree_container,
            columns=concept_columns,
            show="headings",
            selectmode=TREE_SELECTMODE_BROWSE
        )

        self.concepts_tree.heading(COL_CONCEPT_RANK, text=COL_HEADER_CONCEPT_RANK)
        self.concepts_tree.heading(COL_CONCEPT_PHRASE, text=COL_HEADER_CONCEPT_PHRASE)
        self.concepts_tree.heading(COL_CONCEPT_TYPE, text=COL_HEADER_CONCEPT_TYPE)

        self.concepts_tree.column(COL_CONCEPT_RANK, width=WIDTH_CONCEPT_RANK, minwidth=MINWIDTH_CONCEPT_RANK, anchor=tk.CENTER)
        self.concepts_tree.column(COL_CONCEPT_PHRASE, width=WIDTH_CONCEPT_PHRASE, minwidth=MINWIDTH_CONCEPT_PHRASE, anchor=tk.W)
        self.concepts_tree.column(COL_CONCEPT_TYPE, width=WIDTH_CONCEPT_TYPE, minwidth=MINWIDTH_CONCEPT_TYPE, anchor=tk.CENTER)

        concepts_vscroll = ttk.Scrollbar(concepts_tree_container, orient=tk.VERTICAL, command=self.concepts_tree.yview)
        concepts_hscroll = ttk.Scrollbar(concepts_tree_container, orient=tk.HORIZONTAL, command=self.concepts_tree.xview)
        self.concepts_tree.configure(yscrollcommand=concepts_vscroll.set, xscrollcommand=concepts_hscroll.set)

        concepts_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        concepts_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.concepts_tree.pack(fill=tk.BOTH, expand=True)

    def on_search_submit(self):
        text = self.concepts_entry.get().strip()
        if not text:
            messagebox.showwarning(MSG_TITLE_INPUT_NEEDED, MSG_TEXT_INPUT_NEEDED)
            return

        try:
            conc_val = int(self.concurrency_entry.get().strip())
        except ValueError:
            conc_val = DEFAULT_MAX_CONCURRENT_QUERIES

        try:
            top_n_val = int(self.top_n_entry.get().strip())
        except ValueError:
            top_n_val = DEFAULT_TOP_K

        concepts = [c.strip() for c in text.split(QUERY_DELIMITER) if c.strip()]
        if not concepts:
            messagebox.showwarning(MSG_TITLE_INPUT_NEEDED, MSG_TEXT_INPUT_NEEDED)
            return

        if self.content_generator is None:
            self.content_generator = AugmentedContentGenerator()

        start_time = time.time()
        self.status_var.set(STATUS_SEARCHING)
        self.search_button.config(state=STATE_DISABLED)
        self.root.config(cursor=CURSOR_WATCH)

        threading.Thread(
            target=self._async_run_search,
            args=(concepts, conc_val, top_n_val, start_time),
            daemon=True
        ).start()

    def _async_run_search(self, concepts: List[str], max_concurrent: int, top_n_val: int, start_time: float):
        try:
            results = self.content_generator.generate_augmented_content(concepts, max_concurrent=max_concurrent, top_k=top_n_val)
            elapsed = time.time() - start_time
            self.root.after(
                INITIAL_ASYNCHRONOUS_DELAY_MS,
                lambda: self._display_search_results(results, elapsed)
            )
        except Exception as e:
            self.root.after(
                INITIAL_ASYNCHRONOUS_DELAY_MS,
                lambda: self._on_search_error(str(e))
            )

    def _on_search_error(self, err_msg: str):
        self.root.config(cursor=CURSOR_DEFAULT)
        self.search_button.config(state=STATE_NORMAL)
        self.status_var.set(STATUS_ERROR_FORMAT.format(error=err_msg))

    def _display_search_results(self, results: List[Dict[str, Any]], elapsed: float):
        self.root.config(cursor=CURSOR_DEFAULT)
        self.search_button.config(state=STATE_NORMAL)
        self.current_results = results

        # Clear all treeviews
        for tree in (self.master_tree, self.chunks_tree, self.concepts_tree):
            for item in tree.get_children():
                tree.delete(item)
        self.chunk_text_preview.delete(TEXT_START_INDEX, tk.END)

        for rank, item in enumerate(results, start=1):
            tot_score = f"{item['total_aggregated_score']:.4f}"
            b_name = item["book_name"]
            ch_str = f"Ch.{item['chapter_number']}: {item['chapter_title']}"
            concepts_cnt = len(item["matched_concepts"])
            chunks_cnt = len(item["chunks"])
            concepts_summary = ", ".join(item["matched_concepts"])

            self.master_tree.insert(
                "",
                tk.END,
                iid=str(rank - 1),
                values=(
                    rank,
                    tot_score,
                    b_name,
                    ch_str,
                    concepts_cnt,
                    chunks_cnt,
                    concepts_summary
                )
            )

        status_msg = STATUS_COMPLETED_FORMAT.format(elapsed=elapsed, count=len(results))
        self.status_var.set(status_msg)

        # Automatically select the top item if available
        first_child = self.master_tree.get_children()
        if first_child:
            self.master_tree.selection_set(first_child[0])
            self.master_tree.focus(first_child[0])

    def _on_master_select(self, event=None):
        selected_items = self.master_tree.selection()
        if not selected_items:
            return

        item_idx = int(selected_items[0])
        if item_idx < 0 or item_idx >= len(self.current_results):
            return

        result_item = self.current_results[item_idx]
        self.selected_master_result = result_item

        # Populate Chunks Treeview (Bottom Left)
        for item in self.chunks_tree.get_children():
            self.chunks_tree.delete(item)
        self.chunk_text_preview.delete(TEXT_START_INDEX, tk.END)

        chunks = result_item.get("chunks", [])
        for c_rank, chunk in enumerate(chunks, start=1):
            c_idx = chunk.get(RESULT_KEY_CHUNK_INDEX, 0)
            sc_val = chunk.get(RESULT_KEY_SCORE, 0.0)
            sc_str = f"{sc_val:.4f}" if sc_val > 0 else "0.0000 (context)"
            raw_text = chunk.get(RESULT_KEY_CHUNK_TEXT, "")
            snippet = raw_text.replace("\n", " ")[:MAX_SNIPPET_LENGTH]

            self.chunks_tree.insert(
                "",
                tk.END,
                iid=str(c_rank - 1),
                values=(c_rank, c_idx, sc_str, snippet)
            )

        # Populate Matched Concepts Treeview (Bottom Right)
        for item in self.concepts_tree.get_children():
            self.concepts_tree.delete(item)

        matched_concepts = result_item.get("matched_concepts", [])
        for m_rank, m_str in enumerate(matched_concepts, start=1):
            # Parse phrase and match_type from "Phrase (match_type)" format
            if "(" in m_str and m_str.endswith(")"):
                parts = m_str.rsplit(" (", 1)
                phrase = parts[0]
                m_type = parts[1][:-1]
            else:
                phrase = m_str
                m_type = "matched"

            self.concepts_tree.insert(
                "",
                tk.END,
                iid=str(m_rank - 1),
                values=(m_rank, phrase, m_type)
            )

        # Select first chunk automatically
        first_chunk_item = self.chunks_tree.get_children()
        if first_chunk_item:
            self.chunks_tree.selection_set(first_chunk_item[0])
            self.chunks_tree.focus(first_chunk_item[0])

    def _on_chunk_select(self, event=None):
        selected_items = self.chunks_tree.selection()
        if not selected_items or not self.selected_master_result:
            return

        c_idx_sel = int(selected_items[0])
        chunks = self.selected_master_result.get("chunks", [])
        if c_idx_sel < 0 or c_idx_sel >= len(chunks):
            return

        chunk = chunks[c_idx_sel]
        full_text = chunk.get(RESULT_KEY_CHUNK_TEXT, "")

        self.chunk_text_preview.delete(TEXT_START_INDEX, tk.END)
        self.chunk_text_preview.insert(TEXT_START_INDEX, full_text)

# ==============================================================================
# CLI PARSER & MAIN ENTRY POINT
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description=CLI_DESCRIPTION)
    parser.add_argument(
        CLI_ARG_QUERIES_FLAG,
        CLI_ARG_QUERIES_SHORT_FLAG,
        type=str,
        default="",
        help=CLI_ARG_QUERIES_HELP
    )
    parser.add_argument(
        CLI_ARG_MAX_CONCURRENT_FLAG,
        CLI_ARG_MAX_CONCURRENT_SHORT_FLAG,
        type=int,
        default=DEFAULT_MAX_CONCURRENT_QUERIES,
        help=CLI_ARG_MAX_CONCURRENT_HELP
    )

    args = parser.parse_args()

    initial_queries = []
    if args.queries:
        initial_queries = [q.strip() for q in args.queries.split(QUERY_DELIMITER) if q.strip()]

    root = tk.Tk()
    app = FinalSearchVisualizerApp(root, initial_queries=initial_queries, max_concurrent=args.max_concurrent)
    root.mainloop()

if __name__ == "__main__":
    main()
