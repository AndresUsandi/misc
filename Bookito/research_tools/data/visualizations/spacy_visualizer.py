import json
import sys
import textwrap
import spacy
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTextEdit,
    QPushButton,
    QLabel,
    QSplitter,
    QFrame
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

# ==============================================================================
# CONSTANTS & CONFIGURATION
# ==============================================================================
APP_WINDOW_TITLE = "SpaCy Subphrase & Dependency Graph Visualizer"
APP_WINDOW_WIDTH = 1400
APP_WINDOW_HEIGHT = 900

SPACY_MODEL_NAME = "en_core_web_sm"

COLOR_NOUN = {"background": "#e0f2fe", "border": "#0284c7", "text": "#0369a1"}
COLOR_VERB = {"background": "#dcfce7", "border": "#16a34a", "text": "#15803d"}
COLOR_ADJ = {"background": "#f3e8ff", "border": "#9333ea", "text": "#7e22ce"}
COLOR_ADV = {"background": "#ffedd5", "border": "#ea580c", "text": "#c2410c"}
COLOR_PRON = {"background": "#fef3c7", "border": "#d97706", "text": "#b45309"}
COLOR_ADP = {"background": "#f1f5f9", "border": "#64748b", "text": "#475569"}
COLOR_DET = {"background": "#f8fafc", "border": "#94a3b8", "text": "#64748b"}
COLOR_DEFAULT = {"background": "#f3f4f6", "border": "#6b7280", "text": "#374151"}

POS_COLOR_MAP = {
    "NOUN": COLOR_NOUN,
    "PROPN": COLOR_NOUN,
    "VERB": COLOR_VERB,
    "AUX": COLOR_VERB,
    "ADJ": COLOR_ADJ,
    "ADV": COLOR_ADV,
    "PRON": COLOR_PRON,
    "ADP": COLOR_ADP,
    "DET": COLOR_DET,
}

COLOR_PHRASE_BG = "#1e293b"
COLOR_PHRASE_BORDER = "#64748b"
COLOR_ROOT_BORDER = "#f59e0b"
COLOR_PHRASE_TEXT = "#f8fafc"
COLOR_LEAF_TEXT = "#0f172a"
COLOR_HIGHLIGHT_BG = "#ffffff"
COLOR_HIGHLIGHT_BORDER = "#38bdf8"

BORDER_WIDTH_ROOT = 3
BORDER_WIDTH_NORMAL = 2
TEXTWRAP_WIDTH = 36

VIS_JS_CDN_URL = "https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/vis-network.min.js"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Subphrase Tree Visualizer</title>
    <script type="text/javascript">
        // Polyfills for older Chromium embedded engines (QtWebEngine)
        if (!Array.prototype.toReversed) {
            Array.prototype.toReversed = function() {
                return this.slice().reverse();
            };
        }
        if (!Array.prototype.toSorted) {
            Array.prototype.toSorted = function(compareFn) {
                return this.slice().sort(compareFn);
            };
        }
        if (!Array.prototype.toSpliced) {
            Array.prototype.toSpliced = function(start, deleteCount) {
                var items = Array.prototype.slice.call(arguments, 2);
                var copy = this.slice();
                copy.splice.apply(copy, [start, deleteCount].concat(items));
                return copy;
            };
        }
    </script>
    <script type="text/javascript" src="__VIS_JS_URL__"></script>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        body, html {
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #0f172a;
            color: #f8fafc;
        }
        #toolbar {
            position: absolute;
            top: 12px;
            left: 12px;
            z-index: 10;
            background: rgba(30, 41, 59, 0.85);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 8px 16px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            display: flex;
            gap: 12px;
            align-items: center;
            font-size: 13px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .legend-badge {
            width: 12px;
            height: 12px;
            border-radius: 3px;
            display: inline-block;
        }
        #network-container {
            width: 100%;
            height: 100%;
        }
    </style>
