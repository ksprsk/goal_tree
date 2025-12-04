from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models import AppData


class JsonStorage:
    def __init__(self, file_path: str = "data.json", debounce_ms: int = 500):
        self.file_path = Path(file_path)
        self.debounce_ms = debounce_ms
        self._save_task: Optional[asyncio.Task] = None
        self._pending_data: Optional[AppData] = None

    def load(self) -> "AppData":
        """Load data from JSON file, return empty AppData if file doesn't exist."""
        from models import AppData

        if not self.file_path.exists():
            return AppData()

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AppData.model_validate(data)

    def _write_sync(self, data: "AppData") -> None:
        """Synchronous write to file."""
        data.last_modified = datetime.utcnow()
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

    async def _debounced_save(self) -> None:
        """Wait for debounce period then save."""
        try:
            await asyncio.sleep(self.debounce_ms / 1000.0)
            if self._pending_data:
                self._write_sync(self._pending_data)
                self._pending_data = None
        except asyncio.CancelledError:
            pass

    def save(self, data: "AppData") -> None:
        """Schedule a debounced save operation."""
        self._pending_data = data

        # Cancel any pending save task
        if self._save_task and not self._save_task.done():
            self._save_task.cancel()

        # Schedule new save
        try:
            loop = asyncio.get_running_loop()
            self._save_task = loop.create_task(self._debounced_save())
        except RuntimeError:
            # No running loop, save immediately
            self._write_sync(data)

    def save_immediate(self, data: "AppData") -> None:
        """Save immediately without debouncing."""
        self._write_sync(data)
