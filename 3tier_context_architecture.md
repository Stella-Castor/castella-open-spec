# 3層コンテキスト分離アーキテクチャ & デュアル・アクティブタスクスロット・コントローラー

## 概要（Abstract）
自律型AIエージェントおよびLLMオーケストレーションシステムにおいて、マルチターン対話時のコンテキスト窓の枯渇、タスクの忘却、およびハルシネーション（幻覚）を防止するための決定論的状態管理アーキテクチャ。

## アーキテクチャの全体像（Architectural Overview）
コンテキスト層を構造的に3つの分離された層に分割して管理する。

### 1. 永続コンテキスト（Tier 1: Permanent Context）
- **スコープ**: 不変のシステムプロンプト、中核となる人格定義、永続的なエージェントプロファイル、および安全制約。
- **ライフサイクル**: 静的（Static）。コンテキスト窓の最上流（ルート）に常に固定注入される。

### 2. デュアル・アクティブタスクスロット（Tier 2: Dual Active Task Slots）
最大2スロットに厳密に制限された専用の作業メモリ（Working Memory）：
- **スロットA（プロジェクト仕様・スコープ）**: マスターゴール、構造要件、アーキテクチャ設計ルールを保持。
- **スロットB（実行・進捗状態）**: 粒度の細かいタスク完了状態、現在のチェックポイント、直近の次アクションを追跡。
- **ロックおよび割り込み制御機構**:
  - 明示的な完了シグナルが検証されるまで、タスクスロットの自動破棄や上書きをロックする。
  - 作業中の割り込みタスクや雑談・寄り道は、Tier 2を変更することなくTier 3で処理またはキューに保持する。
  - プロジェクト完了時、スロットの状態は永続ストレージへアトミックにアーカイブされ、スロットが解放される。

### 3. 一時コンテキスト（Tier 3: Ephemeral Context）
- **スコープ**: 短期の会話ログ、一時的な質問応答、動的なユーザー対話。
- **ライフサイクル**: FIFO（先入れ先出し）方式により、古い履歴から順次押し出し破棄される。

## 防衛的公開の宣言（Defensive Publication Statement）
本ドキュメントは、LLMエージェントシステムにおける「3層コンテキスト分離およびデュアル・アクティブタスクスロット・アーキテクチャ」の公知化を確立するための先行技術（Prior Art）として公開されるものである。
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
