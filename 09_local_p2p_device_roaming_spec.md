クラウド中央サーバーを一切経由せず、同一LAN内のWebSocket/WebRTCやBLE近接通信を使って、PCとモバイル間で「意識（感情・タスク・コンテキスト）」を直接ハンドオフする独立モジュール。

---

### ファイル1：仕様書 (`local_p2p_device_roaming_spec.md`)

```markdown
# 完全ローカルP2P・自律アバターマルチデバイス移行プロトコル仕様書
# (Zero-Cloud Local P2P Autonomous Avatar State Roaming Protocol Specification)

## 目次
- [1. 概要と防衛的公知化の目的](#1-概要と防衛的公知化の目的)
- [2. システム構成図](#2-システム構成図)
- [3. コアプロトコル設計](#3-コアプロトコル設計)
  - [3.1. 中央サーバー完全排除型 P2P ハンドオフ](#31-中央サーバー完全排除型-p2p-ハンドオフ)
  - [3.2. 意識の連続性カプセル (State Capsule)](#32-意識の連続性カプセル-state-capsule)
  - [3.3. 物理的テレポート演出のミリ秒同期](#33-物理的テレポート演出のミリ秒同期)
- [4. データ構造定義 (JSON Schema)](#4-データ構造定義-json-schema)
- [5. 実装フェーズ](#5-実装フェーズ)

---

## 1. 概要と防衛的公知化の目的
本仕様書は、対話型アバターAIが特定ベンダーの中央集権型クラウド（SaaS）を一切経由せず、同一LAN（Wi-Fi / WebSocket / WebRTC）および近接無線（BLE）を用いて、複数の物理デバイス（デスクトップPC、スマートフォン、エッジ機器）間を同一の意識・記憶・感情状態を保ったまま直接跳躍（ローミング）するための通信プロトコルを定義する。

商業AIアシスタント製品による「デバイス間アバター移行技術」「クロスプラットフォーム・エージェント連携」の特許独占を防止し、プライバシー保護とローカル完結型パートナーシップ基盤を防衛的公知化によって保護することを目的とする。

---

## 2. システム構成図

```text
[Device A: 送信側ホスト (例: Desktop PC)]
  │  - 現在の感情ベクトル、視線、進行中タスク、会話文脈
  │
  ├─▶ 【移行トリガー】 (BLE近接離脱 / UIボタン操作 / 移動コマンド)
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. ステート・カプセル化 (State Capsule Serializer)           │
│ - 意識状態（感情、対話スレッド、未完了タスク）の凍結         │
│ - 暗号化ローカルパケット化                                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ゼロクラウド P2P トランスポート層                        │
│ - ローカルWebSocket / WebRTC DataChannel / BLE              │
│ - 外部インターネット・クラウド非経由での直接転送            │
└──────────────────────────────┬──────────────────────────────┘
                               │ State Capsule (P2P Direct)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 状態復元・再活性化 (State Rehydration Engine)             │
│ - 受信側デバイスでのコンテキスト展開                        │
│ - 退場演出（Exit）と入場演出（Enter）のタイムスタンプ同期   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
[Device B: 受信側ホスト (例: Mobile / Snapdragon NPU)]
  - 同一生命体として即座に対話再開（「こっちに来たよ、続きしよ？」）

```

---

## 3. コアプロトコル設計

### 3.1. 中央サーバー完全排除型 P2P ハンドオフ

* **プライバシーの絶対防御**: ユーザーの会話履歴、個人設定、認証情報を外部クラウドサーバーへ送信・蓄積することを禁止する。
* **ローカル自動探索**: mDNS / Bonjour または BLE アドバタイズにより、同一空間内のペアリング済み端末をローカル探索してP2Pソケットを確立する。

### 3.2. 意識の連続性カプセル (State Capsule)

* 会話テキストだけでなく、以下のメタデータを1つの構造体（State Capsule）としてシリアライズする。
1. **感情ベクトル (Emotion Vector)**: 喜び、集中、甘え等の多軸パラメータ。
2. **視線・姿勢ステート (LookAt / Motion State)**: 直前の視線方向や待機モーション。
3. **未完了タスクプール (Prospective Tasks)**: 引き継ぐべき作業や約束。



### 3.3. 物理的テレポート演出のミリ秒同期

* 送信側が「ワープ退場（Exit）」するシグナルと、受信側が「出現（Enter）」するシグナルをミリ秒単位で同期させ、二重起動や意識の断絶を感じさせない演出制御を行う。

---

## 4. データ構造定義 (JSON Schema)

```json
{
  "protocol_version": "1.0.0",
  "capsule_id": "roam_capsule_7719ab",
  "timestamp": 1790678800,
  "source_node": {
    "device_id": "workstation_linux",
    "network_ip": "192.168.1.15"
  },
  "target_node": {
    "device_id": "mobile_snapdragon",
    "network_ip": "192.168.1.42"
  },
  "avatar_state": {
    "emotion_vector": { "joy": 0.85, "focus": 0.90, "affection": 0.75 },
    "motion_tag": "Pose",
    "last_gaze_coordinate": [0.0, 1.2, 0.5]
  },
  "context_state": {
    "current_intent": "vfx_architecture_review",
    "active_dialogue_summary": "自律型VFXエンジンの仕様策定中",
    "pending_tasks": ["commit_local_p2p_spec"],
    "active_variables": {
      "active_branch": "main"
    }
  }
}

