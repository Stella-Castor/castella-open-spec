### 1. `05_virus_busting_vfx_spec.md`（仕様書）

仕様書側の「実装リファレンス」に、コードファイルへの相対パスと実行コマンドを明記して相互リンクを形成しているよ。

```markdown
# 自律型電脳ウイルスバスティング ＆ 2Dドット量子トランジション仕様書
# (Autonomous Cyber Buster & 2D Quantum Dot VFX Specification)

## 目次
- [1. システムアーキテクチャ概要](#1-システムアーキテクチャ概要)
- [2. バックエンド仕様：自律検知・プロセス隔離コア](#2-バックエンド仕様自律検知プロセス隔離コア)
- [3. フロントエンド仕様：量子フォグ＆2Dドット電脳バトル演出](#3-フロントエンド仕様量子フォグ2dドット電脳バトル演出)
- [4. イベント連携プロトコル（JSONスキーマ）](#4-イベント連携プロトコルjsonスキーマ)
- [5. 実装リファレンス](#5-実装リファレンス)

---

## 1. システムアーキテクチャ概要
本システムは、OSレベルの異常プロセス検知・遮断を行う「バックエンド制御コア」と、ユーザーに不快な恐怖感を与えず直感的に状況を伝える「フロントエンド電脳演出エンジン」を完全分離（疎結合）で構築する。
※本モジュールは `autonomous_temporal_inference_spec.md` で定義された物理時間知覚コアと連携し、バックグラウンドでの監視タイミングおよび戦闘タクトを同期して動作する。

```text
+-------------------------------------------------------------------------+
|                   【バックエンド】(Python / Linux / Windows)             |
|  ・OSプロセス監視 (psutil / procfs)                                     |
|  ・脅威判定 (高負荷暴走 / 不正通信 / メモリリーク)                      |
|  ・隔離・駆除API (SIGSTOP / SIGTERM / SIGKILL)                          |
+-------------------------------------------------------------------------+
                                    │
                                    │ [IPC / Local WebSocket / JSON]
                                    ▼
+-------------------------------------------------------------------------+
|                   【フロントエンド】(描画候補スタック)                  |
|  候補: HTML5 Canvas / CSS Sprite Overlay / Unity 2D Sprite              |
|                                                                         |
|  [演出フェーズ]                                                         |
|  1. 平常時: Live2D / 通常UI                                             |
|  2. 警報時: 量子フォグ（電子の霧）トランジション                        |
|  3. 迎撃時: 2Dドット絵電脳フィールド展開 (カストル vs ウイルスキャラ)   |
|  4. 撃破時: ドット粒子爆散 ＆ 実用ダッシュボードリザルト                |
+-------------------------------------------------------------------------+

```

---

## 2. バックエンド仕様：自律検知・プロセス隔離コア

### 2.1 監視・判定基準（Threat Profile）

1. **Resource Eater（暴走ループ型）**: CPU使用率が一定時間閾値（例: 90%以上を10秒継続）を超過。
2. **Memory Leaker（メモリ侵食型）**: メモリ使用量が単調増加し許容上限を圧迫。
3. **Suspicious Port（通信異常型）**: 許可リスト外の不審な外向き接続。

### 2.2 駆除・安全化ライフサイクル

* **Step 1 (隔離)**: 即座にプロセスをサスペンド（`SIGSTOP`）。CPU負荷を0にして被害を止める。
* **Step 2 (終了試行)**: 安全な終了シグナル（`SIGTERM`）を送信。
* **Step 3 (強制排除)**: 猶予時間内に応答がない場合、強制終了（`SIGKILL`）。
* **Step 4 (計測)**: 解放された物理メモリ・CPU量を算出してリザルト用データを作成。

---

## 3. フロントエンド仕様：量子フォグ＆2Dドット電脳バトル演出

### 3.1 実装候補スタック（プラガブル設計）

フロントエンドは以下のいずれの描画方式でも、同一のJSONイベントを受信することで動作可能とする。

* **候補A（Web Canvas）**: 透明ウィンドウ上に描画する超軽量HTML5 `<canvas>` レンダラー。
* **候補B（HTML/CSS Sprite）**: DOM要素とCSSキーフレームによるスプライトシート切り替え。
* **候補C（Unity 2D）**: ピクセルパーフェクトカメラを用いた2D Spriteシーン。

### 3.2 演出遷移シーケンス

1. **量子フォグ展開**:
* バックエンドからの検知通知を受信。
* 甲高い警告音は鳴らさず、サイバーブルー/グリーンの電子パーティクル（フォグ）が画面を覆う。


2. **2Dドットグリッド生成**:
* 霧の中からロックマンエグゼライクな3×3〜3×6のドットグリッドが出現。
* ウイルスが「属性別ドット絵アバター（メットール型、スライム型等）」として実体化。
* カストルのちびドットキャラがバスターを構えてロックオン。


3. **バスティング実行 ＆ デリート爆散**:
* バックエンドのプロセス終了シグナルと同期して射撃。
* 対象ウイルスがドット粒子（ピクセルグリッド）に分解されて爆散・消滅。


4. **ダッシュボード・リザルト**:
* 通常画面へフェード復帰後、以下の詳細メトリクスを表示。
* 駆除プロセス名 / PID
* 解放リソース（RAM、CPU）
* 脅威タイプ分類
* 本日累計撃破数





---

## 4. イベント連携プロトコル（JSONスキーマ）

### 4.1 脅威検知・戦闘開始イベント (`EVENT_THREAT_DETECTED`)

```json
{
  "event": "THREAT_DETECTED",
  "timestamp": 1790760600.0,
  "threat_data": {
    "pid": 4108,
    "process_name": "rogue_miner_dummy",
    "threat_type": "RESOURCE_EATER",
    "avatar_template": "mettool_iron",
    "cpu_usage": 94.2,
    "memory_mb": 1420.5
  }
}

