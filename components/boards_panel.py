from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nicegui import ui

if TYPE_CHECKING:
    from state import AppState


class BoardsPanel:
    def __init__(self, state: "AppState", splitter: Any = None):
        self.state = state
        self.splitter = splitter
        self.left_container: ui.column | None = None
        self.right_container: ui.column | None = None

    def build(self) -> None:
        if self.splitter:
            # Use splitter's before/after for left/right boards
            with self.splitter.before:
                self.left_container = ui.column().classes("w-full h-full p-0 overflow-hidden")
            with self.splitter.after:
                self.right_container = ui.column().classes("w-full h-full p-0 overflow-hidden")
        else:
            # Fallback: side by side
            with ui.row().classes("w-full h-full"):
                self.left_container = ui.column().classes("w-1/2 h-full")
                self.right_container = ui.column().classes("w-1/2 h-full")

        self._rebuild()
        self.state.subscribe_selection_change(self._rebuild)

    def _rebuild(self) -> None:
        if self.left_container is None or self.right_container is None:
            return

        self.left_container.clear()
        self.right_container.clear()
        node = self.state.get_selected_node()

        # Progress Board (left)
        with self.left_container:
            with ui.column().classes("w-full h-full"):
                ui.label("Progress Board").classes(
                    "text-sm font-bold px-3 py-1 text-blue-600 bg-blue-50 border-b shrink-0"
                )
                if not node:
                    ui.label("Select a node").classes("text-gray-400 italic p-4")
                else:
                    with ui.scroll_area().classes("w-full flex-grow"):
                        ui.textarea(
                            value=node.progress_board,
                            on_change=lambda e: self._update_board("progress_board", e.value),
                        ).classes("w-full min-h-full").props("outlined autogrow borderless")

        # Content Board (right)
        with self.right_container:
            with ui.column().classes("w-full h-full"):
                ui.label("Content Board").classes(
                    "text-sm font-bold px-3 py-1 text-green-600 bg-green-50 border-b shrink-0"
                )
                if not node:
                    ui.label("Select a node").classes("text-gray-400 italic p-4")
                else:
                    with ui.scroll_area().classes("w-full flex-grow"):
                        ui.textarea(
                            value=node.content_board,
                            on_change=lambda e: self._update_board("content_board", e.value),
                        ).classes("w-full min-h-full").props("outlined autogrow borderless")

    def _update_board(self, field: str, value: str) -> None:
        if self.state.selected_node_id:
            self.state.update_node_field(self.state.selected_node_id, field, value)
