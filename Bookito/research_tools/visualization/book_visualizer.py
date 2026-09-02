import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Add parent directory to sys.path to import Bookito modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.worker import BookParserWorker
from processors.concept_processor import ConceptProcessor
from book import Book, Chapter, Chunk

class BookVisualizerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Bookito Document Visualizer")
        self.root.geometry("1400x850")
        self.root.minsize(900, 600)

        self.parser_worker = BookParserWorker()
        self.concept_processor = ConceptProcessor()
        self.current_book = None
        self.node_tag_map = {}  # Maps tree item ID -> Text widget tag/index

        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except Exception:
            pass

        self._create_menu()
        self._create_layout()
        self._create_status_bar()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open File...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)
        
        self.root.bind("<Control-o>", lambda event: self.open_file())

    def _create_layout(self):
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ----------------------------------------------------
        # Panel 1: Left Panel (Document Hierarchy Treeview)
        # ----------------------------------------------------
        self.left_frame = ttk.Frame(self.paned)
        self.paned.add(self.left_frame, weight=1)

        tree_title_label = ttk.Label(self.left_frame, text="Document Hierarchy", font=("Segoe UI", 10, "bold"))
        tree_title_label.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=2)

        tree_container = ttk.Frame(self.left_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_container, selectmode="browse", show="tree")
        
        tree_vscroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        tree_hscroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_vscroll.set, xscrollcommand=tree_hscroll.set)

        tree_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # ----------------------------------------------------
        # Panel 2: Middle Panel (Chunk Text View)
        # ----------------------------------------------------
        self.middle_frame = ttk.Frame(self.paned)
        self.paned.add(self.middle_frame, weight=3)

        text_title_label = ttk.Label(self.middle_frame, text="Chunk Text Content", font=("Segoe UI", 10, "bold"))
        text_title_label.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=2)

        text_container = ttk.Frame(self.middle_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(
            text_container,
            wrap=tk.NONE,
            font=("Consolas", 10),
            bg="#FFFFFF",
            fg="#000000",
            selectbackground="#0078D7",
            selectforeground="#FFFFFF",
            padx=10,
            pady=10
        )

        text_vscroll = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=self.text_area.yview)
        text_hscroll = ttk.Scrollbar(text_container, orient=tk.HORIZONTAL, command=self.text_area.xview)
        self.text_area.configure(yscrollcommand=text_vscroll.set, xscrollcommand=text_hscroll.set)

        text_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        text_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text_area.tag_configure("bg_white", background="#FFFFFF", foreground="#000000")
        self.text_area.tag_configure("bg_gray", background="#F2F4F7", foreground="#000000")
        self.text_area.tag_configure("highlight_selected", background="#FFF2B2", foreground="#000000")

        # ----------------------------------------------------
        # Panel 3: Right Panel (25% Width: Concepts List View)
        # ----------------------------------------------------
        self.right_frame = ttk.Frame(self.paned)
        self.paned.add(self.right_frame, weight=1)

        concepts_title_label = ttk.Label(self.right_frame, text="Extracted Concepts", font=("Segoe UI", 10, "bold"))
        concepts_title_label.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=2)

        concepts_container = ttk.Frame(self.right_frame)
        concepts_container.pack(fill=tk.BOTH, expand=True)

        concept_cols = ("phrase", "score", "instances", "chapters")
        self.concepts_tree = ttk.Treeview(
            concepts_container,
            selectmode="browse",
            show="headings",
            columns=concept_cols
        )

        self.concepts_tree.heading("phrase", text="Concept Phrase", anchor=tk.W)
        self.concepts_tree.heading("score", text="Score", anchor=tk.E)
        self.concepts_tree.heading("instances", text="Instances", anchor=tk.E)
        self.concepts_tree.heading("chapters", text="Chapters", anchor=tk.E)

        self.concepts_tree.column("phrase", width=160, minwidth=100, anchor=tk.W)
        self.concepts_tree.column("score", width=65, minwidth=50, anchor=tk.E)
        self.concepts_tree.column("instances", width=65, minwidth=50, anchor=tk.E)
        self.concepts_tree.column("chapters", width=65, minwidth=50, anchor=tk.E)

        concepts_vscroll = ttk.Scrollbar(concepts_container, orient=tk.VERTICAL, command=self.concepts_tree.yview)
        concepts_hscroll = ttk.Scrollbar(concepts_container, orient=tk.HORIZONTAL, command=self.concepts_tree.xview)
        self.concepts_tree.configure(yscrollcommand=concepts_vscroll.set, xscrollcommand=concepts_hscroll.set)

        concepts_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        concepts_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.concepts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Open a book file (.pdf, .epub, .chm) to visualize.")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open Book File",
            filetypes=[
                ("Supported Books", "*.pdf;*.epub;*.chm"),
                ("PDF Documents", "*.pdf"),
                ("EPUB Documents", "*.epub"),
                ("CHM Help Files", "*.chm"),
                ("All Files", "*.*")
            ]
        )
        if not file_path:
            return

        self.status_var.set(f"Parsing '{os.path.basename(file_path)}'... Please wait.")
        self.root.config(cursor="watch")
        self.root.update_idletasks()

        threading.Thread(target=self._async_parse_and_display, args=(file_path,), daemon=True).start()

    def _async_parse_and_display(self, file_path: str):
        try:
            book_obj = self.parser_worker.parse_book(file_path)
            self.root.after(0, lambda: self.status_var.set(f"Classifying chunks and concepts for '{os.path.basename(file_path)}'..."))
            concepts = self.concept_processor.processBook(book_obj)
            self.root.after(0, lambda: self._display_book(book_obj, file_path, concepts))
        except Exception as e:
            self.root.after(0, lambda: self._on_parse_error(file_path, str(e)))

    def _on_parse_error(self, file_path: str, err_msg: str):
        self.root.config(cursor="")
        self.status_var.set(f"Error parsing '{os.path.basename(file_path)}'.")
        messagebox.showerror("Parse Error", f"Failed to parse file:\n{file_path}\n\nError: {err_msg}")

    def _display_book(self, book_obj: Book, file_path: str, concepts: list = None):
        self.root.config(cursor="")
        self.current_book = book_obj
        self.node_tag_map.clear()

        # Clear Treeviews and Text Area
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in self.concepts_tree.get_children():
            self.concepts_tree.delete(item)

        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)

        book_title = book_obj.Title or os.path.basename(file_path)
        book_tree_id = self.tree.insert("", "end", text=f"Book: {book_title}", open=True)

        chunk_counter = 0

        for ch in book_obj.Chapters:
            ch_title = f"Chapter {ch.Number}: {ch.Title}" if ch.Number > 0 else f"Chapter: {ch.Title}"
            ch_tree_id = self.tree.insert(book_tree_id, "end", text=ch_title, open=False)
            ch_first_pos = None

            for chunk in ch.Chunks:
                chunk_counter += 1
                c_idx = chunk.Index if chunk.Index > 0 else chunk_counter
                c_type = chunk.Type if chunk.Type else "AMBIGUOUS"
                chunk_label = f"Chunk {c_idx} ({c_type})"
                chunk_tree_id = self.tree.insert(ch_tree_id, "end", text=chunk_label)

                bg_tag = "bg_white" if (chunk_counter % 2 == 0) else "bg_gray"

                start_index = self.text_area.index("end-1c")
                if ch_first_pos is None:
                    ch_first_pos = start_index

                pos_tag = f"tag_chunk_{chunk_counter}"
                chunk_text_content = chunk.Text if chunk.Text.endswith("\n") else chunk.Text + "\n"
                
                self.text_area.insert(tk.END, chunk_text_content, (bg_tag, pos_tag))
                self.node_tag_map[chunk_tree_id] = pos_tag

            if ch_first_pos:
                ch_tag = f"tag_ch_{ch.Id if ch.Id > 0 else ch.Number}"
                self.text_area.tag_add(ch_tag, ch_first_pos, self.text_area.index("end-1c"))
                self.node_tag_map[ch_tree_id] = ch_tag

        self.node_tag_map[book_tree_id] = "1.0"

        # Populate Concepts List View
        concept_count = 0
        if concepts:
            concept_count = len(concepts)
            for phrase, score, chapters_count, total_occurrences in concepts:
                score_fmt = f"{score:.2f}"
                self.concepts_tree.insert("", "end", values=(phrase, score_fmt, total_occurrences, chapters_count))

        filename = os.path.basename(file_path)
        self.status_var.set(f"Loaded '{filename}' | {len(book_obj.Chapters)} Chapters | {chunk_counter} Chunks | {concept_count} Concepts")

    def _on_tree_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        node_id = selected_items[0]
        target = self.node_tag_map.get(node_id)
        if not target:
            return

        self.text_area.tag_remove("highlight_selected", "1.0", tk.END)

        if target == "1.0":
            self.text_area.see("1.0")
        else:
            ranges = self.text_area.tag_ranges(target)
            if ranges:
                start_pos, end_pos = ranges[0], ranges[1]
                self.text_area.see(start_pos)
                self.text_area.tag_add("highlight_selected", start_pos, end_pos)

def main():
    root = tk.Tk()
    app = BookVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
