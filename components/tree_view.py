from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from nicegui import ui

from models import ChildrenType, Status

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

CHILDREN_TYPE_LABELS: Dict[ChildrenType, str] = {
    ChildrenType.LEAF: "",
    ChildrenType.RRTD: "[R]",
    ChildrenType.DAPP: "[D]",
}


def build_tree_nodes(nodes: List[Any], state: "AppState") -> List[Dict[str, Any]]:
    """Convert Pydantic nodes to ui.tree format."""
    result = []
    for node in nodes:
        children_label = CHILDREN_TYPE_LABELS.get(node.children_type, "")
        tree_node = {
            "id": node.id,
            "label": node.name,
            "icon": NODE_ICONS.get(node.type, "circle"),
            "status_color": STATUS_COLORS.get(node.status, "#000000"),
            "children_label": children_label,
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
        with ui.column().classes("w-full h-full"):
            ui.button("+ Add Root Goal", on_click=self._on_add_root).classes(
                "m-2"
            ).props("flat color=primary")

            self.container = ui.column().classes("w-full flex-grow overflow-auto p-2")
            self._rebuild_tree()

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

            # Custom header slot for status colors and icons
            self.tree.add_slot(
                "default-header",
                """
                <div class="row items-center no-wrap">
                    <q-icon :name="props.node.icon" :style="{ color: props.node.status_color }" class="q-mr-xs" size="sm" />
                    <span :style="{ color: props.node.status_color }">
                        {{ props.node.label }}
                    </span>
                    <span v-if="props.node.children_label" class="q-ml-xs text-caption text-grey">
                        {{ props.node.children_label }}
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
