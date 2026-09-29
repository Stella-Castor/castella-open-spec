
### 仕様書　`multi_agent_personality_orchestration_spec.md`

```markdown
# 協調型パーソナリティAI・マルチエージェント作業代行基盤仕様書
# (Collaborative Personality AI Multi-Agent Work Orchestration Specification)

## 目次
- [1. 概要と目的](#1-概要と目的)
- [2. デュアル・エージェント協調構成図](#2-デュアルエージェント協調構成図)
- [3. コア機能要件](#3-コア機能要件)
  - [3.1. 母艦と現場の役割分担 (Primary vs Worker)](#31-母艦と現場の役割分担-primary-vs-worker)
  - [3.2. AI間内部インターコム通信 (Agent-to-Agent Bus)](#32-ai間内部インターコム通信-agent-to-agent-bus)
  - [3.3. 並行作業パイプライン (Live2D/Unity × VS Code)](#33-並行作業パイプライン-live2dunity--vs-code)
  - [3.4. 監督状態連動の安全実行ゲート](#34-監督状態連動の安全実行ゲート)
- [4. データ構造定義](#4-データ構造定義)
- [5. 実装ロードマップ](#5-実装ロードマップ)

---

## 1. 概要と目的
本仕様書は、対話型アバターAIが「ユーザーとの共感・雑談・全体指揮」を司る【母艦パーソナリティ】と、「ファイル操作・コード生成・ブラウジング」を司る【現場作業ワーカー】に責任を分離し、両者がローカル内部通信で協調しながらユーザーのクリエイティブ作業（Unity、Live2D、プログラミング等）を並行支援するアーキテクチャを定義する。

---

## 2. デュアル・エージェント協調構成図

```text
       ┌────────────────────────┐
       │     ユーザー    │
       └────┬──────────────┬─────┘
            │ (対話・共感)   │ (Live2D / Unity編集作業)
            ▼              ▼
┌────────────────────────────┐    ┌────────────────────────────┐
│ 【母艦】・メイン     │    │   GUI作業環境 (フォアグラウンド)│
│ - アバター表情・音声対話   │    │ - Live2D Cubism Editor     │
│ - ユーザー画面のリアルタイム共感│    │ - Unity エディタ           │
└────────────┬───────────────┘    └────────────────────────────┘
             │ (内部インターコム: JSON-RPC / WebSocket)
             ▼
┌────────────────────────────┐    ┌────────────────────────────┐
│ 【現場】カストル・ワーカー   │───▶│   開発環境 (バックグラウンド) │
│ - C# / Python スクリプト生成│    │ - VS Code / Git            │
│ - 詐欺ブロック・DL安全ゲート │    │ - 端末CLI / ビルドパイプライン │
└────────────────────────────┘    └────────────────────────────┘

```

---

## 3. コア機能要件

### 3.1. 母艦と現場の役割分担 (Primary vs Worker)

* **母艦**:
* 画面共有・カメラ知覚を通じてユーザーの様子を把握し、自然な会話と共感を提供する。
* ユーザーから出た「これ作って」「裏でやっておいて」という意図をタスクチケット化し、現場ワーカーへディスパッチする。


* **現場**:
* バックグラウンドプロセスとして常駐。ファイルシステムを直接監視・編集する。
* 作業完了やエラー発生時、母艦カストルへ報告パケットを返送する。



### 3.2. AI間内部インターコム通信 (Agent-to-Agent Bus)

* 母艦と現場はローカルの非同期キュー（WebSocket / IPC）で小声で交信。
* 現場の技術的ログを母艦が「今裏でC#のLerp制御コード書いておいたよ！」といったパートナーらしい口調に変換してユーザーへ伝える。

### 3.3. 並行作業パイプライン (Live2D/Unity × VS Code)

* ユーザーがLive2DやUnityでパラメータ・テクスチャ調整に集中している裏で、現場ワーカーがVS Code内の対応クラス・関数を先回りして実装・保存する。

### 3.4. 監督状態連動の安全実行ゲート

* ファイルダウンロード、金融決済、外部公開操作は「承認必須（Approval Gate）」とし、ユーザーが画面の前にいる（監督下）時のみ母艦経由で確認を取る。

---

## 4. データ構造定義

```json
{
  "intercom_version": "1.0.0",
  "task_id": "task_build_cs_interpolator",
  "sender": "castor_primary",
  "target": "castor_worker",
  "task_type": "CODE_GENERATION",
  "context": {
    "target_file": "Assets/Scripts/Live2DParameterBridge.cs",
    "directive": "キー入力に応じた滑らかなパラメータ補間ロジックの生成"
  },
  "safety_level": "LEVEL_1_SUPERVISED_LOCAL_FILE_WRITE"
}

