"""
Lifestyle Profile Core Engine (OS-Agnostic / Linux Standard)
Compliant with: 06_lifestyle_profile_memory_spec.md
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class FactEntry:
    fact_id: str
    category: str
    action: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    access_count: int = 1


@dataclass
class UserProfileSummary:
    action_frequencies: Dict[str, int]
    confidence_scores: Dict[str, float]
    permanent_facts: List[str]


class LifestyleProfileCore:
    """
    自律型ライフログ抽出・統計クラスタリングおよび忘却管理エンジン
    """

    # 昇格閾値・忘却パラメータ
    PROMOTION_FREQUENCY_THRESHOLD = 5
    PROMOTION_CONFIDENCE_THRESHOLD = 0.85
    DECAY_HALF_LIFE_SECONDS = 86400 * 7  # 半減期: 7日

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        event_emitter: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        self.base_dir = base_dir or Path(".")
        self.event_emitter = event_emitter or (lambda event: None)
        self.memory_store: Dict[str, FactEntry] = {}
        self.permanent_profile: Dict[str, Dict[str, Any]] = {}

    def ingest_fact(
        self,
        action: str,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
        current_time: Optional[float] = None,
    ) -> FactEntry:
        """
        対話から抽出された行動ファクトを取り込み、統計スコアを更新する
        """
        now = current_time if current_time is not None else time.time()
        meta = metadata or {}
        fact_id = f"fact_{action}_{int(now)}"

        if action in self.memory_store:
            entry = self.memory_store[action]
            entry.access_count += 1
            entry.timestamp = now
            entry.metadata.update(meta)
            entry.weight = min(2.0, entry.weight + 0.3)
        else:
            entry = FactEntry(
                fact_id=fact_id,
                category=category,
                action=action,
                timestamp=now,
                metadata=meta,
                weight=1.0,
                access_count=1,
            )
            self.memory_store[action] = entry

        # イベント通知
        event_payload = {
            "event_type": "EVENT_FACT_EXTRACTED",
            "timestamp": now,
            "fact_id": entry.fact_id,
            "category": entry.category,
            "action": entry.action,
            "access_count": entry.access_count,
            "metadata": entry.metadata,
        }
        self.event_emitter(event_payload)

        # 昇格判定
        self._evaluate_promotion(entry)
        return entry

    def _evaluate_promotion(self, entry: FactEntry) -> None:
        confidence = self.calculate_confidence(entry.action)
        if (
            entry.access_count >= self.PROMOTION_FREQUENCY_THRESHOLD
            or confidence >= self.PROMOTION_CONFIDENCE_THRESHOLD
        ):
            self.permanent_profile[entry.action] = {
                "action": entry.action,
                "category": entry.category,
                "confidence": confidence,
                "total_occurrences": entry.access_count,
                "status": "permanent_core_fact",
            }

    def calculate_confidence(self, action: str, current_time: Optional[float] = None) -> float:
        """
        頻度と減衰重みから嗜好確信度(0.0 ~ 1.0)を算出
        """
        if action not in self.memory_store:
            return 0.0
        now = current_time if current_time is not None else time.time()
        entry = self.memory_store[action]

        elapsed = max(0.0, now - entry.timestamp)
        decay = math.exp(-math.log(2) * (elapsed / self.DECAY_HALF_LIFE_SECONDS))
        effective_weight = entry.weight * decay

        score = 1.0 - math.exp(-0.35 * entry.access_count * effective_weight)
        return round(min(1.0, max(0.0, score)), 4)

    def get_profile_summary(self, current_time: Optional[float] = None) -> UserProfileSummary:
        now = current_time if current_time is not None else time.time()
        frequencies = {a: e.access_count for a, e in self.memory_store.items()}
        confidences = {a: self.calculate_confidence(a, current_time=now) for a in self.memory_store}
        permanent = list(self.permanent_profile.keys())
        return UserProfileSummary(
            action_frequencies=frequencies,
            confidence_scores=confidences,
            permanent_facts=permanent,
        )


if __name__ == "__main__":
    # 簡易単体検証
    engine = LifestyleProfileCore(event_emitter=lambda e: print(f"Event: {e['event_type']} -> {e['action']}"))
    
    # 5回キャンプへ行ったファクトを順次流し込む
    for i in range(5):
        engine.ingest_fact(action="camping", category="outdoor", metadata={"location": "hokkaido"})

    summary = engine.get_profile_summary()
    print("\n--- Profile Summary ---")
    print("Frequencies:", summary.action_frequencies)
    print("Confidence :", summary.confidence_scores)
    print("Permanent  :", summary.permanent_facts)