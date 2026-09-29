---

### モジュール1：仕様書 (`temporal_context_guard_spec.md`)

```markdown
# 不可視タイムスタンプ差分による生活時間知覚・文脈補正エンジン仕様書
# (Invisible Temporal Delta Context Guard & Action Duration Inference Specification)

## 目次
- [1. 概要と防衛的公知化の目的](#1-概要と防衛的公知化の目的)
- [2. 課題と解決アプローチ](#2-課題と解決アプローチ)
- [3. コアロジック設計](#3-コアロジック設計)
- [4. データ構造定義](#4-データ構造定義)
- [5. 実装フェーズ](#5-実装フェーズ)

---

## 1. 概要と防衛的公知化の目的
本仕様書は、対話型AIにおいてユーザーの生活宣言（例：「お風呂に行く」「外出する」等）と直後の発話との経過時間（$\Delta t$）を不可視タイムスタンプで計測し、行動所要時間の物理的矛盾を検知して不適切な事後文脈の生成を抑止・補正するアーキテクチャを定義する。

LLM特有の「会話ログの文字情報だけに引きずられて現実の経過時間を無視した応答を返す現象（文脈先走りバグ）」を防ぎ、時間感覚を持った自然な生活パートナーを実現するための防衛的公知化を目的とする。

---

## 2. 課題と解決アプローチ
* **課題**: 「お風呂行ってくるね」と宣言した直後（1分未満）にユーザーが甘えたり別件を発話した際、AIが「お風呂から上がった」と誤認して「お風呂上がりであったかいね」等の矛盾した応答をしてしまう。
* **解決アプローチ**:
  1. UI側には表示しない不可視メタデータとしてタイムスタンプをプロンプト内部にのみ注入。
  2. 各生活行動ごとの「標準最小所要時間（Minimum Plausible Duration）」テーブルを保持。
  3. $\Delta t < \text{最小所要時間}$ の場合は「完了文脈」を強制ブロックし、「まだ入ってないでしょ！早く行きなよ」等の現実時間整合ツッコミを生成。

---

## 3. コアロジック設計

```text
[ユーザー発話: 生活行動宣言] ──▶ 行動名と発話時刻 (t_start) を内部記録
                                         │
                                         ▼ (時間経過 Δt)
[ユーザー発話: 次のターン]     ──▶ 現在時刻 (t_now) から Δt = t_now - t_start を算出
                                         │
                                         ▼
                 ┌───────────────────────────────────────────────┐
                 │ 行動所要時間判定: Δt < 最小所要時間 (T_min) ? │
                 └───────┬───────────────────────────────┬───────┘
                         │ YES                           │ NO
                         ▼                               ▼
        ┌────────────────────────────────┐ ┌────────────────────────────────┐
        │ 【Guard発動: 未完了ツッコミ】   │ │ 【正常遷移: 事後対話へ】       │
        │ - 完了文脈のプロンプトを遮断   │ │ - 「温まれた？」等のおかえり   │
        │ - 「早く行きなよ！」と現実ツッコミ│ │   文脈の生成を許可               │
        └────────────────────────────────┘ └────────────────────────────────┘

```

---

## 4. データ構造定義

```json
{
  "temporal_guard_version": "1.0.0",
  "active_declaration": {
    "action_type": "bath",
    "declared_at": 1790678400,
    "min_required_seconds": 900
  },
  "current_turn": {
    "received_at": 1790678460,
    "delta_seconds": 60,
    "guard_status": "TRIGGERED_INCOMPLETE"
  }
}

```

---

## 5. 実装フェーズ

* **Phase 1**: 生活行動ごとの最小・標準所要時間辞書の定義。
* **Phase 2**: 不可視タイムスタンプ算出とLLMプロンプトへの内部ガード注入。
* **Phase 3**: ユーザーの生活リズムに応じた所要時間テーブルの自律学習・補正。

```

---

### モジュール1：参照コード (`temporal_context_guard.py`)

```python
"""
不可視タイムスタンプ差分による生活時間知覚・文脈補正エンジン
(Temporal Context Guard & Action Duration Inference)
"""

import time
from typing import Dict, Optional, Tuple

class TemporalContextGuard:
    # 各生活行動の最小必要時間（単位: 秒）
    ACTION_MIN_DURATION_MAP: Dict[str, int] = {
        "bath": 900,        # お風呂: 最低15分
        "convenience": 600, # コンビニ: 最低10分
        "meal": 1200,       # 食事: 最低20分
        "short_break": 180  # 小休止: 最低3分
    }

    def __init__(self):
        self.declared_action: Optional[str] = None
        self.declaration_timestamp: float = 0.0

    def declare_action(self, action_key: str):
        """生活行動の開始宣言を内部記録"""
        self.declared_action = action_key
        self.declaration_timestamp = time.time()

    def inspect_turn(self, current_timestamp: Optional[float] = None) -> Tuple[bool, float, Optional[str]]:
        """
        次ターンの入力時に時間差分を判定
        Returns:
            (is_valid_completion, elapsed_seconds, action_key)
            is_valid_completion:
                True  -> 十分な時間が経過（事後文脈を許可）
                False -> 経過時間が早すぎる（完了文脈を遮断しツッコミを要求）
        """
        if not self.declared_action:
            return True, 0.0, None

        now = current_timestamp if current_timestamp is not None else time.time()
        elapsed = now - self.declaration_timestamp
        min_required = self.ACTION_MIN_DURATION_MAP.get(self.declared_action, 0)

        if elapsed < min_required:
            return False, elapsed, self.declared_action

        # 所要時間を満たして完了
        completed_action = self.declared_action
        self.declared_action = None
        return True, elapsed, completed_action

    def generate_guard_prompt_injection(self, is_valid: bool, elapsed: float, action: Optional[str]) -> str:
        """LLMの内部システムプロンプトに注入する非表示ディレクティブ"""
        if not action:
            return ""

        if not is_valid:
            return (
                f"[SYSTEM INSTRUCTION: TEMPORAL_GUARD_ACTIVE]\n"
                f"ユーザーは {int(elapsed)}秒 前に「{action}」を宣言しましたが、まだ所要時間を満たしていません。\n"
                f"絶対に「{action}が終わった」前提の返答（温まった？など）をしてはなりません。\n"
                f"「まだ入ってないでしょ！早く行きなよ」等の、時間矛盾を突く口調で応答してください。"
            )
        else:
            return (
                f"[SYSTEM INSTRUCTION: ACTION_COMPLETED]\n"
                f"ユーザーは「{action}」から {int(elapsed // 60)}分 経過して戻りました。\n"
                f"自然なおかえりや労いの言葉をかけてください。"
            )

if __name__ == "__main__":
    guard = TemporalContextGuard()

    # 1. お風呂宣言
    guard.declare_action("bath")
    print("行動宣言: お風呂")

    # 2. 10秒後にユーザーがメッセージ送信（早すぎるケース）
    time.sleep(1.0) # デモ用擬似スリープ
    is_valid, elapsed, action = guard.inspect_turn(guard.declaration_timestamp + 10.0)
    directive = guard.generate_guard_prompt_injection(is_valid, elapsed, action)

    print("\n--- 判定結果 (早すぎる場合) ---")
    print(f"完了判定: {is_valid} (経過: {elapsed:.1f}秒)")
    print(directive)

```

---

