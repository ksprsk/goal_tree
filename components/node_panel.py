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
        # Compact layout for bottom panel - 2 rows
        self.container = ui.column().classes("w-full p-2 gap-1 overflow-auto")
        self._rebuild()
        self.state.subscribe_selection_change(self._rebuild)

    def _rebuild(self) -> None:
        if self.container is None:
            return

        self.container.clear()
        node = self.state.get_selected_node()

        with self.container:
            if not node:
                ui.label("Select a node").classes("text-gray-400 italic")
                return

            # Main layout: Left (basic fields, 60%) | Right (DAPP fields, 40%, only for DAPP_Child)
            is_dapp = isinstance(node, DAPPChildNode)
            with ui.row().classes("w-full h-full gap-4"):
                # Left side: Basic node fields (60% when DAPP, 100% otherwise)
                left_class = "flex-[6] gap-1" if is_dapp else "flex-1 gap-1"
                with ui.column().classes(left_class):
                    # Row 1: Name (flex) | +child (fixed) | Status (fixed)
                    with ui.row().classes("w-full items-center gap-2"):
                        ui.input(
                            "Name",
                            value=node.name,
                            on_change=lambda e: self._update_field("name", e.value),
                        ).classes("flex-1 min-w-0").props("dense")

                        ui.button("+ child", on_click=self._on_add_child).props(
                            "flat dense color=primary size=sm"
                        )

                        status_options = {s.value: s.value for s in Status}
                        ui.select(
                            status_options,
                            label="Status",
                            value=node.status.value,
                            on_change=lambda e: self._update_field("status", Status(e.value)),
                        ).classes("w-28").props("dense")

                    # Row 2: Description (1 line default, expandable)
                    ui.textarea(
                        "Description",
                        value=node.description,
                        on_change=lambda e: self._update_field("description", e.value),
                    ).classes("w-full").props("dense rows=1 autogrow")

                    # Row 3: Completion condition (1 line default, expandable)
                    ui.textarea(
                        "Completion condition",
                        value=node.completion_condition,
                        on_change=lambda e: self._update_field("completion_condition", e.value),
                    ).classes("w-full").props("dense rows=1 autogrow")

                # Right side: DAPP fields (40%, only for DAPP_Child nodes)
                if is_dapp:
                    with ui.column().classes("flex-[4] gap-2 border-l pl-4"):
                        ui.label("DAPP").classes("text-sm font-bold text-purple-600")
                        # ATP (required, min 1)
                        self._build_dapp_list("ATP", node.atp, "atp", min_items=1)
                        # Signposts
                        self._build_dapp_list("Signpost", node.signposts, "signposts", min_items=0)
                        # Triggers
                        self._build_dapp_list("Trigger", node.triggers, "triggers", min_items=0)

    def _build_dapp_list(
        self, label: str, items: List[str], field_name: str, min_items: int = 0
    ) -> None:
        with ui.column().classes("w-full gap-1"):
            with ui.row().classes("items-center gap-1"):
                ui.label(label).classes("text-xs text-purple-600 font-bold")
                ui.button(
                    icon="add",
                    on_click=lambda fn=field_name: self._add_list_item(fn),
                ).props("flat dense round size=xs color=purple")

            if not items:
                ui.label("(empty)").classes("text-xs text-gray-400 italic")
            else:
                for i, item in enumerate(items):
                    with ui.row().classes("w-full items-center gap-1"):
                        ui.input(
                            value=item,
                            on_change=lambda e, fn=field_name, idx=i: self._update_list_item(fn, idx, e.value),
                        ).classes("flex-1").props("dense")

                        # Show delete button if above minimum
                        if len(items) > min_items:
                            ui.button(
                                icon="close",
                                on_click=lambda fn=field_name, idx=i: self._remove_list_item(fn, idx),
                            ).props("flat dense round size=xs color=negative")

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
            self.state._save_only()
            self._rebuild()

    def _update_list_item(self, field_name: str, index: int, value: str) -> None:
        node = self.state.get_selected_node()
        if node and isinstance(node, DAPPChildNode):
            items: List[str] = getattr(node, field_name)
            items[index] = value
            self.state._save_only()

    def _remove_list_item(self, field_name: str, index: int) -> None:
        node = self.state.get_selected_node()
        if node and isinstance(node, DAPPChildNode):
            items: List[str] = getattr(node, field_name)
            items.pop(index)
            self.state._save_only()
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
