from __future__ import annotations

from typing import TYPE_CHECKING

from nicegui import ui

if TYPE_CHECKING:
    from state import AppState


class BoardsPanel:
    def __init__(self, state: "AppState"):
        self.state = state
        self.container: ui.row | None = None

    def build(self) -> None:
        self.container = ui.row().classes("w-full h-full gap-4 p-4")
        self._rebuild()
        self.state.subscribe_selection_change(self._rebuild)

    def _rebuild(self) -> None:
        if self.container is None:
            return

        self.container.clear()
        node = self.state.get_selected_node()

        with self.container:
            if not node:
                ui.label("Select a node to view boards").classes(
                    "text-gray-500 italic w-full text-center"
                )
                return

            # Progress Board (50% width)
            with ui.column().classes("w-1/2"):
                ui.label("Progress Board").classes("font-bold text-blue-600 mb-2")
                ui.textarea(
                    value=node.progress_board,
                    on_change=lambda e: self._update_board("progress_board", e.value),
                ).classes("w-full").props("outlined rows=12")

            # Content Board (50% width)
            with ui.column().classes("w-1/2"):
                ui.label("Content Board").classes("font-bold text-green-600 mb-2")
                ui.textarea(
                    value=node.content_board,
                    on_change=lambda e: self._update_board("content_board", e.value),
                ).classes("w-full").props("outlined rows=12")

    def _update_board(self, field: str, value: str) -> None:
        if self.state.selected_node_id:
            self.state.update_node_field(self.state.selected_node_id, field, value)
