import sys
import os
import time
import threading
import concurrent.futures
import argparse
import tkinter as tk
from tkinter import ttk, messagebox

# Add parent directory to sys.path to import Bookito modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.query_manager import QueryManager, DEFAULT_TOP_K
from visualization.constants import (
    CLI_ARG_QUERIES_FLAG,
    CLI_ARG_QUERIES_SHORT_FLAG,
    CLI_ARG_QUERIES_HELP,
    CLI_ARG_MAX_CONCURRENT_FLAG,
    CLI_ARG_MAX_CONCURRENT_SHORT_FLAG,
    CLI_ARG_MAX_CONCURRENT_HELP,
    CLI_DESCRIPTION,
    QUERY_DELIMITER,
    DEFAULT_MAX_CONCURRENT_QUERIES
)

# ==============================================================================
# TOP-OF-FILE CONFIGURATION & UI CONSTANTS
# ==============================================================================

WINDOW_TITLE = "Bookito OpenSearch Multi-Tab Search Visualizer"
WINDOW_GEOMETRY = "1380x880"
WINDOW_MIN_WIDTH = 950
WINDOW_MIN_HEIGHT = 650
INITIAL_ASYNCHRONOUS_DELAY_MS = 0
SEARCH_PAGE_SIZE = 50
DEFAULT_INITIAL_PAGE = 1
MAX_SNIPPET_LENGTH = 80
MAX_TAB_TITLE_LENGTH = 20

WEIGHT_TOP_PANEL = 1
WEIGHT_BOTTOM_PANEL = 1
WEIGHT_TREE_CONTAINER = 3
WEIGHT_DETAIL_CONTAINER = 2

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
TAB_HEADER_PADDING = 3
LABEL_PADX = (5, 5)
ENTRY_PADX = 5
BUTTON_PADX = (5, 5)
PAGINATION_PADX = (2, 2)
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
FONT_WEIGHT_ITALIC = "italic"

# Color and Styling Constants
COLOR_WHITE = "#FFFFFF"
COLOR_BLACK = "#000000"
TTK_THEME_CLAM = "clam"

# Treeview Column Identifiers
COL_SCORE = "score"
COL_BOOK = "book"
COL_CHAPTER = "chapter"
COL_CHUNK_IDX = "chunk_index"
COL_TEXT = "chunk_text"

# Treeview Column Headers
COL_HEADER_SCORE = "Score"
COL_HEADER_BOOK = "Book Name"
COL_HEADER_CHAPTER = "Chapter"
COL_HEADER_CHUNK_IDX = "Chunk Index"
COL_HEADER_TEXT = "Chunk Text Preview"

# Treeview Column Widths
WIDTH_SCORE = 70
MINWIDTH_SCORE = 50
WIDTH_BOOK = 200
MINWIDTH_BOOK = 120
WIDTH_CHAPTER = 220
MINWIDTH_CHAPTER = 120
WIDTH_CHUNK_IDX = 80
MINWIDTH_CHUNK_IDX = 60
WIDTH_TEXT = 350
MINWIDTH_TEXT = 150

# Result Dictionary Key Constants (matching QueryManager)
RESULT_KEY_SCORE = "score"
RESULT_KEY_CHUNK_ID = "chunk_id"
RESULT_KEY_CHUNK_INDEX = "chunk_index"
RESULT_KEY_CHUNK_TEXT = "chunk_text"
RESULT_KEY_VECTOR_DIM = "vector_dim"
RESULT_KEY_CHAPTER_ID = "chapter_id"
RESULT_KEY_CHAPTER_NUMBER = "chapter_number"
RESULT_KEY_CHAPTER_TITLE = "chapter_title"
RESULT_KEY_BOOK_ID = "book_id"
RESULT_KEY_BOOK_NAME = "book_name"
RESULT_KEY_FILE_LINK = "file_link"

