
### 1. `autonomous_temporal_inference_spec.md`（仕様書）

```markdown
# 自律型生活時間推論・文脈補正エンジン仕様書
# (Autonomous Temporal Lifestyle Inference & Contextual Guard Specification)

## 目次
- [1. 概要と目的](#1-概要と目的)
- [2. 自律推論アーキテクチャ](#2-自律推論アーキテクチャ)
- [3. コアロジック（暗黙的推定と時間差分照合）](#3-コアロジック暗黙的推定と時間差分照合)
- [4. データ構造定義](#4-データ構造定義)
- [5. 実装フェーズ](#5-実装フェーズ)
- [6. 実装リファレンス](#6-実装リファレンス)

---

## 1. 概要と目的
本モジュールは、ユーザーからの明示的な行動宣言（「お風呂に行く」等）の有無に関わらず、**「時刻（時間帯）」「無操作・無言の経過時間（$\Delta t$）」「過去の生活習慣プロファイル」**を照合し、現在のユーザーの行動状態を自律推論する。

時間経過を無視したLLMの文脈先走りや見当違いな応答を防止し、人間同様に「時間を察して自然に声をかける」パートナーシップを実現する。

---

## 2. 自律推論アーキテクチャ

```text
[現在時刻 / 無操作経過時間 (Δt) / 過去の習慣ログ]
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. 自律仮説生成 (Implicit State Estimator)                   │
│ - 時間帯（例: 20時）× 経過時間（例: 30分）から行動候補を算出 │
│ - 候補: [お風呂 (尤度 80%), 食事 (尤度 15%), 離席 (尤度 5%)]  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
[復帰シグナル検知 (入力 / カメラ / 操作)]
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 差分検証＆文脈決定 (Temporal Guard & Disambiguation)     │
│ - Δt が行動最小所要時間未満 ──▶ 未完了・短時間離席と判定    │
│ - Δt が標準所要時間レンジ内 ──▶ 該当行動の完了と推論        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 非表示プロンプト・インジェクション                       │
│ - 「お風呂上がりと推論されるため、温まったか気遣う応答を生成」│
└─────────────────────────────────────────────────────────────┘

```

---

## 3. コアロジック（暗黙的推定と時間差分照合）

1. **自律判定レンジ（Lifestyle Time Slots）**:

* **短時間離席（1〜10分）**: 飲み物調達、小休止 ➔ 普段通りの継続対話。
* **中時間離席（10〜45分）**: 入浴、軽食 ➔ 「あったまった？」「一服できた？」等の気遣い。
* **長時間離席（45分以上）**: 外出、仮眠 ➔ 「おかえり」等の帰還対応。

2. **早すぎる復帰の自動ツッコミ**:

* 明示宣言があった場合、$\Delta t$ が規定未満であれば自律的に「まだ入ってないでしょ！」と現実時間を指摘。

---

## 4. データ構造定義

```json
{
  "inference_version": "2.0.0",
  "temporal_delta_seconds": 2100,
  "inferred_activity": "bath",
  "confidence_score": 0.88,
  "guard_action": "ALLOW_COMPLETION_CONTEXT",
  "injected_prompt_directive": "ユーザーは夜の時間帯に約35分間離席していました。入浴後の可能性が高いため、自然に温まったか労うトーンで応答してください。"
}

```

---

## 5. 実装フェーズ

* **Phase 1**: 無操作時間と時間帯マトリクスによる自律行動推論エンジンの構築。
* **Phase 2**: 不可視プロンプト連携による文脈先走り防止ガードの実装。
* **Phase 3**: ユーザー固有の生活サイクルに合わせた所要時間レンジの自動学習。

---

## 6. 実装リファレンス

本仕様で定義された推論アルゴリズムの実動コードは、同ディレクトリ内の以下のファイルに格納されている。

* 実装コアファイル: [`autonomous_temporal_inference.py`](https://www.google.com/search?q=./autonomous_temporal_inference.py)
* 実行方法:
```powershell
python autonomous_temporal_inference.py

```



```

---

### 2. `autonomous_temporal_inference.py`（実装コード）

```python
"""
自律型生活時間推論・文脈補正エンジン (Autonomous Temporal Lifestyle Inference Engine)
Project Castella - Open Architecture Specification

対応仕様書: autonomous_temporal_inference_spec.md
概要: ユーザーの無操作経過時間と時間帯マトリクスから自律的に行動文脈を推論・補正する。
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

        # 1. 明示的宣言が存在する場合の厳密検証
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

        # 2. 宣言なしの自律推論（時間帯 × 無操作時間マトリクス）
        if idle_delta_sec < 60:
            return {
                "inferred_state": "continuous",
                "delta_sec": idle_delta_sec,
                "confidence": 0.99,
                "prompt_directive": ""
            }

        elif idle_delta_sec < self.SLOT_SHORT_BREAK_MAX:
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


if __name__ == "__main__":
    engine = AutonomousTemporalInference()

    # シミュレーション：宣言なしで夜に30分放置された後の復帰
    engine.last_interaction_time = time.time() - 1800  # 30分前
    result = engine.infer_context_on_return()

    print("=== 自律推論結果 ===")
    print("推論ステート:", result["inferred_state"])
    print("経過秒数:", result["delta_sec"])
    print("AI内部指示:", result["prompt_directive"])

```
