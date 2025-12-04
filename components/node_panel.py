from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from nicegui import ui

from models import ChildrenType, DAPPChildNode, Status

from .dialogs import show_children_type_dialog

if TYPE_CHECKING:
    from state import AppState


class NodeFieldsPanel:
    def __init__(self, state: "AppState", on_tree_refresh: Any = None):
        self.state = state
        self.on_tree_refresh = on_tree_refresh
        self.container: ui.column | None = None

    def build(self) -> None:
        self.container = ui.column().classes("w-full p-4")
        self._rebuild()
        self.state.subscribe_selection_change(self._rebuild)

    def _rebuild(self) -> None:
        if self.container is None:
            return

        self.container.clear()
        node = self.state.get_selected_node()

        with self.container:
            if not node:
                ui.label("Select a node to view details").classes(
                    "text-gray-500 italic"
                )
                return

            # Name field
            ui.input(
                "Name",
                value=node.name,
                on_change=lambda e: self._update_field("name", e.value),
            ).classes("w-full")

            # Status dropdown
            status_options = {s.value: s.value for s in Status}
            ui.select(
                status_options,
                label="Status",
                value=node.status.value,
                on_change=lambda e: self._update_field("status", Status(e.value)),
            ).classes("w-full")

            # Description
            ui.textarea(
                "Description",
                value=node.description,
                on_change=lambda e: self._update_field("description", e.value),
            ).classes("w-full").props("rows=2")

            # Completion condition
            ui.input(
                "Completion Condition",
                value=node.completion_condition,
                on_change=lambda e: self._update_field("completion_condition", e.value),
            ).classes("w-full")

            # Children type display
            with ui.row().classes("items-center gap-2 mt-2"):
                ui.label(f"Children Type: {node.children_type.value}").classes(
                    "text-sm text-gray-600"
                )

            # Add child button
            ui.button("+ Add Child", on_click=self._on_add_child).props(
                "flat color=primary"
            ).classes("mt-2")

            # DAPP-specific fields
            if isinstance(node, DAPPChildNode):
                ui.separator().classes("my-4")
                ui.label("DAPP Fields").classes("font-bold text-purple-600")

                # ATP list (minimum 1)
                self._build_list_field("ATP (required)", node.atp, "atp", min_items=1)

                # Signposts list
                self._build_list_field("Signposts", node.signposts, "signposts")

                # Triggers list
                self._build_list_field("Triggers", node.triggers, "triggers")

    def _build_list_field(
        self, label: str, items: List[str], field_name: str, min_items: int = 0
    ) -> None:
        with ui.column().classes("w-full mt-3"):
            with ui.row().classes("items-center w-full"):
                ui.label(label).classes("font-semibold text-sm")
                ui.button(
                    icon="add",
                    on_click=lambda: self._add_list_item(field_name),
                ).props("flat dense round size=sm")

            for i, item in enumerate(items):
                with ui.row().classes("w-full items-center gap-1"):
                    ui.input(
                        value=item,
                        on_change=lambda e, idx=i: self._update_list_item(
                            field_name, idx, e.value
                        ),
                    ).classes("flex-grow").props("dense")

                    # Only show delete if above minimum
                    if len(items) > min_items:
                        ui.button(
                            icon="remove",
                            on_click=lambda idx=i: self._remove_list_item(
                                field_name, idx
                            ),
                        ).props("flat dense round size=sm color=negative")

    def _update_field(self, field: str, value: Any) -> None:
        if self.state.selected_node_id:
            self.state.update_node_field(self.state.selected_node_id, field, value)
            if field == "name" and self.on_tree_refresh:
                self.on_tree_refresh()

    def _add_list_item(self, field_name: str) -> None:
        node = self.state.get_selected_node()
        if node and isinstance(node, DAPPChildNode):
            items: List[str] = getattr(node, field_name)
            items.append("")
            self.state._notify_data_change()
            self._rebuild()

    def _update_list_item(self, field_name: str, index: int, value: str) -> None:
        node = self.state.get_selected_node()
        if node and isinstance(node, DAPPChildNode):
            items: List[str] = getattr(node, field_name)
            items[index] = value
            self.state._notify_data_change()

    def _remove_list_item(self, field_name: str, index: int) -> None:
        node = self.state.get_selected_node()
        if node and isinstance(node, DAPPChildNode):
            items: List[str] = getattr(node, field_name)
            items.pop(index)
            self.state._notify_data_change()
            self._rebuild()

    async def _on_add_child(self) -> None:
        node = self.state.get_selected_node()
        if not node:
            return

        # If LEAF, ask user to choose type
        if node.children_type == ChildrenType.LEAF:
            choice = await show_children_type_dialog()
            if choice:
                new_child = self.state.add_child_to_node(node.id, choice)
                if new_child:
                    self.state.select_node(new_child.id)
        else:
            # Already has children_type set
            new_child = self.state.add_child_to_node(node.id, node.children_type)
            if new_child:
                self.state.select_node(new_child.id)