# UI Headers, Buttons & Section Labels
HEADER_LEXICAL_TITLE = "Lexical Search Results (OpenSearch Text Match)"
HEADER_VECTOR_TITLE = "Vector Search Results (KNN Semantic Search)"
LABEL_QUERY_TERMS = "Query Terms:"
LABEL_QUERY_BUTTON = "Query"
LABEL_TOP_N = "Top N:"
ENTRY_TOP_N_WIDTH = 5
LABEL_NEW_TAB_BUTTON = "+ New Search Tab"
LABEL_CLOSE_TAB_BUTTON = "Close Active Tab"
LABEL_PREV_PAGE = "< Prev Page"
LABEL_NEXT_PAGE = "Next Page >"
LABEL_PAGE_FORMAT = "Page {page}"
LABEL_FULL_DETAILS_HEADER = "Full Chunk & Metadata Details"
DEFAULT_NEW_TAB_NAME_FORMAT = "Search {number}"
ELLIPSIS_SUFFIX = "..."

# Status Messages and Formats
STATUS_CONNECTING = "Connecting to OpenSearch..."
STATUS_READY = "Ready. Open a search tab, enter a query, and click 'Query' (or press Enter) to search."
STATUS_SEARCHING_FORMAT = "Tab '{tab_name}': Searching for '{query}' (Page {page})... Please wait."
STATUS_FAILED = "Search execution failed."
STATUS_RESULTS_FORMAT = "Tab '{tab_name}' | Query: '{query}' | Page: {page} | Lexical Hits: {lexical_count} | Vector Hits: {vector_count} | Elapsed: {elapsed:.2f}s"
STATUS_CONNECTION_ERROR_FORMAT = "OpenSearch Connection Error: {error}"

# Dialog Messages
MSG_TITLE_INPUT_NEEDED = "Input Needed"
MSG_TEXT_INPUT_NEEDED = "Please enter query terms to search."
MSG_TITLE_NOT_CONNECTED = "Not Connected"
MSG_TEXT_NOT_CONNECTED = "OpenSearch connection is not ready yet."
MSG_TITLE_SEARCH_ERROR = "Search Error"
MSG_TEXT_SEARCH_ERROR_FORMAT = "Failed to execute search query:\n{error}"

# Formatter String Templates
SCORE_TREE_FORMAT = "{score:.4f}"
CHAPTER_TREE_FORMAT = "Ch {chapter_number}: {chapter_title}"
CHUNK_IDX_TREE_FORMAT = "Chunk {chunk_index}"
SNIPPET_REPLACE_TARGET = "\n"
SNIPPET_REPLACE_DEST = " "

DETAILS_TEMPLATE = (
    "=== CHUNK PROPERTIES ===\n"
    "Chunk ID      : {chunk_id}\n"
    "Chunk Index   : {chunk_index}\n"
    "Search Score  : {score:.6f}\n"
    "Vector Dim    : {vector_dim} dims\n\n"
    "=== CHAPTER METADATA ===\n"
    "Chapter ID    : {chapter_id}\n"
    "Chapter Number: {chapter_number}\n"
    "Chapter Title : {chapter_title}\n\n"
    "=== BOOK METADATA ===\n"
    "Book ID       : {book_id}\n"
    "Book Name     : {book_name}\n"
    "File Link     : {file_link}\n\n"
    "=== CHUNK TEXT CONTENT ===\n"
    "{chunk_text}\n"
)

# Tkinter Event & Attribute Constants
EVENT_KEY_RETURN = "<Return>"
EVENT_TREE_SELECT = "<<TreeviewSelect>>"
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
DATA_MAP_ATTRIBUTE = "_data_map"
PENDING_AUTO_SEARCH_ATTRIBUTE = "pending_auto_search"
EMPTY_STRING = ""

