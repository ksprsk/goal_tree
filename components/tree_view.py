from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from nicegui import ui

from models import Status

if TYPE_CHECKING:
    from state import AppState

STATUS_COLORS: Dict[Status, str] = {
    Status.IN_PROGRESS: "#2196F3",  # blue
    Status.COMPLETED: "#4CAF50",  # green
    Status.ON_HOLD: "#9E9E9E",  # gray
    Status.CANCELLED: "#BDBDBD",  # light gray
    Status.FAILED: "#F44336",  # red
}

NODE_ICONS: Dict[str, str] = {
    "Base": "radio_button_checked",
    "DAPP_Child": "change_history",
}


def build_tree_nodes(nodes: List[Any], state: "AppState") -> List[Dict[str, Any]]:
    """Convert Pydantic nodes to ui.tree format."""
    result = []
    for node in nodes:
        tree_node = {
            "id": node.id,
            "label": node.name,
            "icon": NODE_ICONS.get(node.type, "circle"),
            "status_color": STATUS_COLORS.get(node.status, "#000000"),
            "created_time": node.created_at.strftime("%H:%M"),
            "updated_time": node.updated_at.strftime("%H:%M"),
            "children": build_tree_nodes(node.children, state) if node.children else [],
        }
        result.append(tree_node)
    return result


class TreeViewComponent:
    def __init__(self, state: "AppState"):
        self.state = state
        self.tree: ui.tree | None = None
        self.container: ui.column | None = None

    def build(self) -> None:
        # Everything in one scroll area so button follows tree content
        with ui.scroll_area().classes("w-full h-full"):
            with ui.column().classes("w-full gap-0"):
                self.container = ui.column().classes("w-full gap-0")
                self._rebuild_tree()

                # Button right after tree content (like a new node)
                ui.button("+ Add Root", on_click=self._on_add_root).classes(
                    "ml-4 mt-1"
                ).props("flat dense color=primary size=sm")

    def _rebuild_tree(self) -> None:
        if self.container is None:
            return

        self.container.clear()
        with self.container:
            nodes = build_tree_nodes(self.state.data.roots, self.state)
            if not nodes:
                ui.label("No goals yet. Click '+ Add Root Goal' to start.").classes(
                    "text-gray-500 italic"
                )
                return

            self.tree = (
                ui.tree(
                    nodes,
                    label_key="label",
                    children_key="children",
                    node_key="id",
                    on_select=self._on_node_select,
                )
                .props("no-selection-unset")
                .classes("w-full")
            )

            # Custom header slot: Icon Name ... HH:MM HH:MM (times on right, fixed width)
            self.tree.add_slot(
                "default-header",
                """
                <div style="display: flex; align-items: center; width: 100%; font-size: 12px; overflow: hidden;">
                    <q-icon :name="props.node.icon" :style="{ color: props.node.status_color }" size="16px" style="flex-shrink: 0; margin-right: 4px;" />
                    <span :style="{ color: props.node.status_color }" style="flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        {{ props.node.label }}
                    </span>
                    <span class="text-grey-5" style="flex-shrink: 0; font-family: monospace; font-size: 10px; margin-left: 4px;">
                        {{ props.node.created_time }} {{ props.node.updated_time }}
                    </span>
                </div>
                """,
            )

            # Set expanded state
            if self.state.expanded_nodes:
                self.tree.props["expanded"] = list(self.state.expanded_nodes)
            self.tree.on("update:expanded", self._on_expand_change)

            # Set selected node if any
            if self.state.selected_node_id:
                self.tree.props["selected"] = self.state.selected_node_id

    def _on_node_select(self, e: Any) -> None:
        node_id = e.value if e.value else None
        self.state.select_node(node_id)

    def _on_expand_change(self, e: Any) -> None:
        self.state.expanded_nodes = set(e.args)

    def _on_add_root(self) -> None:
        node = self.state.add_root_node()
        self.state.select_node(node.id)

    def refresh(self) -> None:
        self._rebuild_tree()
