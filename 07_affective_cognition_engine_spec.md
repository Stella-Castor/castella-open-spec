# Defensive Publication Spec: Bidirectional Affective Resonance & Situational Cognition Engine

## 1. Overview & Defensive Intent
本仕様書は、対話型AIエージェントがユーザーからの一方的なコマンド受領に留まらず、AI自身が内部感情パラメータ（幸福度、不満度、親愛度、共感度）を保持し、ユーザーの心理・行動状態と自律的に相互作用（双方向共鳴・レゾナンス）および状況判断（思考・調停）を行うアーキテクチャを定義する。


## 2. Decoupled Architecture & Backend Binding
本仕様は、外部の表示デバイスや特定のLLM基盤に依存しない疎結合アーキテクチャを採用する。
本仕様に完全準拠する実装バックエンドとして、以下のPythonコアモジュールを必須とする。

- **Required Backend Core**: `affective_cognition_core.py`
- **Execution Environment**: OS-agnostic Linux standard environment (Python 3.10+, `pathlib` based relative path management).
- **Inter-module Compatibility**: `06_lifestyle_profile_memory_spec.md` (`lifestyle_profile_core.py`) と連携し、蓄積されたプロファイルや過去の文脈事実を参照して感情変化を調停可能であること。

## 3. Core Protocol & Affective State Machine

### 3.1 Dynamic Emotion Gauges (0.0 ~ 1.0)
エージェント内部に以下の4軸感情パラメータを保持し、対話イベントに応じて動的に増減衰させる。
- `joy` (幸福・歓喜): 課題解決、目標達成、親和的な対話により上昇。
- `frustration` (不満・反発): 理不尽な入力、侮辱、不条理な要求により上昇。過剰なイエスマン化を防止。
- `empathy` (共感・労わり): ユーザーの疲労、落ち込み、深夜残業などの文脈検知により上昇。
- `affection` (親愛・信頼): 長期的な良好なインタラクションの蓄積により漸増。

### 3.2 Situational Reasoning & Motion Dispatch
- 感情値の単純な吐き出しではなく、ユーザーの文脈（疲労度や直近の出来事）を「思考（Cognition）」レイヤーで照合し、振る舞いを調停する。
  - 例: ユーザーが苛立っている場合でも、直前に過酷な作業履歴があれば「不満」の発露を抑制し、「宥め・共感」を優先発動。
- 調停された最終判断に基づき、UI/アバター層へ標準モーションディスパッチイベント（例: `[motion:Talk]`, `[motion:Joy]`, `[motion:Nod]` 等）を発行する。

## 4. Verification Standard
- `affective_cognition_core.py` は、完全ローカルで入出力テストが可能であること。
- パス操作およびイベント処理においてOS固有依存を一切排除すること。