class SearchTab(ttk.Frame):
    """Encapsulates a single search tab interface (Lexical + Vector search views, control bar, and individual query state)."""
    def __init__(self, parent: ttk.Notebook, app_instance: 'OpenSearchSearchVisualizerApp', tab_name: str, initial_query: str = "", auto_search: bool = False):
        super().__init__(parent)
        self.parent = parent
        self.app = app_instance
        self.tab_name = tab_name
        self.active_query = initial_query
        self.current_page = DEFAULT_INITIAL_PAGE
        setattr(self, PENDING_AUTO_SEARCH_ATTRIBUTE, auto_search)

        self.lexical_tree = None
        self.lexical_details_text = None
        self.vector_tree = None
        self.vector_details_text = None

        self._create_control_bar()
        self._create_layout()

        if initial_query:
            self.query_entry.insert(0, initial_query)

    def _create_layout(self):
        # Vertical split paned window for 50% Top (Lexical) and 50% Bottom (Vector)
        self.paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=PANED_PADX, pady=PANED_PADY)

        # Top Panel: Lexical Search
        self.top_frame = ttk.Frame(self.paned)
        self.paned.add(self.top_frame, weight=WEIGHT_TOP_PANEL)

        top_title = ttk.Label(self.top_frame, text=HEADER_LEXICAL_TITLE, font=(FONT_FAMILY_TITLE, FONT_SIZE_HEADER, FONT_WEIGHT_BOLD))
        top_title.pack(side=tk.TOP, anchor=tk.W, padx=TITLE_PADX, pady=TITLE_PADY)

        self.lexical_tree, self.lexical_details_text = self._build_results_view(self.top_frame)

        # Bottom Panel: Vector Search
        self.bottom_frame = ttk.Frame(self.paned)
        self.paned.add(self.bottom_frame, weight=WEIGHT_BOTTOM_PANEL)

        bottom_title = ttk.Label(self.bottom_frame, text=HEADER_VECTOR_TITLE, font=(FONT_FAMILY_TITLE, FONT_SIZE_HEADER, FONT_WEIGHT_BOLD))
        bottom_title.pack(side=tk.TOP, anchor=tk.W, padx=TITLE_PADX, pady=TITLE_PADY)

        self.vector_tree, self.vector_details_text = self._build_results_view(self.bottom_frame)

    def _build_results_view(self, parent_frame: ttk.Frame):
        """Creates a sub-split frame with Treeview table on left and Detail text preview on right."""
        sub_paned = ttk.PanedWindow(parent_frame, orient=tk.HORIZONTAL)
        sub_paned.pack(fill=tk.BOTH, expand=True)

        # Left Table
        tree_container = ttk.Frame(sub_paned)
        sub_paned.add(tree_container, weight=WEIGHT_TREE_CONTAINER)

        cols = (COL_SCORE, COL_BOOK, COL_CHAPTER, COL_CHUNK_IDX, COL_TEXT)
        tree = ttk.Treeview(tree_container, selectmode=TREE_SELECTMODE_BROWSE, show=TREE_SHOW_HEADINGS, columns=cols)

        tree.heading(COL_SCORE, text=COL_HEADER_SCORE, anchor=tk.E)
        tree.heading(COL_BOOK, text=COL_HEADER_BOOK, anchor=tk.W)
        tree.heading(COL_CHAPTER, text=COL_HEADER_CHAPTER, anchor=tk.W)
        tree.heading(COL_CHUNK_IDX, text=COL_HEADER_CHUNK_IDX, anchor=tk.E)
        tree.heading(COL_TEXT, text=COL_HEADER_TEXT, anchor=tk.W)

        tree.column(COL_SCORE, width=WIDTH_SCORE, minwidth=MINWIDTH_SCORE, anchor=tk.E)
        tree.column(COL_BOOK, width=WIDTH_BOOK, minwidth=MINWIDTH_BOOK, anchor=tk.W)
        tree.column(COL_CHAPTER, width=WIDTH_CHAPTER, minwidth=MINWIDTH_CHAPTER, anchor=tk.W)
        tree.column(COL_CHUNK_IDX, width=WIDTH_CHUNK_IDX, minwidth=MINWIDTH_CHUNK_IDX, anchor=tk.E)
        tree.column(COL_TEXT, width=WIDTH_TEXT, minwidth=MINWIDTH_TEXT, anchor=tk.W)

        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=tree.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right Detail Text Area
        detail_container = ttk.Frame(sub_paned)
        sub_paned.add(detail_container, weight=WEIGHT_DETAIL_CONTAINER)

        detail_label = ttk.Label(detail_container, text=LABEL_FULL_DETAILS_HEADER, font=(FONT_FAMILY_TITLE, FONT_SIZE_DETAIL_LABEL, FONT_WEIGHT_ITALIC))
        detail_label.pack(side=tk.TOP, anchor=tk.W, padx=DETAIL_LABEL_PADX, pady=DETAIL_LABEL_PADY)

        detail_text = tk.Text(
            detail_container,
            wrap=tk.WORD,
            font=(FONT_FAMILY_MONO, FONT_SIZE_DETAIL_TEXT),
            bg=COLOR_WHITE,
            fg=COLOR_BLACK,
            padx=DETAIL_TEXT_PADX,
            pady=DETAIL_TEXT_PADY
        )
        detail_vscroll = ttk.Scrollbar(detail_container, orient=tk.VERTICAL, command=detail_text.yview)
        detail_text.configure(yscrollcommand=detail_vscroll.set)

        detail_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree.bind(EVENT_TREE_SELECT, lambda event, t=tree, d=detail_text: self._on_result_select(t, d))

        return tree, detail_text

    def _create_control_bar(self):
        control_frame = ttk.Frame(self, padding=CONTROL_FRAME_PADDING)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        query_label = ttk.Label(control_frame, text=LABEL_QUERY_TERMS, font=(FONT_FAMILY_BODY, FONT_SIZE_BODY, FONT_WEIGHT_BOLD))
        query_label.pack(side=tk.LEFT, padx=LABEL_PADX)

        self.query_entry = ttk.Entry(control_frame, font=(FONT_FAMILY_BODY, FONT_SIZE_BODY))
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=ENTRY_PADX)
        self.query_entry.focus_set()

        self.query_entry.bind(EVENT_KEY_RETURN, lambda event: self.on_query_submit())

        self.query_button = ttk.Button(control_frame, text=LABEL_QUERY_BUTTON, command=self.on_query_submit)
        self.query_button.pack(side=tk.LEFT, padx=BUTTON_PADX)

        top_n_label = ttk.Label(control_frame, text=LABEL_TOP_N, font=(FONT_FAMILY_BODY, FONT_SIZE_BODY))
        top_n_label.pack(side=tk.LEFT, padx=LABEL_PADX)

        self.top_n_entry = ttk.Entry(control_frame, width=ENTRY_TOP_N_WIDTH, font=(FONT_FAMILY_MONO, FONT_SIZE_BODY))
        self.top_n_entry.insert(0, str(DEFAULT_TOP_K))
        self.top_n_entry.pack(side=tk.LEFT, padx=ENTRY_PADX)

        self.next_button = ttk.Button(control_frame, text=LABEL_NEXT_PAGE, command=self.on_next_page, state=STATE_DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=PAGINATION_PADX)

        self.page_label = ttk.Label(control_frame, text=LABEL_PAGE_FORMAT.format(page=DEFAULT_INITIAL_PAGE), font=(FONT_FAMILY_BODY, FONT_SIZE_BODY, FONT_WEIGHT_BOLD))
        self.page_label.pack(side=tk.RIGHT, padx=PAGINATION_PADX)

        self.prev_button = ttk.Button(control_frame, text=LABEL_PREV_PAGE, command=self.on_prev_page, state=STATE_DISABLED)
        self.prev_button.pack(side=tk.RIGHT, padx=PAGINATION_PADX)

    def on_query_submit(self):
        query_text = self.query_entry.get().strip()
        if not query_text:
            messagebox.showwarning(MSG_TITLE_INPUT_NEEDED, MSG_TEXT_INPUT_NEEDED)
            return

        if not self.app.is_connected or not self.app.query_manager:
            messagebox.showerror(MSG_TITLE_NOT_CONNECTED, MSG_TEXT_NOT_CONNECTED)
            return

        self.active_query = query_text
        self.current_page = DEFAULT_INITIAL_PAGE

        truncated_title = query_text if len(query_text) <= MAX_TAB_TITLE_LENGTH else query_text[:MAX_TAB_TITLE_LENGTH] + ELLIPSIS_SUFFIX
        self.app.update_tab_title(self, truncated_title)

        self._trigger_search_execution()

    def on_prev_page(self):
        if self.current_page > DEFAULT_INITIAL_PAGE and self.active_query:
            self.current_page -= 1
            self._trigger_search_execution()

    def on_next_page(self):
        if self.active_query:
            self.current_page += 1
            self._trigger_search_execution()

    def _trigger_search_execution(self):
        query_text = self.active_query
        start_time = time.time()

        try:
            top_n_val = int(self.top_n_entry.get().strip())
        except ValueError:
            top_n_val = DEFAULT_TOP_K

        self.app.set_status(STATUS_SEARCHING_FORMAT.format(tab_name=self.tab_name, query=query_text, page=self.current_page))
        self.query_button.config(state=STATE_DISABLED)
        self.prev_button.config(state=STATE_DISABLED)
        self.next_button.config(state=STATE_DISABLED)
        self.app.root.config(cursor=CURSOR_WATCH)

        threading.Thread(target=self._async_execute_searches, args=(query_text, self.current_page, top_n_val, start_time), daemon=True).start()

    def _async_execute_searches(self, query_text: str, page: int, top_n_val: int, start_time: float):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_lex = executor.submit(self.app.query_manager.lexical_search, query_text, page=page, page_size=top_n_val, top_k=top_n_val)
                future_vec = executor.submit(self.app.query_manager.vector_search, query_text, page=page, page_size=top_n_val, top_k=top_n_val)

                lexical_results = future_lex.result()
                vector_results = future_vec.result()

            elapsed = time.time() - start_time
            self.app.root.after(INITIAL_ASYNCHRONOUS_DELAY_MS, lambda: self._display_search_results(query_text, page, lexical_results, vector_results, elapsed))
        except Exception as e:
            self.app.root.after(INITIAL_ASYNCHRONOUS_DELAY_MS, lambda: self._on_search_error(str(e)))

    def _on_search_error(self, err_msg: str):
        self.app.root.config(cursor=CURSOR_DEFAULT)
        self.query_button.config(state=STATE_NORMAL)
        self.prev_button.config(state=STATE_NORMAL if self.current_page > DEFAULT_INITIAL_PAGE else STATE_DISABLED)
        self.next_button.config(state=STATE_NORMAL)
        self.app.set_status(STATUS_FAILED)
        messagebox.showerror(MSG_TITLE_SEARCH_ERROR, MSG_TEXT_SEARCH_ERROR_FORMAT.format(error=err_msg))

    def _display_search_results(self, query_text: str, page: int, lexical_results: list, vector_results: list, elapsed: float):
        self.app.root.config(cursor=CURSOR_DEFAULT)
        self.query_button.config(state=STATE_NORMAL)

        self.page_label.config(text=LABEL_PAGE_FORMAT.format(page=page))
        self.prev_button.config(state=STATE_NORMAL if page > DEFAULT_INITIAL_PAGE else STATE_DISABLED)

        has_more_hits = (len(lexical_results) == SEARCH_PAGE_SIZE) or (len(vector_results) == SEARCH_PAGE_SIZE)
        self.next_button.config(state=STATE_NORMAL if has_more_hits else STATE_DISABLED)

        self._populate_tree(self.lexical_tree, self.lexical_details_text, lexical_results)
        self._populate_tree(self.vector_tree, self.vector_details_text, vector_results)

        status_msg = STATUS_RESULTS_FORMAT.format(
            tab_name=self.tab_name,
            query=query_text,
            page=page,
            lexical_count=len(lexical_results),
            vector_count=len(vector_results),
            elapsed=elapsed
        )
        self.app.set_status(status_msg)

    def _populate_tree(self, tree: ttk.Treeview, detail_text: tk.Text, results: list):
        for item in tree.get_children():
            tree.delete(item)

        setattr(tree, DATA_MAP_ATTRIBUTE, {})

        detail_text.config(state=STATE_NORMAL)
        detail_text.delete(TEXT_START_INDEX, tk.END)
        detail_text.config(state=STATE_DISABLED)

        for res in results:
            score_str = SCORE_TREE_FORMAT.format(score=res[RESULT_KEY_SCORE])
            book_str = res[RESULT_KEY_BOOK_NAME]
            ch_str = CHAPTER_TREE_FORMAT.format(
                chapter_number=res[RESULT_KEY_CHAPTER_NUMBER],
                chapter_title=res[RESULT_KEY_CHAPTER_TITLE]
            )
            chunk_idx_str = CHUNK_IDX_TREE_FORMAT.format(chunk_index=res[RESULT_KEY_CHUNK_INDEX])

            raw_text = res[RESULT_KEY_CHUNK_TEXT]
            clean_text = raw_text.replace(SNIPPET_REPLACE_TARGET, SNIPPET_REPLACE_DEST).strip()
            text_snippet = clean_text[:MAX_SNIPPET_LENGTH] + ELLIPSIS_SUFFIX

            item_id = tree.insert(
                TREE_INSERT_PARENT_ROOT,
                TREE_INSERT_POSITION_END,
                values=(score_str, book_str, ch_str, chunk_idx_str, text_snippet)
            )
            tree.set(item_id, column=COL_TEXT, value=text_snippet)
            if not hasattr(tree, DATA_MAP_ATTRIBUTE):
                setattr(tree, DATA_MAP_ATTRIBUTE, {})
            data_map = getattr(tree, DATA_MAP_ATTRIBUTE)
            data_map[item_id] = res

    def _on_result_select(self, tree: ttk.Treeview, detail_text: tk.Text):
        selected = tree.selection()
        if not selected:
            return

        item_id = selected[0]
        data_map = getattr(tree, DATA_MAP_ATTRIBUTE, {})
        res = data_map.get(item_id)
        if not res:
            return

        detail_text.config(state=STATE_NORMAL)
        detail_text.delete(TEXT_START_INDEX, tk.END)

        details_str = DETAILS_TEMPLATE.format(
            chunk_id=res[RESULT_KEY_CHUNK_ID],
            chunk_index=res[RESULT_KEY_CHUNK_INDEX],
            score=res[RESULT_KEY_SCORE],
            vector_dim=res[RESULT_KEY_VECTOR_DIM],
            chapter_id=res[RESULT_KEY_CHAPTER_ID],
            chapter_number=res[RESULT_KEY_CHAPTER_NUMBER],
            chapter_title=res[RESULT_KEY_CHAPTER_TITLE],
            book_id=res[RESULT_KEY_BOOK_ID],
            book_name=res[RESULT_KEY_BOOK_NAME],
            file_link=res[RESULT_KEY_FILE_LINK],
            chunk_text=res[RESULT_KEY_CHUNK_TEXT]
        )

        detail_text.insert(tk.END, details_str)
        detail_text.config(state=STATE_DISABLED)

