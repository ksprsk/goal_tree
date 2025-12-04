from __future__ import annotations

from typing import Optional

from nicegui import ui

from models import ChildrenType


async def show_children_type_dialog() -> Optional[ChildrenType]:
    """Show dialog to let user choose between RRTD and DAPP children type."""
    result: dict[str, Optional[ChildrenType]] = {"value": None}

    with ui.dialog() as dialog, ui.card().classes("p-6"):
        ui.label("Choose Children Type").classes("text-lg font-bold mb-2")
        ui.label("This choice is permanent for this node.").classes(
            "text-sm text-gray-500 mb-4"
        )

        def select_rrtd() -> None:
            result["value"] = ChildrenType.RRTD
            dialog.close()

        def select_dapp() -> None:
            result["value"] = ChildrenType.DAPP
            dialog.close()

        with ui.row().classes("gap-4 w-full justify-center"):
            with ui.card().classes(
                "p-4 cursor-pointer hover:bg-blue-50 text-center"
            ).on("click", select_rrtd):
                ui.icon("account_tree", size="lg", color="blue")
                ui.label("RRTD").classes("font-bold text-blue-600")
                ui.label("Subgoals / Bottlenecks").classes("text-sm text-gray-600")
                ui.label("Children will be Base nodes").classes("text-xs text-gray-400")

            with ui.card().classes(
                "p-4 cursor-pointer hover:bg-purple-50 text-center"
            ).on("click", select_dapp):
                ui.icon("alt_route", size="lg", color="purple")
                ui.label("DAPP").classes("font-bold text-purple-600")
                ui.label("Scenarios / Strategies").classes("text-sm text-gray-600")
                ui.label("With ATP/Signposts/Triggers").classes("text-xs text-gray-400")

        ui.button("Cancel", on_click=dialog.close).props("flat").classes("mt-4")

    dialog.open()
    await dialog
    return result["value"]
