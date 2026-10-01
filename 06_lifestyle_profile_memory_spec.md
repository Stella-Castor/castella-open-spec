```markdown
# Defensive Publication Spec: Autonomous Lifestyle Profile & Memory Decay Engine

## 1. Overview & Defensive Intent
本仕様書は、対話型AIエージェントがユーザーとの自然言語対話から自律的に生活行動・嗜好・経済活動（支出ログ等）のファクトを抽出し、統計的クラスタリングおよび忘却曲線アルゴリズムを用いてプロファイルを動的形成するアーキテクチャを定義する。

## 2. Decoupled Architecture & Backend Binding
本仕様は、プレゼンテーション層や特定のLLM基盤から完全に独立した疎結合アーキテクチャを採用する。
本仕様に完全準拠する実装バックエンドとして、以下のPythonコアモジュールを必須とする。

- **Required Backend Core**: `lifestyle_profile_core.py`
- **Execution Environment**: OS-agnostic Linux standard environment (Python 3.10+, `pathlib` based relative path management).

## 3. Core Protocol & Data Structures

### 3.1 Fact Extraction Event Schema (`EVENT_FACT_EXTRACTED`)
対話中から抽出されたファクトイベントの標準JSONプロトコル。

```json
{
  "event_type": "EVENT_FACT_EXTRACTED",
  "timestamp": "2026-10-01T18:00:00Z",
  "fact_id": "fact_001_camping",
  "category": "lifestyle_activity",
  "action": "camping",
  "metadata": {
    "location": "outdoor",
    "frequency_delta": 1,
    "cost": 0,
    "sentiment": "positive"
  }
}

```

### 3.2 Dynamic Profile & Confidence Threshold

* **Frequency-Based Clustering**: 特定アクション（例: `camping`）の累計検知回数および間隔に基づき、カテゴリ嗜好スコア（Confidence Score: 0.0 ~ 1.0）を動的算出。
* **Decay & Promotion Pipeline**:
* 短期メモリ（Episodic Cache）: 最終アクセス時刻からの経過日数に応じて重要度（Weight）が指数関数的に減衰。
* 長期プロファイル昇格（Long-Term Promotion）: 閾値（例: 頻度 >= 5回、または累積確信度 >= 0.85）を超過したファクトは「恒久プロファイル（Permanent Core Fact）」へ自律昇格。



## 4. Verification Standard

* `lifestyle_profile_core.py` は、外部クラウドに依存せず完全ローカルで動作検証可能であること。
* Windows特有の絶対パスやバックスラッシュを排除し、`pathlib.Path` による相対パス管理を遵守すること。

```