</head>
<body>
    <div id="toolbar">
        <span style="font-weight: 600; color: #94a3b8; margin-right: 4px;">Node Types:</span>
        <div class="legend-item"><span class="legend-badge" style="background: #1e293b; border: 1px solid #64748b;"></span> Multi-Word Subphrase</div>
        <div class="legend-item"><span class="legend-badge" style="background: #0284c7;"></span> NOUN/PROPN</div>
        <div class="legend-item"><span class="legend-badge" style="background: #16a34a;"></span> VERB/AUX</div>
        <div class="legend-item"><span class="legend-badge" style="background: #9333ea;"></span> ADJ</div>
        <div class="legend-item"><span class="legend-badge" style="background: #ea580c;"></span> ADV</div>
        <div class="legend-item"><span class="legend-badge" style="background: #d97706;"></span> PRON</div>
        <div class="legend-item"><span class="legend-badge" style="background: #64748b;"></span> ADP/DET</div>
    </div>
    <div id="network-container"></div>
    <script type="text/javascript">
        var nodesData = __NODES_JSON__;
        var edgesData = __EDGES_JSON__;

        var container = document.getElementById('network-container');
        var data = {
            nodes: new vis.DataSet(nodesData),
            edges: new vis.DataSet(edgesData)
        };

        var options = {
            layout: {
                hierarchical: {
                    direction: 'UD',
                    sortMethod: 'directed',
                    levelSeparation: 140,
                    nodeSpacing: 220,
                    treeSpacing: 240,
                    blockShifting: true,
                    edgeMinimization: true,
                    parentCentralization: true
                }
            },
            interaction: {
                dragNodes: true,
                dragView: true,
                zoomView: true,
                hover: true,
                navigationButtons: true,
                keyboard: true
            },
            physics: {
                enabled: false
            },
            nodes: {
                shape: 'box',
                shapeProperties: {
                    borderRadius: 8
                },
                borderWidth: 2,
                margin: 12,
                shadow: {
                    enabled: true,
                    color: 'rgba(0,0,0,0.35)',
                    size: 8,
                    x: 3,
                    y: 3
                },
                font: {
                    multi: 'html',
                    size: 13,
                    face: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
                }
            },
            edges: {
                arrows: {
                    to: { enabled: true, scaleFactor: 0.9 }
                },
                color: {
                    color: '#64748b',
                    highlight: '#38bdf8',
                    hover: '#38bdf8'
                },
                width: 2,
                font: {
                    size: 12,
                    face: 'Segoe UI, sans-serif',
                    color: '#38bdf8',
                    strokeWidth: 3,
                    strokeColor: '#0f172a',
                    align: 'middle'
                },
                smooth: {
                    type: 'cubicBezier',
                    forceDirection: 'vertical',
                    roundness: 0.4
                }
            }
        };

        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""