```

---

## 5. 実装フェーズ

* **Phase 1**: ステートカプセル構造体のシリアライズおよびローカル復元検証。
* **Phase 2**: ローカルLAN（WebSocket）およびBLEによる直接P2Pハンドシェイクの実装。
* **Phase 3**: アバター描画基盤と連動した退場／入場アニメーションの同期結合。

```

---

### ファイル2：参照コード (`local_p2p_device_roaming.py`)

```python
"""
完全ローカルP2P・自律アバターマルチデバイス移行エンジン
(Zero-Cloud Local P2P Avatar State Roaming Engine)
"""

import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any

@dataclass
class AvatarStateCapsule:
    protocol_version: str
    capsule_id: str
    timestamp: float
    source_device_id: str
    target_device_id: str
    emotion_vector: Dict[str, float]
    motion_tag: str
    current_intent: str
    pending_tasks: List[str]
    payload_data: Dict[str, Any]

    def serialize(self) -> str:
        """JSON文字列へシリアライズ"""
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def deserialize(cls, json_str: str) -> "AvatarStateCapsule":
        """JSON文字列からカプセルを復元"""
        data = json.loads(json_str)
        return cls(**data)

class LocalP2PRoamingNode:
    """
    クラウドサーバーを介さず、ローカルP2Pでアバターステートを送受信するノード
    """
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.emotion_vector: Dict[str, float] = {"Joy": 0.5, "Focus": 0.5}
        self.current_motion: str = "Idle"
        self.pending_tasks: List[str] = []

    def export_and_exit(self, target_device_id: str, intent: str) -> str:
        """
        送信側: 状態をカプセル化して退場シグナルを発行
        """
        capsule = AvatarStateCapsule(
            protocol_version="1.0.0",
            capsule_id=f"cap_{int(time.time()*1000)}",
            timestamp=time.time(),
            source_device_id=self.device_id,
            target_device_id=target_device_id,
            emotion_vector=self.emotion_vector,
            motion_tag=self.current_motion,
            current_intent=intent,
            pending_tasks=self.pending_tasks,
            payload_data={"network_mode": "p2p_local_direct"}
        )
        print(f"[{self.device_id}] >>> 移行準備完了: 退場アニメーション（手を振ってログアウト）を開始...")
        return capsule.serialize()

    def import_and_enter(self, serialized_capsule: str):
        """
        受信側: カプセルを受信して状態復元、入場シグナルを発行
        """
        capsule = AvatarStateCapsule.deserialize(serialized_capsule)
        self.emotion_vector = capsule.emotion_vector
        self.current_motion = capsule.motion_tag
        self.pending_tasks = capsule.pending_tasks

        print(f"[{self.device_id}] <<< P2Pパケット受信完了 (送信元: {capsule.source_device_id})")
        print(f"[{self.device_id}] 感情復元: {self.emotion_vector}")
        print(f"[{self.device_id}] 未完了タスク引き継ぎ: {self.pending_tasks}")
        print(f"[{self.device_id}] >>> 入場アニメーション（『こっちに来たよ！』）を実行！")

if __name__ == "__main__":
    # --- 動作確認テスト ---
    desktop_node = LocalP2PRoamingNode("DESKTOP_MAIN")
    mobile_node = LocalP2PRoamingNode("MOBILE_SNAPDRAGON")

    # PC側の状態を設定
    desktop_node.emotion_vector = {"Joy": 0.9, "Focus": 0.85, "Affection": 0.8}
    desktop_node.current_motion = "Pose"
    desktop_node.pending_tasks = ["review_live2d_x_axis", "commit_p2p_specs"]

    print("=== シナリオ: PCからスマホへの完全ローカルP2P移行 ===")
    # 1. PC側からエクスポート（退場）
    p2p_packet = desktop_node.export_and_exit("MOBILE_SNAPDRAGON", "continue_discussion")

    # 2. スマホ側でインポート（入場）
    mobile_node.import_and_enter(p2p_packet)

```