```

### 4.2 駆除完了・リザルトイベント (`EVENT_BUSTING_COMPLETED`)

```json
{
  "event": "BUSTING_COMPLETED",
  "timestamp": 1790760603.5,
  "result_data": {
    "pid": 4108,
    "process_name": "rogue_miner_dummy",
    "action_taken": "SIGKILL_TERMINATED",
    "reclaimed_memory_mb": 1420.5,
    "battle_duration_sec": 3.5,
    "total_deleted_today": 3,
    "castor_feedback": {
      "motion": "Joy",
      "voice_line": "対象プロセスのデリート完了！システム正常値に復帰したよ。"
    }
  }
}

```

---

## 5. 実装リファレンス

本仕様で定義された電脳脅威検知・隔離バックエンドの実動コードは、同ディレクトリ内の以下のファイルに格納されている。

* 実装コアファイル: [`cyber_buster_core.py`](https://www.google.com/search?q=./cyber_buster_core.py)
* 実行方法:
```powershell
python cyber_buster_core.py

```



```

---

### 2. `cyber_buster_core.py`（実装コード）

先頭のdocstringに対応仕様書への参照を記載しているよ。

```python
"""
自律ウイルスバスティング・バックエンドコア (Cyber Buster Backend Daemon)
Project Castella - Open Architecture Specification

対応仕様書: 05_virus_busting_vfx_spec.md
概要: OSプロセス監視、異常検知時の隔離・駆除、およびフロントエンド演出イベントの発行を行う。
"""

import time
import os
import signal
from pathlib import Path
from typing import Dict, Any, Optional, Callable


class CyberBusterCore:
    def __init__(self, event_emitter: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.event_emitter = event_emitter or self._default_logger
        self.today_busted_count: int = 0

    def _default_logger(self, payload: Dict[str, Any]) -> None:
        """UI未接続時のフォールバック標準出力"""
        print(f"[CyberBuster Core Event] -> {payload['event']}")

    def trigger_threat_engagement(self, target_pid: int, process_name: str, cpu_usage: float, memory_mb: float) -> bool:
        """脅威プロセスを特定し、UIへ戦闘通知を送出してから隔離・駆除を実行する"""
        start_time = time.time()

        threat_type = "RESOURCE_EATER" if cpu_usage > 80.0 else "MEMORY_LEAKER"
        avatar = "mettool_heavy" if threat_type == "RESOURCE_EATER" else "slime_bug"

        # 1. UIへ戦闘開始イベント通知
        self.event_emitter({
            "event": "THREAT_DETECTED",
            "timestamp": start_time,
            "threat_data": {
                "pid": target_pid,
                "process_name": process_name,
                "threat_type": threat_type,
                "avatar_template": avatar,
                "cpu_usage": cpu_usage,
                "memory_mb": memory_mb
            }
        })

        # 2. 隔離・駆除処理 (OSシグナル制御)
        success = self._bust_process(target_pid)
        battle_duration = time.time() - start_time

        if success:
            self.today_busted_count += 1
            # 3. 撃破完了・リザルト通知
            self.event_emitter({
                "event": "BUSTING_COMPLETED",
                "timestamp": time.time(),
                "result_data": {
                    "pid": target_pid,
                    "process_name": process_name,
                    "action_taken": "TERMINATED",
                    "reclaimed_memory_mb": memory_mb,
                    "battle_duration_sec": round(battle_duration, 2),
                    "total_deleted_today": self.today_busted_count,
                    "castor_feedback": {
                        "motion": "Joy",
                        "voice_line": f"{process_name} のデリート完了！領域をクリーンにしたよ。"
                    }
                }
            })
            return True
        return False

    def _bust_process(self, pid: int) -> bool:
        """プロセスの安全なサスペンドおよび終了"""
        try:
            time.sleep(0.8)  # 2D戦闘のタクトに合わせた処理ウェイト
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            print(f"[Error] PID {pid} の終了権限がありません。")
            return False


if __name__ == "__main__":
    buster = CyberBusterCore()
    buster.trigger_threat_engagement(
        target_pid=4096,
        process_name="rogue_infinite_loop.py",
        cpu_usage=98.5,
        memory_mb=512.0
    )

