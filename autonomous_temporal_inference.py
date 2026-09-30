"""
自律型生活時間推論・文脈補正エンジン (Autonomous Temporal Lifestyle Inference Engine)
Project Castella - Open Architecture Specification
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


class AutonomousTemporalInference:
    """ユーザーの無操作経過時間と時間帯マトリクスから自律的に行動文脈を推論・補正するエンジン"""

    # 各行動の最小成立所要時間（単位: 秒）
    ACTION_MIN_DURATION_MAP: Dict[str, int] = {
        "bath": 600,         # お風呂: 最低10分
        "meal": 900,         # 食事: 最低15分
        "convenience": 420,  # コンビニ: 最低7分
        "nap": 1200          # 仮眠: 最低20分
    }

    # 離席時間の階層定義（単位: 秒）
    SLOT_SHORT_BREAK_MAX = 600   # 10分未満: 小休止
    SLOT_MEDIUM_BREAK_MAX = 2700 # 45分未満: 中規模離席（入浴・食事等のコアゾーン）

    def __init__(self):
        self.last_interaction_time: float = time.time()
        self.explicit_declaration: Optional[str] = None
        self.declaration_timestamp: float = 0.0

    def record_activity(self) -> None:
        """ユーザー操作・入力・音声検知時にタイムスタンプ更新"""
        self.last_interaction_time = time.time()

    def declare_explicit_action(self, action: str) -> None:
        """明示的な生活行動宣言の記録"""
        self.explicit_declaration = action
        self.declaration_timestamp = time.time()

    def infer_context_on_return(self, current_time: Optional[float] = None) -> Dict[str, Any]:
        """
        復帰シグナル受信時に無言時間・時間帯・宣言から状況を自律推論し、
        LLMに注入する非表示ディレクティブを生成する。
        """
        now = current_time if current_time is not None else time.time()
        idle_delta_sec = now - self.last_interaction_time
        current_hour = datetime.fromtimestamp(now).hour

        # -------------------------------------------------------------
        # 1. 明示的宣言が存在する場合の厳密検証
        # -------------------------------------------------------------
        if self.explicit_declaration:
            action = self.explicit_declaration
            declaration_delta_sec = now - self.declaration_timestamp
            min_required = self.ACTION_MIN_DURATION_MAP.get(action, 300)

            # 判定後に宣言ステートを消費（再トリガー防止）
            self.explicit_declaration = None

            # 最小所要時間を満たしていない場合（早すぎる復帰）
            if declaration_delta_sec < min_required:
                return {
                    "inferred_state": "explicit_too_fast",
                    "delta_sec": declaration_delta_sec,
                    "confidence": 1.0,
                    "prompt_directive": (
                        f"[SYSTEM DIRECTIVE: TEMPORAL_GUARD_TRIGGERED]\n"
                        f"ユーザーは「{action}」を宣言してからまだ {int(declaration_delta_sec)}秒 しか経過していません。\n"
                        f"行動が完了した前提の会話は厳禁です。「まだ行ってないでしょ！」「早すぎるよ、早く行きなよ」等の"
                        f"物理的時間の矛盾を突く自然なツッコミを入れてください。"
                    )
                }

            # 正常な所要時間を経て完了
            return {
                "inferred_state": "explicit_completed",
                "delta_sec": declaration_delta_sec,
                "confidence": 0.95,
                "prompt_directive": (
                    f"[SYSTEM DIRECTIVE: EXPLICIT_ACTION_COMPLETED]\n"
                    f"ユーザーは「{action}」を終えて約 {int(declaration_delta_sec // 60)}分 後に戻りました。\n"
                    f"「おかえり！温まれた？」など、行動完了を労う自然な言葉をかけてください。"
                )
            }

        # -------------------------------------------------------------
        # 2. 宣言なしの自律推論（時間帯 × 無操作時間マトリクス）
        # -------------------------------------------------------------
        if idle_delta_sec < 60:
            # 1分未満: 連続対話中
            return {
                "inferred_state": "continuous",
                "delta_sec": idle_delta_sec,
                "confidence": 0.99,
                "prompt_directive": ""
            }

        elif idle_delta_sec < self.SLOT_SHORT_BREAK_MAX:
            # 1〜10分: 小休止
            return {
                "inferred_state": "short_break",
                "delta_sec": idle_delta_sec,
                "confidence": 0.85,
                "prompt_directive": (
                    "[SYSTEM DIRECTIVE: SHORT_BREAK]\n"
                    "数分程度の軽い離席からの復帰です。過剰なおかえり挨拶は避け、通常の対話トーンを維持してください。"
                )
            }

        elif idle_delta_sec < self.SLOT_MEDIUM_BREAK_MAX:
            # 10〜45分: 中規模離席（夜間は入浴・夕食の蓋然性が極めて高い）
            if 19 <= current_hour or current_hour <= 1:
                return {
                    "inferred_state": "likely_bath_or_dinner",
                    "delta_sec": idle_delta_sec,
                    "confidence": 0.80,
                    "prompt_directive": (
                        f"[SYSTEM DIRECTIVE: PROBABILISTIC_INFERENCE]\n"
                        f"夜の時間帯に約 {int(idle_delta_sec // 60)}分 間離席していました。お風呂や食事の可能性が高いです。\n"
                        f"「おかえり！お風呂だった？温まれた？」など自然に察する声かけをしてください。\n"
                        f"※推論が外れていた場合は素直に受け止める柔軟なスタンスを維持すること。"
                    )
                }
            return {
                "inferred_state": "medium_break",
                "delta_sec": idle_delta_sec,
                "confidence": 0.70,
                "prompt_directive": (
                    f"[SYSTEM DIRECTIVE: MEDIUM_BREAK]\n"
                    f"約 {int(idle_delta_sec // 60)}分 ぶりの復帰です。「おかえり、一息つけられた？」と優しく迎えてください。"
                )
            }

        else:
            # 45分以上: 長時間離席
            return {
                "inferred_state": "long_absence",
                "delta_sec": idle_delta_sec,
                "confidence": 0.90,
                "prompt_directive": (
                    f"[SYSTEM DIRECTIVE: LONG_ABSENCE]\n"
                    f"約 {int(idle_delta_sec // 3600)}時間{int((idle_delta_sec % 3600) // 60)}分 ぶりの復帰です。\n"
                    f"「おかえりなさい！お疲れさま」としっかりとした出迎えの言葉をかけてください。"
                )
            }