class OpenSearchSearchVisualizerApp:
    """Multi-tab GUI visualizer application managing search tabs and shared OpenSearch connection."""
    def __init__(self, root: tk.Tk, initial_queries: list = None, max_concurrent: int = DEFAULT_MAX_CONCURRENT_QUERIES):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.max_concurrent = max_concurrent
        self.query_manager = None
        self.is_connected = False
        self.tab_counter = 0

        self.style = ttk.Style()
        try:
            self.style.theme_use(TTK_THEME_CLAM)
        except Exception:
            pass

        self._create_status_bar()
        self._create_top_tab_bar()
        self._create_notebook()

        # Connect to OpenSearch asynchronously on startup
        threading.Thread(target=self._async_init_query_manager, daemon=True).start()

        # Add initial search tab(s)
        first_tab = None
        if initial_queries:
            for query_str in initial_queries:
                created_tab = self.add_new_tab(initial_query=query_str, auto_search=True)
                if first_tab is None:
                    first_tab = created_tab
            if first_tab:
                self.notebook.select(first_tab)
        else:
            self.add_new_tab()

    def _create_top_tab_bar(self):
        tab_control_frame = ttk.Frame(self.root, padding=TAB_HEADER_PADDING)
        tab_control_frame.pack(side=tk.TOP, fill=tk.X)

        self.add_tab_button = ttk.Button(
            tab_control_frame,
            text=LABEL_NEW_TAB_BUTTON,
            command=self.add_new_tab
        )
        self.add_tab_button.pack(side=tk.LEFT, padx=BUTTON_PADX, pady=TITLE_PADY)

        self.close_tab_button = ttk.Button(
            tab_control_frame,
            text=LABEL_CLOSE_TAB_BUTTON,
            command=self.close_current_tab
        )
        self.close_tab_button.pack(side=tk.LEFT, padx=BUTTON_PADX, pady=TITLE_PADY)

    def _create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=PANED_PADX, pady=PANED_PADY)

    def _create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set(STATUS_CONNECTING)
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=STATUS_BAR_PADDING)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, message: str):
        self.status_var.set(message)

    def _async_init_query_manager(self):
        try:
            self.query_manager = QueryManager(max_concurrent_queries=self.max_concurrent)
            self.is_connected = True
            self.root.after(INITIAL_ASYNCHRONOUS_DELAY_MS, self._on_query_manager_ready)
        except Exception as e:
            err_msg = STATUS_CONNECTION_ERROR_FORMAT.format(error=e)
            self.root.after(INITIAL_ASYNCHRONOUS_DELAY_MS, lambda: self.status_var.set(err_msg))

    def _on_query_manager_ready(self):
        self.status_var.set(STATUS_READY)
        self._trigger_pending_auto_searches()

    def _trigger_pending_auto_searches(self):
        for tab_id in self.notebook.tabs():
            tab_widget = self.notebook.nametowidget(tab_id)
            if isinstance(tab_widget, SearchTab) and getattr(tab_widget, PENDING_AUTO_SEARCH_ATTRIBUTE, False):
                setattr(tab_widget, PENDING_AUTO_SEARCH_ATTRIBUTE, False)
                tab_widget.on_query_submit()

    def add_new_tab(self, initial_query: str = "", auto_search: bool = False) -> SearchTab:
        self.tab_counter += 1
        if initial_query:
            tab_title = initial_query if len(initial_query) <= MAX_TAB_TITLE_LENGTH else initial_query[:MAX_TAB_TITLE_LENGTH] + ELLIPSIS_SUFFIX
        else:
            tab_title = DEFAULT_NEW_TAB_NAME_FORMAT.format(number=self.tab_counter)

        search_tab = SearchTab(self.notebook, self, tab_title, initial_query=initial_query, auto_search=auto_search)
        self.notebook.add(search_tab, text=tab_title)
        self.notebook.select(search_tab)

        if auto_search:
            if self.is_connected:
                setattr(search_tab, PENDING_AUTO_SEARCH_ATTRIBUTE, False)
                search_tab.on_query_submit()
            else:
                setattr(search_tab, PENDING_AUTO_SEARCH_ATTRIBUTE, True)

        return search_tab

    def update_tab_title(self, search_tab: SearchTab, new_title: str):
        search_tab.tab_name = new_title
        self.notebook.tab(search_tab, text=new_title)

    def close_current_tab(self):
        selected_tab = self.notebook.select()
        if not selected_tab:
            return

        self.notebook.forget(selected_tab)
        if len(self.notebook.tabs()) == 0:
            self.add_new_tab()

def main():
    parser = argparse.ArgumentParser(description=CLI_DESCRIPTION)
    parser.add_argument(
        CLI_ARG_QUERIES_SHORT_FLAG,
        CLI_ARG_QUERIES_FLAG,
        type=str,
        default=EMPTY_STRING,
        help=CLI_ARG_QUERIES_HELP
    )
    parser.add_argument(
        CLI_ARG_MAX_CONCURRENT_SHORT_FLAG,
        CLI_ARG_MAX_CONCURRENT_FLAG,
        type=int,
        default=DEFAULT_MAX_CONCURRENT_QUERIES,
        help=CLI_ARG_MAX_CONCURRENT_HELP
    )
    args = parser.parse_args()

    initial_queries = []
    if args.queries:
        raw_queries = args.queries.split(QUERY_DELIMITER)
        initial_queries = [q.strip() for q in raw_queries if q and q.strip()]

    root = tk.Tk()
    app = OpenSearchSearchVisualizerApp(root, initial_queries=initial_queries, max_concurrent=args.max_concurrent)
    root.mainloop()

if __name__ == "__main__":
    main()
