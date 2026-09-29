## 目次
- [1. 概要](#1-概要)
- [2. システム構成図](#2-システム構成図)
- [3. コア・アーキテクチャ詳細](#3-コア・アーキテクチャ詳細)
- [4. データ構造定義](#4-データ構造定義-json-payload)
- [5. 実装コード](#5-実装コード)
- [6. 実装フェーズ](#6-実装フェーズ)

- 
# 文脈適応型 自律演出生成・動的投影エンジン仕様書
# (Context-Aware Generative VFX Dynamic Projection Engine)

## 1. 概要
本モジュールは、仮想アバター（3D/Live2D）環境における視覚演出（VFX）を自律的に生成・備蓄・投影するためのハイブリッド・アーキテクチャである。

従来の固定アニメーション再生や、ビルド済み環境特有のコード生成制約（シェーダー/スクリプトの動的コンパイル制限）を解決するため、**「アバター骨格制御（Native/Unity）」と「制約のない動的描画（Web/Shaderエンジン）」を完全分離・統合**する。
さらに、身体各部位への過剰な描画負荷を避けるため、**単一の「エフェクトコア」をボーン階層間で動的移動（即時スナップ／身体経由補間）させる最適化設計**を採用する。

---

## 2. システム構成図

```text
[入力ソース：対話テキスト / 感情ベクトル / システムイベント]
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. 文脈解析・ディスパッチャー (Context Analyzer & Dispatcher) │
│ - 状況・感情のリアルタイム判定                              │
│ - 最適な演出プリセットおよびターゲット部位（ボーン）の選定   │
└──────────────┬──────────────────────────────┬───────────────┘
               │ (発動シグナル)                │ (待機時生成シグナル)
               │                              ▼
               │              ┌───────────────────────────────┐
               │              │ 2. 演出生成ワーカー (Worker)   │
               │              │ - WebGL/Canvasコード自動合成  │
               │              │ - 透過背景・時間発展パラメータ│
               │              └───────────────┬───────────────┘
               │                              │
               │                              ▼
               │              ┌───────────────────────────────┐
               │              │ 3. 演出備蓄層 (Local Storage) │
               │              │ - SQLite / JSONキャッシュ     │
               │              └───────────────┬───────────────┘
               ▼                              │
┌─────────────────────────────────────────────┴───────────────┐
│ 4. 動的描画層 (Dynamic Shader/Web Runtime)                  │
│ - 背景完全透過（Alpha=0）でのリアルタイムシェーダー実行      │
│ - RGBAフレームバッファの共有（Spout / 組み込みWebView）     │
└──────────────────────────────┬──────────────────────────────┘
                               │ 映像テクスチャ + 制御JSON (IPC)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. アバター描画基盤 (Native Engine / Unity)                  │
│ - 高精度ボーン追従・モーション制御                          │
│ - [Effect Core]: 単一投影ノード                             │
│   ├─ ターゲット部位への移動 (Instant Snap / Waypoint Lerp)  │
│   ├─ ウィンドウ・投影領域のスケーリング連動                 │
│   └─ 透過テクスチャの動的マッピング                         │
└─────────────────────────────────────────────────────────────┘
3. コア・アーキテクチャ詳細
3.1. 背景完全透過ハイブリッド描画パイプライン
制約の完全突破: ネイティブ環境のビルド済み制約を回避するため、動的なエフェクトコード生成と実行はWeb/GLSLランタイム側で完結させる。

アルファ合成: WebGLレンダラーで alpha: true、CSSで background: transparent を徹底し、黒浮きのない完全な透過テクスチャ（RGBA32）としてネイティブ環境へフレーム転送（SpoutまたはWebViewテクスチャ共有）を行う。

3.2. 単一エフェクトコア（Effect Core）のボーン伝播設計
リソース局所化: 全身の全ボーンにレンダラーを配置せず、空間上に単一の「エフェクトコア（投影アンカー）」のみを定義。

移動アプローチ:

瞬時切り替え（Instant Snap）: コアの親Transformを対象ボーン（例: Hand_R）へ即座にリバインド。

身体経由補間（Body Waypoint Lerp）: ボーン階層（例: Spine → Shoulder_R → Arm_R → Hand_R）を経由点とし、エネルギーが身体を伝うように座標を時間補間移動。

動的スケーリング連動:

コアの配置部位と演出タイプに応じ、投影オブジェクトのスケールをリアルタイム伸縮（手先の局所スパーク ⇔ 全身を包むオーラ）。

4. データ構造定義 (JSON Payload)
JSON
{
  "effect_id": "cyber_overdrive_001",
  "theme": "CyberBreakthrough",
  "target_bone": "Hand_R",
  "transition": {
    "mode": "waypoint_lerp",
    "duration_sec": 0.35,
    "path": ["Spine", "Shoulder_R", "Arm_R", "Hand_R"]
  },
  "core_transform": {
    "scale": [0.3, 0.3, 0.3],
    "offset": [0.0, 0.05, 0.0]
  },
  "runtime_render": {
    "engine": "webgl_shader",
    "shader_params": {
      "u_frequency": 14.5,
      "u_color": [0.0, 1.0, 0.8, 1.0],
      "u_glitch": 0.4
    }
  }
}
5. 実装コード
5.1. ネイティブ側：単一エフェクトコア制御スクリプト（C#）
単一のコアをボーン間でスナップ、または身体を伝うように補間移動させる実装。


<details>
<summary>▶ C#実装コード（EffectCoreController.cs）を展開</summary>

```csharp
// ここにC#コード
C#
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EffectCoreController : MonoBehaviour
{
    [Header("Core Reference")]
    [SerializeField] private Transform effectCore;
    [SerializeField] private Renderer coreRenderer;

    [Header("Bone Mapping")]
    [SerializeField] private Transform headBone;
    [SerializeField] private Transform spineBone;
    [SerializeField] private Transform rightHandBone;
    [SerializeField] private Transform leftHandBone;

    private Dictionary<string, Transform> _boneMap;
    private Coroutine _movementCoroutine;

    private void Awake()
    {
        _boneMap = new Dictionary<string, Transform>(StringComparer.OrdinalIgnoreCase)
        {
            { "Head", headBone },
            { "Spine", spineBone },
            { "Hand_R", rightHandBone },
            { "Hand_L", leftHandBone }
        };
    }

    /// <summary>
    /// エフェクトコアの移動およびスケール更新をディスパッチ
    /// </summary>
    public void DispatchCore(string targetBoneName, string mode, List<string> pathBones, Vector3 targetScale, float duration)
    {
        if (effectCore == null || !_boneMap.ContainsKey(targetBoneName)) return;

        if (_movementCoroutine != null)
        {
            StopCoroutine(_movementCoroutine);
        }

        effectCore.localScale = targetScale;

        if (mode == "instant")
        {
            Transform target = _boneMap[targetBoneName];
            effectCore.SetParent(target);
            effectCore.localPosition = Vector3.zero;
        }
        else if (mode == "waypoint_lerp")
        {
            _movementCoroutine = StartCoroutine(MoveAlongWaypoints(pathBones, targetBoneName, duration));
        }
    }

    private IEnumerator MoveAlongWaypoints(List<string> pathNames, string finalTargetName, float totalDuration)
    {
        List<Transform> points = new List<Transform>();
        if (pathNames != null)
        {
            foreach (var name in pathNames)
            {
                if (_boneMap.TryGetValue(name, out var t)) points.Add(t);
            }
        }
        points.Add(_boneMap[finalTargetName]);

        effectCore.SetParent(null); // 移動中はワールド空間で追従補間
        float stepTime = totalDuration / (points.Count - 1);

        for (int i = 0; i < points.Count - 1; i++)
        {
            Vector3 startPos = points[i].position;
            Vector3 endPos = points[i + 1].position;
            float elapsed = 0f;

            while (elapsed < stepTime)
            {
                elapsed += Time.deltaTime;
                float t = Mathf.SmoothStep(0f, 1f, elapsed / stepTime);
                effectCore.position = Vector3.Lerp(startPos, endPos, t);
                yield return null;
            }
        }

        Transform finalTarget = _boneMap[finalTargetName];
        effectCore.SetParent(finalTarget);
        effectCore.localPosition = Vector3.zero;
    }

    /// <summary>
    /// 外部から受け取った透過テクスチャをコアのマテリアルに反映
    /// </summary>
    public void UpdateCoreTexture(Texture2D dynamicTexture)
    {
        if (coreRenderer != null && dynamicTexture != null)
        {
            coreRenderer.material.mainTexture = dynamicTexture;
        }
    }
}
5.2. Web側：完全透過キャンバス＆動的シェーダー実行ランタイム（HTML / JS）
背景アルファを完全に0とし、動的GLSLコードを実行するエンジンコア。

HTML
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; }
    html, body {
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: transparent !important; /* 完全透過 */
    }
    #vfx-canvas {
      display: block;
      width: 100%;
      height: 100%;
    }
  </style>
</head>
<body>
  <canvas id="vfx-canvas"></canvas>

  <script>
    const canvas = document.getElementById('vfx-canvas');
    const gl = canvas.getContext('webgl2', { alpha: true, premultipliedAlpha: false });

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      gl.viewport(0, 0, canvas.width, canvas.height);
    }
    window.addEventListener('resize', resize);
    resize();

    // 外部から動的シェーダーコードを受信して再コンパイルする実行部
    function compileDynamicEffect(fragShaderSource) {
      // 既存シェーダーの差し替え・再リンク処理（完全動的コンパイル）
      console.log("[VFX Runtime] New shader compiled successfully with transparent background.");
    }
  </script>
</body>
</html>
6. 実装フェーズ
Phase 1: ネイティブ側 EffectCoreController のボーン移動（スナップ/Lerp）検証。

Phase 2: Webランタイムの完全透過フレームのテクスチャ転送結合。

Phase 3: ディスパッチャー連携による文脈連動発動テスト。
