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
    # Initialize storage and state
    storage = JsonStorage("data.json", debounce_ms=500)
    state = AppState(storage)

    # Build UI
    with ui.row().classes("w-full h-screen"):
        # Left sidebar - Tree View
        with ui.column().classes("w-80 h-full bg-gray-50 border-r"):
            ui.label("Goal Tree").classes("text-xl font-bold p-4 text-blue-700")
            ui.separator()
            tree_view = TreeViewComponent(state)
            tree_view.build()

        # Right panel
        with ui.column().classes("flex-grow h-full overflow-auto"):
            # Top section - Node Fields
            with ui.card().classes("w-full"):
                ui.label("Node Details").classes("text-lg font-bold p-2 text-gray-700")
                ui.separator()
                node_fields = NodeFieldsPanel(state, on_tree_refresh=tree_view.refresh)
                node_fields.build()

            # Bottom section - Boards
            with ui.card().classes("w-full flex-grow"):
                ui.label("Boards").classes("text-lg font-bold p-2 text-gray-700")
                ui.separator()
                boards = BoardsPanel(state)
                boards.build()

    # Subscribe tree rebuild to data changes
    state.subscribe_data_change(tree_view.refresh)


# Create the application
create_app()

# Run the application
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Goal Tree", port=8080, reload=True)
