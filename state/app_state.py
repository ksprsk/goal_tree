from __future__ import annotations

from typing import Callable, List, Optional, Set, Union

from models import AppData, BaseNode, ChildrenType, DAPPChildNode
from persistence import JsonStorage

NodeType = Union[BaseNode, DAPPChildNode]


class AppState:
    def __init__(self, storage: JsonStorage):
        self.storage = storage
        self.data: AppData = storage.load()
        self.selected_node_id: Optional[str] = None
        self.expanded_nodes: Set[str] = set()

        # Callbacks for UI updates
        self._on_data_change: List[Callable[[], None]] = []
        self._on_selection_change: List[Callable[[], None]] = []

    def subscribe_data_change(self, callback: Callable[[], None]) -> None:
        self._on_data_change.append(callback)

    def subscribe_selection_change(self, callback: Callable[[], None]) -> None:
        self._on_selection_change.append(callback)

    def _notify_data_change(self) -> None:
        for cb in self._on_data_change:
            cb()
        self.storage.save(self.data)

    def _notify_selection_change(self) -> None:
        for cb in self._on_selection_change:
            cb()

    def find_node_by_id(self, node_id: str) -> Optional[NodeType]:
        """Traverse tree to find node by ID."""

        def search(nodes: List[NodeType]) -> Optional[NodeType]:
            for node in nodes:
                if node.id == node_id:
                    return node
                result = search(node.children)
                if result:
                    return result
            return None

        return search(self.data.roots)

    def get_selected_node(self) -> Optional[NodeType]:
        if not self.selected_node_id:
            return None
        return self.find_node_by_id(self.selected_node_id)

    def select_node(self, node_id: Optional[str]) -> None:
        self.selected_node_id = node_id
        self._notify_selection_change()

    def toggle_expanded(self, node_id: str) -> None:
        if node_id in self.expanded_nodes:
            self.expanded_nodes.discard(node_id)
        else:
            self.expanded_nodes.add(node_id)

    def add_root_node(self, name: str = "New Goal") -> BaseNode:
        node = BaseNode(name=name)
        self.data.roots.append(node)
        self._notify_data_change()
        return node

    def add_child_to_node(
        self, parent_id: str, children_type: ChildrenType
    ) -> Optional[NodeType]:
        parent = self.find_node_by_id(parent_id)
        if not parent:
            return None

        # Set children_type if this is first child (was LEAF)
        if parent.children_type == ChildrenType.LEAF:
            parent.children_type = children_type

        # Create appropriate child type
        if parent.children_type == ChildrenType.RRTD:
            child: NodeType = BaseNode(name="New Subgoal")
        else:  # DAPP
            child = DAPPChildNode(name="New Strategy", atp=[""])

        parent.children.append(child)
        self.expanded_nodes.add(parent_id)  # Auto-expand parent
        self._notify_data_change()
        return child

    def update_node_field(self, node_id: str, field: str, value: object) -> None:
        node = self.find_node_by_id(node_id)
        if node and hasattr(node, field):
            setattr(node, field, value)
            self._notify_data_change()
