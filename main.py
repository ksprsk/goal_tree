#!/usr/bin/env python3
"""Goal Tree Application - Browser-based goal/task management using NiceGUI."""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from nicegui import ui

from components import BoardsPanel, NodeFieldsPanel, TreeViewComponent
from persistence import JsonStorage
from state import AppState


def create_app() -> None:
    """Create and configure the Goal Tree application."""
    # Remove all margin/padding and compact tree nodes
    ui.add_head_html('''<style>
        body, .q-page-container, .q-page, .nicegui-content {
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
        /* Tree node height - VS Code like */
        .q-tree__node-header {
            padding-top: 2px !important;
            padding-bottom: 2px !important;
        }
        /* Remove default padding from Quasar components */
        .q-scrollarea__content {
            padding: 0 !important;
        }
        .q-tree {
            padding: 0 !important;
        }
        .q-splitter__panel {
            padding: 0 !important;
        }
        /* Node Details minimum height */
        .node-details-panel {
            min-height: 160px !important;
        }
        /* Selected node highlight */
        .q-tree .q-tree__node--selected .q-tree__node-header-content {
            background-color: rgba(33, 150, 243, 0.2) !important;
        }
    </style>''')

    # Initialize storage and state
    storage = JsonStorage("data.json", debounce_ms=500)
    state = AppState(storage)

    # VS Code style layout: Sidebar | Main Area (Editors / Bottom Panel)
    # Outer splitter: Goal Tree (left) | Main Area (right)
    with ui.splitter(value=15).classes("w-full h-[100dvh]").props("limits=[10,30]") as outer_splitter:
        # Left sidebar - Tree View
        with outer_splitter.before:
            with ui.column().classes("w-full h-full bg-gray-50 overflow-hidden gap-0"):
                ui.label("Goal Tree").classes("text-sm font-bold px-2 py-1 text-blue-700 shrink-0")
                tree_view = TreeViewComponent(state)
                tree_view.build()

        # Right main area - vertical splitter (Boards on top, Node Details at bottom)
        with outer_splitter.after:
            with ui.splitter(horizontal=True, value=65).classes("w-full h-full").props("limits=[55,80]") as main_splitter:
                # Top: Boards area (horizontal splitter for left/right boards)
                with main_splitter.before:
                    with ui.splitter(value=50).classes("w-full h-full") as boards_splitter:
                        boards = BoardsPanel(state, boards_splitter)
                        boards.build()

                # Bottom: Node Details panel (compact, console-like)
                with main_splitter.after:
                    with ui.column().classes("w-full h-full bg-gray-50 overflow-hidden node-details-panel"):
                        ui.label("Node Details").classes("text-xs font-bold px-2 py-1 text-gray-600 bg-gray-100")
                        node_fields = NodeFieldsPanel(state, on_tree_refresh=tree_view.refresh)
                        node_fields.build()

    # Subscribe tree rebuild to tree structure changes only
    state.subscribe_tree_change(tree_view.refresh)


# Create the application
create_app()

# Run the application
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Goal Tree", port=8080, reload=True)
