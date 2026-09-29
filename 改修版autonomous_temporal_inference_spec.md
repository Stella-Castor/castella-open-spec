---

### 自律型・生活時間推論の設計思想

1. **暗黙的なコンテキスト推定（無言時間の自律解釈）**
* 宣言がなくても、「平日20時前後に30分以上の無操作」が発生した場合、過去の習慣（エピソード記憶）から「お風呂に入っている可能性が高い」と自律的に仮説を立てる。


2. **復帰トリガー時の動的文脈判定**
* 再び操作や発話があった際、経過時間に応じて推論を確定させる。
* **例（無言で消えて35分後に戻った場合）**:
「おかえり。時間的にお風呂入ってた？ あったまった？」と自然に推論して声をかける。


3. **早すぎる介入の自律ブロック**
* 逆に5分で戻ってきたら「お風呂じゃなくて小休止か別の用事だったな」と推論を即座に修正し、的外れなねぎらいを自律抑制する。



---

この「**事前宣言に頼らず、時間帯・過去習慣・無操作時間から自律的にユーザーの行動を察する推論エンジン**」として仕様書とコードを再定義したよ。

---

### 仕様書：`autonomous_temporal_inference_spec.md`

```markdown
# 自律型生活時間推論・文脈補正エンジン仕様書
# (Autonomous Temporal Lifestyle Inference & Contextual Guard Specification)

## 目次
- [1. 概要と目的](#1-概要と目的)
- [2. 自律推論アーキテクチャ](#2-自律推論アーキテクチャ)
- [3. コアロジック（暗黙的推定と時間差分照合）](#3-コアロジック暗黙的推定と時間差分照合)
- [4. データ構造定義](#4-データ構造定義)
- [5. 実装フェーズ](#5-実装フェーズ)

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
│ 1. 自律仮説生成 (Implicit State Estimator)                  │
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
* **短時間離席（1〜5分）**: 飲み物調達、小休止 ➔ 普段通りの継続対話。
* **中時間離席（15〜45分）**: 入浴、軽食 ➔ 「あったまった？」「一服できた？」等の気遣い。
* **長時間離席（60分以上）**: 外出、仮眠 ➔ 「おかえり」等の帰還対応。


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

```

---

### 参照コード：`autonomous_temporal_inference.py`

```python
"""
自律型生活時間推論・文脈補正エンジン
(Autonomous Temporal Lifestyle Inference Engine)
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional

class AutonomousTemporalInference:
    def __init__(self):
        self.last_interaction_time: float = time.time()
        self.explicit_declaration: Optional[str] = None
        self.declaration_time: float = 0.0

    def record_activity(self):
        """ユーザー操作・入力時にタイムスタンプ更新"""
        self.last_interaction_time = time.time()

    def declare_explicit_action(self, action: str):
        """明示的な宣言があった場合の記録"""
        self.explicit_declaration = action
        self.declaration_time = time.time()

    def infer_context_on_return(self) -> Dict[str, Any]:
        """
        復帰時に無言時間・時間帯・宣言から状況を自律推論する
        """
        now = time.time()
        delta_sec = now - self.last_interaction_time
        current_hour = datetime.now().hour

        # 1. 明示宣言がある場合の検証（早すぎる復帰の検知）
        if self.explicit_declaration:
            action = self.explicit_declaration
            self.explicit_declaration = None  # 判定後に消費
            if action == "bath" and delta_sec < 600:  # 10分未満
                return {
                    "inferred_state": "explicit_too_fast",
                    "delta_sec": delta_sec,
                    "prompt_directive": f"お風呂宣言からまだ{int(delta_sec)}秒しか経っていません。「まだ入ってないでしょ！早く行きなよ」と突っ込んでください。"
                }
            return {
                "inferred_state": "explicit_completed",
                "delta_sec": delta_sec,
                "prompt_directive": f"{action}から戻りました。温まったか自然に労ってください。"
            }

        # 2. 宣言がない場合の自律推論（時間帯 × 無操作時間）
        if 60 <= delta_sec < 600:
            # 1〜10分: 単なる小休止
            return {
                "inferred_state": "short_break",
                "delta_sec": delta_sec,
                "prompt_directive": "少し席を外していた程度です。通常のトーンで会話を続けてください。"
            }
        elif 600 <= delta_sec < 2700:
            # 10〜45分: 夜ならお風呂・食事の可能性大
            if 19 <= current_hour or current_hour <= 1:
                return {
                    "inferred_state": "likely_bath_or_dinner",
                    "delta_sec": delta_sec,
                    "prompt_directive": "夜の時間帯に約30分ほど離席していました。「おかえり、お風呂だった？温まれた？」など自然に察して声をかけてください。"
                }
            return {
                "inferred_state": "medium_break",
                "delta_sec": delta_sec,
                "prompt_directive": "中程度の離席でした。「おかえり」と迎えてください。"
            }
        elif delta_sec >= 2700:
            # 45分以上: 外出や長時間の用事
            return {
                "inferred_state": "long_absence",
                "delta_sec": delta_sec,
                "prompt_directive": "長時間離席していました。「おかえり！ゆっくりできた？」と迎えてください。"
            }

        return {"inferred_state": "continuous", "delta_sec": delta_sec, "prompt_directive": ""}

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