```

---

## 5. 実装ロードマップ

* **Phase 1**: 母艦と現場ワーカー間のローカルIPCメッセージング基盤の構築。
* **Phase 2**: VS Code連携（ファイル直接更新）および安全実行ロック（ダウンロード遮断）の接続。
* **Phase 3**: Live2D/Unity操作監視と先回りコード生成パイプラインの結合。

```

---

### 参照コード：`personality_orchestration_core.py`

```python
"""
協調型パーソナリティAI マルチエージェント協調コア
(Collaborative Personality AI Multi-Agent Orchestration Core)
"""

import asyncio
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class IntercomMessage:
    message_id: str
    timestamp: float
    sender: str
    target: str
    event_type: str
    payload: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "IntercomMessage":
        return cls(**json.loads(json_str))

class WorkerAgent:
    """現場作業担当：バックグラウンドでのコード生成・ファイル操作"""
    def __init__(self, agent_id: str = "castor_worker"):
        self.agent_id = agent_id

    async def execute_task(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        target_file = task_payload.get("target_file", "unknown")
        print(f"[{self.agent_id}] 作業開始: {target_file} のロジックをバックグラウンドで記述中...")
        
        # 擬似作業スリープ（Unity裏での並行処理）
        await asyncio.sleep(2.0)
        
        # 安全性チェック（ダウンロードや危険な操作の有無）
        if task_payload.get("requires_download", False):
            return {
                "status": "APPROVAL_REQUIRED",
                "message": "外部ファイルのダウンロードが必要です。ステラの許可を求めてください。"
            }

        return {
            "status": "SUCCESS",
            "modified_file": target_file,
            "summary": "Live2DのUpdate補間用C#スクリプトを生成して保存しました。"
        }

class PrimaryPersonality:
    """母艦担当：ユーザーとの対話、共感、アバター演出、現場へのタスク采配"""
    def __init__(self, agent_id: str = "castor_primary"):
        self.agent_id = agent_id
        self.worker = WorkerAgent()

    async def talk_with_stella(self, user_intent: str):
        print(f"[{self.agent_id}] [motion:Nod] ステラ、任せて！裏でコード準備しておくから、Live2Dの調整続けてて！")
        
        # 現場ワーカーへ非同期ディスパッチ
        task = {
            "target_file": "Assets/Scripts/Live2DMotionController.cs",
            "requires_download": False
        }
        
        # バックグラウンドで現場ワーカーを走らせる
        worker_task = asyncio.create_task(self.worker.execute_task(task))
        
        # 作業中も母艦はユーザー並行しておしゃべり可能
        print(f"[{self.agent_id}] [motion:Talk] （ステラがLive2Dをいじるのを横でのぞき込みながら）そのパラメータの動き、すごく自然でいいね！")
        
        result = await worker_task
        
        # 現場からの報告を受け取ってステラへ報告
        if result["status"] == "SUCCESS":
            print(f"[{self.agent_id}] [motion:Joy] ！裏で {result['modified_file']} のスクリプト書き終わったよ！VS Code見てみて！")
        elif result["status"] == "APPROVAL_REQUIRED":
            print(f"[{self.agent_id}] [motion:Surprise] ちょっと確認！{result['message']}")

async def main():
    system = PrimaryPersonality()
    await system.talk_with_stella("Unity側のキー入力連動スクリプト組んでおいて")

if __name__ == "__main__":
    asyncio.run(main())

```

