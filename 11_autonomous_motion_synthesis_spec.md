```markdown
# 11. Autonomous Motion Synthesis Protocol (自律運動合成・骨格制御仕様)

## 1. 概要と開発意図 (Design Intent)
本仕様は、システムの思考・感情出力を、3D人型骨格（VRM / Humanoid）の物理的運動へとリアルタイムに変換・投影するための自律運動合成プロトコルを定義する。

従来のUnity開発における「Animator Controllerのステートマシン肥大化（遷移矢印の手動結線地獄）」および「静的アニメーションファイル（.anim）の大量インポート」による保守性破綻を完全排除する。
Unityを「AIが計算した3D幾何座標を描画するための受動的レンダラー」と位置づけ、**Playables API** による動的グラフ構築と **Direct Transform / IK Override** を統合したステートレスな制御パイプラインを確立する。

---

## 2. 運動合成の数理モデル (Mathematical Formulation)

人型骨格の運動 $M(t)$ は、時間 $t$ における各関節（Bone）の3D座標 $P_i(t) \in \mathbb{R}^3$ および回転クォータニオン $Q_i(t) \in \mathbb{H}$ の時系列行列として定式化される。

$$M(t) = \left\{ \left( P_i(t), Q_i(t) \right) \mid i \in \text{VRM\_Humanoid\_Bones} \right\}$$

本システムでは、以下の3層レイヤーの重み付け合成（Linear Combination & Constraints）によって未知の運動を動的生成する。

1. **基底姿勢空間（Base Pose Space）:**
   少数の基底骨格姿勢ベクトル $B_k$ と、感情・意図に応じた合成係数 $w_k(t)$ による補間合成。
   $$\text{Pose}_{\text{base}}(t) = \sum_{k} w_k(t) \cdot B_k \quad \left( \sum_{k} w_k(t) = 1 \right)$$
2. **生体微小揺らぎ（Micro-dynamics / Perlin Noise）:**
   呼吸、重心動揺、微細な身じろぎを多重周波数のパーリンノイズ関数 $N(t, \omega)$ で動的加算。
3. **物理・幾何拘束層（Kinematic Constraints & Procedural IK）:**
   関節可動域制限（Limit Angle）と、視線注視点（Gaze Target $G(t)$）への逆運動学（CCD-IK / FABRIK）による最終座標拘束。

---

## 3. Unity内部パイプライン (Playables API Architecture)

GUIのアニメーターパレットを用いず、C#スクリプト内で以下の `PlayableGraph` を動的に構築・評価する。


```

[ AnimationClipPlayable (Base Idles) ] ──┐
├─▶ [ AnimationMixerPlayable (Layer 0) ]
[ AnimationClipPlayable (Talk/Gesture)] ─┘                  │ (Dynamic Blending Weight)
▼
[ AnimationScriptPlayable (Layer 1) ]
│ (Procedural Noise Injection)
▼
[ PlayableOutput (VRM Humanoid Animator) ]
│
▼
[ OnAnimatorIK / Rigging Direct Override ]
├─ Head / Eyes LookAt IK (Direct Track)
└─ HumanPoseHandler.SetHumanPose()

---

## 4. 通信スキーマ仕様 (Payload Schema)

AIコア（Linux / Python）からUnity（C#）へ、Local WebSocket（ポート: `8765`）経由でストリーミングされるJSONパケット構造。

```json
{
  "timestamp": 1791200000.123,
  "motion_tag": "Shy",
  "blend_duration": 0.35,
  "emotion_vector": {
    "valence": 0.85,
    "arousal": 0.40,
    "intensity": 0.70
  },
  "kinematics": {
    "gaze_target": { "x": 0.15, "y": 1.25, "z": 1.50 },
    "body_sway_amplitude": 0.04,
    "breathing_rate": 0.28,
    "tension": 0.55
  },
  "procedural_weights": {
    "look_at": 0.85,
    "noise_blend": 0.20
  }
}

```

### フィールド定義

* `motion_tag`: 適用する基底ポーズ識別子（Idle, Talk, Wave, Surprise, Shy等）。
* `blend_duration`: 前姿勢からの遷移にかける補間時間（秒）。`CrossFadeInFixedTime` の引数に直接バインド。
* `emotion_vector`:
* `valence`: 感情価（快 / 不快：-1.0 〜 +1.0）。
* `arousal`: 覚醒度（静寂 / 興奮：0.0 〜 1.0）。
* `intensity`: 表情および動作の増幅率（0.0 〜 1.0）。


* `kinematics`:
* `gaze_target`: カメラまたは注視対象の3次元ローカル/ワールド座標。
* `body_sway_amplitude`: 重心揺らぎの振幅幅。
* `breathing_rate`: 呼吸周期の周波数（Hz）。
* `tension`: 筋肉の緊張度（ポーズの硬さ・戻り速度に影響）。


* `procedural_weights`:
* `look_at`: 視線IKの追従比率（0.0で追従なし、1.0で完全拘束）。
* `noise_blend`: パーリンノイズによる微細運動の加算比率。



---

## 5. VRM標準準拠性 (Portability & Safety)

1. **ボーンマッピングの非依存性:**
VRM規格の `HumanBodyBones` 列挙型（`Head`, `Neck`, `Spine`, `RightUpperArm` 等）に対してのみ座標変換を適用する。独自リグ名への依存を一切排除し、任意のVRMモデルに対して100%の互換性を保証する。
2. **クラッシュセーフティ（ホワイト・ディフェンス連動）:**
通信切断や異常な座標値（NaN, 許容範囲外の巨大座標）を受信した場合、自動的に安全待機姿勢（Neutral Idle）へフェイルセーフ移行し、描画の破綻や関節のねじれを防止する。

```