def escape_html(text: str) -> str:
    """Escapes HTML special characters for Vis.js label rendering."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

# ==============================================================================
# MAIN APPLICATION CLASS
# ==============================================================================
class SpacyVisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_WINDOW_TITLE)
        self.resize(APP_WINDOW_WIDTH, APP_WINDOW_HEIGHT)

        # Load spaCy NLP pipeline
        try:
            self.nlp = spacy.load(SPACY_MODEL_NAME)
        except Exception as e:
            print(f"Could not load spaCy model '{SPACY_MODEL_NAME}': {e}")
            self.nlp = None

        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Splitter to allow resizing top input and bottom graph
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)

        # Top Control Container
        top_container = QFrame()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(6)

        label = QLabel("<b>Enter Text to Analyze & Generate Subphrase Tree:</b>")
        top_layout.addWidget(label)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter sentence here...")
        self.text_input.setText(
            "We currently rely on a monolithic architecture that is reaching its end of life."
        )
        self.text_input.setFixedHeight(75)
        top_layout.addWidget(self.text_input)

        btn_row = QHBoxLayout()
        self.process_btn = QPushButton("Generate Graph Tree")
        self.process_btn.setStyleSheet(
            "QPushButton { background-color: #0284c7; color: white; font-weight: bold; "
            "padding: 8px 16px; border-radius: 4px; } "
            "QPushButton:hover { background-color: #0369a1; }"
        )
        self.process_btn.clicked.connect(self.process_text)
        btn_row.addStretch()
        btn_row.addWidget(self.process_btn)
        top_layout.addLayout(btn_row)

        splitter.addWidget(top_container)

        # Bottom Graph Container (QWebEngineView)
        self.browser = QWebEngineView()
        splitter.addWidget(self.browser)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 6)

        # Initial render
        self.process_text()

    def process_text(self):
        if not self.nlp:
            self.browser.setHtml("<h2 style='color:red;'>SpaCy model failed to load.</h2>")
            return

        text = self.text_input.toPlainText().strip()
        if not text:
            return

        doc = self.nlp(text)

        nodes = []
        edges = []
        node_counter = 0

        def process_token_node(token, parent_id=None, dep_label=None):
            nonlocal node_counter
            current_id = node_counter
            node_counter += 1

            subtree_tokens = list(token.subtree)
            subtree_tokens.sort(key=lambda t: t.i)
            word_count = len(subtree_tokens)
            subtree_text = " ".join([t.text for t in subtree_tokens])
            is_root = token.head == token

            clean_sub = escape_html(subtree_text)
            clean_tok = escape_html(token.text)

            if word_count > 1:
                # Multi-word phrase node (internal level)
                wrapped_text = textwrap.fill(clean_sub, width=TEXTWRAP_WIDTH)
                label = (
                    f"<b>\"{wrapped_text}\"</b>\n"
                    f"({word_count} words | Head: <b>{clean_tok}</b> [{token.pos_}])"
                )

                nodes.append({
                    "id": current_id,
                    "label": label,
                    "color": {
                        "background": COLOR_PHRASE_BG,
                        "border": COLOR_ROOT_BORDER if is_root else COLOR_PHRASE_BORDER,
                        "highlight": {"background": COLOR_HIGHLIGHT_BG, "border": COLOR_HIGHLIGHT_BORDER}
                    },
                    "font": {
                        "color": COLOR_PHRASE_TEXT,
                        "multi": "html",
                        "size": 13
                    },
                    "borderWidth": BORDER_WIDTH_ROOT if is_root else BORDER_WIDTH_NORMAL
                })

                if parent_id is not None:
                    edges.append({
                        "from": parent_id,
                        "to": current_id,
                        "label": f" {dep_label} " if dep_label else "",
                        "title": f"Dependency: {dep_label}" if dep_label else ""
                    })

                # Decompose into immediate elements (Head token itself + Child subtrees in sentence order)
                immediate_elements = []

                # Add head token itself
                immediate_elements.append({
                    "is_head": True,
                    "index": token.i,
                    "token": token
                })

                # Add direct children
                for child in token.children:
                    immediate_elements.append({
                        "is_head": False,
                        "index": child.i,
                        "token": child
                    })

                # Sort by original token position in sentence
                immediate_elements.sort(key=lambda x: x["index"])

                # Recursively add children and head word
                for elem in immediate_elements:
                    if elem["is_head"]:
                        # Leaf node for head word itself
                        head_id = node_counter
                        node_counter += 1
                        head_tok = elem["token"]
                        h_color = POS_COLOR_MAP.get(head_tok.pos_, COLOR_DEFAULT)

                        h_label = (
                            f"<b>\"{escape_html(head_tok.text)}\"</b>\n"
                            f"<b>{head_tok.pos_}</b>"
                        )

                        nodes.append({
                            "id": head_id,
                            "label": h_label,
                            "color": {
                                "background": h_color["background"],
                                "border": h_color["border"],
                                "highlight": {"background": COLOR_HIGHLIGHT_BG, "border": COLOR_HIGHLIGHT_BORDER}
                            },
                            "font": {
                                "color": COLOR_LEAF_TEXT,
                                "multi": "html",
                                "size": 13
                            },
                            "borderWidth": BORDER_WIDTH_NORMAL
                        })

                        edges.append({
                            "from": current_id,
                            "to": head_id,
                            "label": f" [{head_tok.dep_}] ",
                            "title": f"Head word: '{head_tok.text}' ({head_tok.dep_})"
                        })
                    else:
                        child_tok = elem["token"]
                        process_token_node(child_tok, parent_id=current_id, dep_label=child_tok.dep_)

            else:
                # Single-word leaf node
                color_info = POS_COLOR_MAP.get(token.pos_, COLOR_DEFAULT)
                label = (
                    f"<b>\"{clean_tok}\"</b>\n"
                    f"<b>{token.pos_}</b>"
                )

                nodes.append({
                    "id": current_id,
                    "label": label,
                    "color": {
                        "background": color_info["background"],
                        "border": color_info["border"],
                        "highlight": {"background": COLOR_HIGHLIGHT_BG, "border": COLOR_HIGHLIGHT_BORDER}
                    },
                    "font": {
                        "color": COLOR_LEAF_TEXT,
                        "multi": "html",
                        "size": 13
                    },
                    "borderWidth": BORDER_WIDTH_NORMAL
                })

                if parent_id is not None:
                    edges.append({
                        "from": parent_id,
                        "to": current_id,
                        "label": f" {dep_label} " if dep_label else "",
                        "title": f"Dependency: {dep_label}" if dep_label else ""
                    })

        # Process from sentence root(s)
        for token in doc:
            if token.head == token:
                process_token_node(token)

        # Inject JSON into template safely using string replace
        nodes_json = json.dumps(nodes)
        edges_json = json.dumps(edges)
        rendered_html = (
            HTML_TEMPLATE.replace("__VIS_JS_URL__", VIS_JS_CDN_URL)
            .replace("__NODES_JSON__", nodes_json)
            .replace("__EDGES_JSON__", edges_json)
        )

        self.browser.setHtml(rendered_html)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpacyVisualizerApp()
    window.show()
    sys.exit(app.exec_())
