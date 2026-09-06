"""
context_slot_manager.py
Tier-2 Task Slot Context Controller for Autonomous LLM Agents

Description:
    A deterministic state controller designed to prevent task drift,
    hallucinations, and context loss in autonomous agent workflows.
    Maintains dual persistent slots (Master Spec & Execution Progress)
    with atomic persistence and lock mechanisms.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class ContextSlotManager:
    """Manages Tier-2 persistent task slots for LLM prompt injection."""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            self.storage_path = Path(__file__).resolve().parent / "data" / "task_slots.json"
        else:
            self.storage_path = Path(storage_path)

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.slots: Dict[str, Dict[str, Any]] = {
            "slot_a": {
                "name": "Master Specification",
                "locked": False,
                "content": "",
                "updated_at": None,
            },
            "slot_b": {
                "name": "Current Progress",
                "locked": False,
                "content": "",
                "updated_at": None,
            },
        }
        self.load()

    def _get_timestamp(self) -> str:
        return datetime.now().isoformat()

    def load(self) -> None:
        """Loads slot states from persistent storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.slots.update(data)
            except Exception as e:
                print(f"[ContextSlotManager] Warning: Failed to load storage ({e}). Using defaults.")

    def save(self) -> None:
        """Atomically saves slot states to prevent file corruption."""
        temp_path = self.storage_path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.slots, f, ensure_ascii=False, indent=2)
            temp_path.replace(self.storage_path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            print(f"[ContextSlotManager] Error: Failed to save storage ({e}).")

    def get_all_slots(self) -> Dict[str, Any]:
        """Returns the full state of all task slots."""
        return self.slots

    def get_slot(self, slot_key: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific slot by key ('slot_a' or 'slot_b')."""
        return self.slots.get(slot_key)

    def update_slot(
        self,
        slot_key: str,
        content: str,
        locked: bool = True,
        force_override: bool = False,
    ) -> bool:
        """Updates slot content and lock status."""
        if slot_key not in self.slots:
            return False

        current_slot = self.slots[slot_key]
        if current_slot["locked"] and not force_override and not locked:
            return False

        self.slots[slot_key]["content"] = content
        self.slots[slot_key]["locked"] = locked
        self.slots[slot_key]["updated_at"] = self._get_timestamp()
        self.save()
        return True

    def clear_slot(self, slot_key: str, force: bool = False) -> bool:
        """Clears slot content if unlocked or explicitly forced."""
        if slot_key not in self.slots:
            return False

        if self.slots[slot_key]["locked"] and not force:
            return False

        self.slots[slot_key] = {
            "name": self.slots[slot_key]["name"],
            "locked": False,
            "content": "",
            "updated_at": self._get_timestamp(),
        }
        self.save()
        return True

    def render_prompt_injection(self) -> str:
        """
        Builds a structured Tier-2 context block ready for prompt injection.
        Skips empty slots automatically.
        """
        slot_a_content = self.slots["slot_a"]["content"].strip()
        slot_b_content = self.slots["slot_b"]["content"].strip()

        if not slot_a_content and not slot_b_content:
            return ""

        lines = ["\n[ACTIVE TASK CONTEXT]"]
        if slot_a_content:
            lines.append(f"■ Master Specification:\n{slot_a_content}")
        if slot_b_content:
            lines.append(f"■ Current Execution Step:\n{slot_b_content}")
        lines.append("[END OF ACTIVE TASK CONTEXT]\n")

        return "\n".join(lines)


if __name__ == "__main__":
    manager = ContextSlotManager()

    manager.update_slot(
        "slot_a",
        "Implement a modular 3-tier context management pipeline for LLM agents.",
        locked=True,
    )
    manager.update_slot(
        "slot_b",
        "Perform unit testing on ContextSlotManager.",
        locked=True,
    )

    print("--- Rendered Prompt Injection ---")
    print(manager.render_prompt_injection())