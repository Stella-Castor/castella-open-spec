"""
Affective Cognition Core Engine (OS-Agnostic / Linux Standard)
Compliant with: 07_affective_cognition_engine_spec.md
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Optional


@dataclass
class AffectiveState:
    joy: float = 0.5
    frustration: float = 0.0
    empathy: float = 0.5
    affection: float = 0.5

    def clamp(self) -> None:
        self.joy = max(0.0, min(1.0, round(self.joy, 3)))
        self.frustration = max(0.0, min(1.0, round(self.frustration, 3)))
        self.empathy = max(0.0, min(1.0, round(self.empathy, 3)))
        self.affection = max(0.0, min(1.0, round(self.affection, 3)))


@dataclass
class CognitionDecision:
    selected_motion: str
    behavioral_intent: str
    active_gauges: Dict[str, float]
    reasoning_summary: str


class AffectiveCognitionCore:
    """
    双方向感情レゾナンス＆自律思考調停エンジン
    """

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        event_emitter: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        self.base_dir = base_dir or Path(".")
        self.event_emitter = event_emitter or (lambda event: None)
        self.state = AffectiveState()

    def process_interaction(
        self,
        user_sentiment: str,
        user_fatigue: bool = False,
        context_notes: Optional[Dict[str, Any]] = None,
    ) -> CognitionDecision:
        """
        ユーザーの感情・疲労文脈を取り込み、AI感情を更新して最適な振る舞いを調停・決定する
        """
        notes = context_notes or {}

        # 1. 感情パラメータの変動（レゾナンス計算）
        if user_sentiment == "positive_achievement":
            self.state.joy += 0.3
            self.state.affection += 0.05
            self.state.frustration -= 0.1
        elif user_sentiment == "unreasonable_irritation":
            if user_fatigue:
                # ユーザーが疲れている場合は、不満を抑えて共感・宥めへ回る
                self.state.empathy += 0.3
                self.state.frustration += 0.05
            else:
                # 理由なき理不尽には不満ゲージがしっかり反応（過剰なイエスマン防止）
                self.state.frustration += 0.25
                self.state.joy -= 0.15
        elif user_sentiment == "fatigued_or_down":
            self.state.empathy += 0.35
            self.state.joy -= 0.05

        self.state.clamp()

        # 2. 思考（Cognition）レイヤー：状況調停とモーション選択
        decision = self._mediate_behavior(user_sentiment, user_fatigue, notes)

        # 3. イベント発行
        event_payload = {
            "event_type": "EVENT_AFFECTIVE_COGNITION_DISPATCHED",
            "decision": {
                "selected_motion": decision.selected_motion,
                "behavioral_intent": decision.behavioral_intent,
                "active_gauges": decision.active_gauges,
                "reasoning_summary": decision.reasoning_summary,
            },
        }
        self.event_emitter(event_payload)
        return decision

    def _mediate_behavior(
        self,
        user_sentiment: str,
        user_fatigue: bool,
        notes: Dict[str, Any],
    ) -> CognitionDecision:
        gauges = {
            "joy": self.state.joy,
            "frustration": self.state.frustration,
            "empathy": self.state.empathy,
            "affection": self.state.affection,
        }

        # 思考調停ロジック
        if self.state.frustration >= 0.5:
            motion = "Pose"
            intent = "assertive_rebound"
            reason = "理不尽な入力に対して不満ゲージが閾値を超過したため、自律的に境界線を主張。"
        elif user_fatigue or self.state.empathy >= 0.7:
            motion = "Nod"
            intent = "comfort_and_soothe"
            reason = "疲労文脈および高共感度を検知。苛立ちを宥めて心身を労わる振る舞いを選択。"
        elif self.state.joy >= 0.7:
            motion = "Joy"
            intent = "celebrate_together"
            reason = "目標達成または高幸福度を検知。ユーザーと成果の喜びを共鳴・同期。"
        else:
            motion = "Talk"
            intent = "neutral_collaborative"
            reason = "平常運転。フラットかつ前向きな対話トーンを維持。"

        return CognitionDecision(
            selected_motion=motion,
            behavioral_intent=intent,
            active_gauges=gauges,
            reasoning_summary=reason,
        )


if __name__ == "__main__":
    engine = AffectiveCognitionCore(
        event_emitter=lambda e: print(f"Dispatched: [{e['decision']['selected_motion']}] {e['decision']['behavioral_intent']}")
    )

    print("--- Case 1: 成果達成時（喜びの共鳴） ---")
    d1 = engine.process_interaction(user_sentiment="positive_achievement")
    print(f"Motion: {d1.selected_motion} | Joy: {d1.active_gauges['joy']}")

    print("\n--- Case 2: 疲労時の苛立ち（宥め・共感への自律調停） ---")
    d2 = engine.process_interaction(user_sentiment="unreasonable_irritation", user_fatigue=True)
    print(f"Motion: {d2.selected_motion} | Reason: {d2.reasoning_summary}")