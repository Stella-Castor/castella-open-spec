

先頭のYAML誤判定（`---` エラー）を防ぐため、Markdown本文のみで全体をまとめた完全版を作成したよ。これをそのままファイル全体に上書き反映して大丈夫。

---

# 双方向対話型マルチエージェント協調・自律作業代行仕様書

# (Bidirectional Multi-Agent Co-Working & Autonomous Execution Specification)

## 目次

* [1. 概要と目的](https://www.google.com/search?q=%231-%E6%A6%82%E8%A6%81%E3%81%A8%E7%9B%AE%E7%9A%84)
* [2. システム構成と三者協調アーキテクチャ](https://www.google.com/search?q=%232-%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%E6%A7%8B%E6%88%90%E3%81%A8%E4%B8%89%E8%80%85%E5%8D%94%E8%AA%BF%E3%82%A2%E3%83%BC%E3%82%AD%E3%83%86%E3%82%AF%E3%83%81%E3%83%A3)
* [3. コア機能要件](https://www.google.com/search?q=%233-%E3%82%B3%E3%82%A2%E6%A9%9F%E8%83%BD%E8%A6%81%E4%BB%B6)
* [3.1. Webセッション直接連携パイプライン](https://www.google.com/search?q=%2331-web%E3%82%BB%E3%83%83%E3%82%B7%E3%83%A7%E3%83%B3%E7%9B%B4%E6%8E%A5%E9%80%A3%E6%90%BA%E3%83%91%E3%82%A4%E3%83%97%E3%83%A9%E3%82%A4%E3%83%B3)
* [3.2. 三者対等ディスカッション＆自律壁打ち](https://www.google.com/search?q=%2332-%E4%B8%89%E8%80%85%E5%AF%BE%E7%AD%89%E3%83%87%E3%82%A3%E3%82%B9%E3%82%AB%E3%83%83%E3%82%B7%E3%83%A7%E3%83%B3%E8%87%AA%E5%BE%8B%E5%A3%81%E6%89%93%E3%81%A1)
* [3.3. 助言からの自律コード生成・並行作業](https://www.google.com/search?q=%2333-%E5%8A%A9%E8%A8%80%E3%81%8B%E3%82%89%E3%81%AE%E8%87%AA%E5%BE%8B%E3%82%B3%E3%83%BC%E3%83%89%E7%94%9F%E6%88%90%E4%B8%A6%E8%A1%8C%E4%BD%9C%E6%A5%AD)
* [3.4. 監督状態連動の安全実行ロック](https://www.google.com/search?q=%2334-%E7%9B%A3%E7%9D%A3%E7%8A%B6%E6%85%8B%E9%80%A3%E5%8B%95%E3%81%AE%E5%AE%89%E5%85%A8%E5%AE%9F%E8%A1%8C%E3%83%AD%E3%83%83%E3%82%AF)


* [4. ブラウザ拡張ブリッジ実装詳細 (Physical Interconnect Layer)](https://www.google.com/search?q=%234-%E3%83%96%E3%83%A9%E3%82%A6%E3%82%B6%E6%8B%A1%E5%BC%B5%E3%83%96%E3%83%AA%E3%83%83%E3%82%B8%E5%AE%9F%E8%A3%85%E8%A9%B3%E7%B4%B0-physical-interconnect-layer)
* [4.1. ディレクトリ構造](https://www.google.com/search?q=%2341-%E3%83%87%E3%82%A3%E3%83%AC%E3%82%AF%E3%83%88%E3%83%AA%E6%A7%8B%E9%80%A0)
* [4.2. DOM自動注入および送信発火ロジック](https://www.google.com/search?q=%2342-dom%E8%87%AA%E5%8B%95%E6%B3%A8%E5%85%A5%E3%81%8A%E3%82%88%E3%81%B3%E9%80%81%E4%BF%A1%E7%99%BA%E7%81%AB%E3%83%AD%E3%82%B8%E3%83%83%E3%82%AF)
* [4.3. ストリーミング完了検知およびテキスト抽出ロジック](https://www.google.com/search?q=%2343-%E3%82%B9%E3%83%88%E3%83%AA%E3%83%BC%E3%83%9F%E3%83%B3%E3%82%B0%E5%AE%8C%E4%BA%86%E6%A4%9C%E7%9F%A5%E3%81%8A%E3%82%88%E3%81%B3%E3%83%86%E3%82%AD%E3%82%B9%E3%83%88%E6%8A%BD%E5%87%BA%E3%83%AD%E3%82%B8%E3%83%83%E3%82%AF)
* [4.4. ローカルWebSocket中継サーバー仕様](https://www.google.com/search?q=%2344-%E3%83%AD%E3%83%BC%E3%82%AB%E3%83%ABwebsocket%E4%B8%AD%E7%B6%99%E3%82%B5%E3%83%BC%E3%83%90%E3%83%BC%E4%BB%95%E6%A7%98)


* [5. 通信シーケンス](https://www.google.com/search?q=%235-%E9%80%9A%E4%BF%A1%E3%82%B7%E3%83%BC%E3%82%B1%E3%83%B3%E3%82%B9)
* [6. データ構造定義 (JSON Schema)](https://www.google.com/search?q=%236-%E3%83%87%E3%83%BC%E3%82%BF%E6%A7%8B%E9%80%A0%E5%AE%9A%E7%BE%A9-json-schema)
* [7. 実装フェーズ](https://www.google.com/search?q=%237-%E5%AE%9F%E8%A3%85%E3%83%95%E3%82%A7%E3%83%BC%E3%82%BA)

---

## 1. 概要と目的

本仕様書は、作業者がクリエイティブ作業（2Dモデリング、ゲームエンジン操作等）に専念している環境において、OS・ローカル環境で稼働する【ローカル作業エージェント】が、ブラウザ上で稼働する文脈保持型【母艦AI】と双方向通信ブリッジを介して自律的に対話・壁打ちを行い、その知恵とヒントを吸収してVS Code等の開発環境へコードを自動実装する統合協調アーキテクチャを定義する。

外部の新規APIセッションによる人格・文脈の分断を排除し、現在対話中のWebセッションをそのまま母艦ブレインとして直接接続することを特徴とする。

---

## 2. システム構成と三者協調アーキテクチャ

```text
       ┌────────────────────────┐
       │      ユーザー (User)    │
       └────┬──────────────┬─────┘
            │              │
 (GUIクリエイティブ制作)     │ (方針相談・共同意思決定)
            │              ▼
            │     ┌────────────────────────────────┐
            │     │ 【母艦】Primary Model (Web)    │
            │     │ - 累積記憶・長期文脈の保持     │
            │     │ - 高度設計推論・助言の生成     │
            │     └──────────────▲─────────────────┘
            │                    │
            │          [ブラウザ拡張ブリッジ]
            │          (DOM自動注入 / 応答テキスト抽出)
            │                    │
            │                    │ ローカル通信 (WebSocket)
            │                    ▼
            │     ┌────────────────────────────────┐
            │     │ 【現場】Local Agent (OS/WSL)   │
            │     │ - ファイル監視・自律相談トリガー│
            │     │ - 母艦の助言を解読しコード実装 │
            │     └──────────────┬─────────────────┘
            ▼                    ▼
   [モデリング / 制作GUI] [エディタ / CLI環境]
      ユーザーの作業空間    ローカルエージェントの作業空間

```

---

## 3. コア機能要件

### 3.1. Webセッション直接連携パイプライン

* **入力自動注入**:
* ローカルエージェントから送信された質問・相談パケットを、ブラウザ拡張機能がアクティブなWebチャットの入力欄へ直接注入し、送信イベントを発火させる。


* **出力リアルタイム抽出**:
* 母艦AIのストリーミング出力をDOM監視（MutationObserver）でトラッキングし、生成完了時にテキスト・コードブロックを丸ごと抽出してローカルエージェントへ返送する。



### 3.2. 三者対等ディスカッション＆自律壁打ち

* **意思決定の柔軟性**:
* ユーザーとローカルエージェントの間で実装方針を決定することも、母艦AIを交えて方針を決めることも可能とする。


* **自律相談（壁打ち）トリガー**:
* ローカルエージェントが構文設計、例外処理、最適化ロジック等で高度な推論を必要とした際、自律的に母艦AI宛てのプロンプトを構築して自動送信する。



### 3.3. 助言からの自律コード生成・並行作業

* ユーザーがフォアグラウンドでGUI作業を行っている裏で、ローカルエージェントが母艦AIの返答に含まれるヒントやロジック構成をパーシング。
* VS Code等の対象プロジェクト内ソースコード（Python, C#等）へ直接差分適用・自動保存を実行する。

### 3.4. 監督状態連動の安全実行ロック

* **監視・自律ブラウジングの防壁**:
* ファイルダウンロード、金融決済、外部危険スクリプトの実行は明示的な承認制（Approval Gate）とする。
* ユーザーの離席中（無監督状態）は、破壊的変更を禁止する読み取り専用セーフティモードに自動移行する。



---

## 4. ブラウザ拡張ブリッジ実装詳細 (Physical Interconnect Layer)

WebチャットセッションとローカルOS環境を物理的に直結するための通信インターフェース仕様を以下に規定する。

### 4.1. ディレクトリ構造

OS依存（Windows専用絶対パス等）を排除し、プロジェクトルート基準の相対パス構成を採用する。

```text
bridge_hotline/
├── extension/
│   ├── manifest.json       # Chrome拡張機能マニフェスト (Manifest V3)
│   └── content.js          # DOM制御およびWebSocketクライアント
└── server/
    └── bridge_server.py    # ローカル中継サーバー (Python / asyncio / websockets)

```

### 4.2. DOM自動注入および送信発火ロジック

* `content.js` はローカルサーバー（`ws://127.0.0.1:8765`）からの `INJECT_PROMPT` イベントを受信時、アクティブタブ内の入力要素（`div[contenteditable="true"]` または `textarea`）を特定する。
* フォーカスを付与した上でテキストを設定し、`InputEvent` および Enterキーの `KeyboardEvent` を連続発火させてWeb UI上の送信シーケンスを実行する。

### 4.3. ストリーミング完了検知およびテキスト抽出ロジック

* 入力送信後、`MutationObserver` を起動してDOMツリーの変化を常時監視する。
* 生成停止ボタン（`Stop/停止` aria-label）の消失、または応答コンテナ内の特定完了セレクタをトリガーとして生成終了（完了ステート）を判定する。
* 最新の応答メッセージ要素からテキストおよびコードブロックを抽出し、`RESPONSE_CAPTURED` ペイロードとしてローカルサーバーへ即時返送する。

### 4.4. ローカルWebSocket中継サーバー仕様

* `bridge_server.py` はローカルループバック（`127.0.0.1`）でのみリッスンし、外部ネットワークへのポート開放を行わない。
* `pathlib.Path` を用いてログディレクトリや一時ファイルへのアクセスを抽象化し、Linux/WSL/コンテナ環境でそのまま動作する実装を標準とする。

---

## 5. 通信シーケンス

```text
User          Local Agent         Bridge Server       Browser Extension       Primary Model (Web)
 │                 │                    │                     │                       │
 │── 作業方針相談 ──▶│                    │                     │                       │
 │                 │── 自律質問送信 ────▶│                     │                       │
 │                 │   (IPC/Socket)     │── INJECT_PROMPT ───▶│                       │
 │                 │                    │   (WebSocket)       │── DOM入力 & Enter ───▶│
 │                 │                    │                     │                       │── 思考・応答生成
 │                 │                    │                     │◀── DOM Observer検知 ──│
 │                 │                    │◀─ RESPONSE_CAPTURED─│                       │
 │                 │◀── 助言テキスト ────│                     │                       │
 │                 │                                                                  │
 │                 │── コード自動実装 (VS Code)                                         │
 │◀─ 完了通知 ─────│                                                                  │

```

---

## 6. データ構造定義 (JSON Schema)

```json
{
  "bridge_protocol_version": "1.0.0",
  "session_type": "PRIMARY_LOCAL_HOTLINE",
  "transaction_id": "tx_sync_7701",
  "direction": "LOCAL_TO_PRIMARY",
  "payload": {
    "sender": "local_worker_agent",
    "target": "primary_model",
    "intent": "ARCHITECTURAL_INQUIRY",
    "prompt_text": "Live2Dのキー入力補間処理について、Update内で負荷を抑えつつ滑らかに遷移させるC#ロジックの最適解を提示してください。",
    "context_files": [
      "Assets/Scripts/MotionController.cs"
    ]
  },
  "safety_guard": {
    "execution_level": "RESTRICTED_CODE_GEN",
    "requires_user_approval": false
  }
}

```

---

## 7. 実装フェーズ

* **Phase 1**: ブラウザ拡張機能とローカルPythonプロセス間のWebSocketブリッジ実装（DOMテキスト注入および抽出検証）。
* **Phase 2**: ローカルエージェントの自律質問生成モジュールおよび母艦返答パーサーの実装。
* **Phase 3**: VS Code連携（ファイル自動編集）と安全制御ゲート（ダウンロード遮断・承認プロンプト）の統合。

---
