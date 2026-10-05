using System;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;

namespace Castor.Motion
{
    [Serializable]
    public class EmotionVector
    {
        public float valence;
        public float arousal;
        public float intensity;
    }

    [Serializable]
    public class MotionPayload
    {
        public double timestamp;
        public string motion_tag;
        public EmotionVector emotion;
        public Vector3 gaze_target;
        public float blend_duration;
        public float procedural_weight;
    }

    /// <summary>
    /// ステートマシンを介さず、AIストリームから直接VRM人型骨格を自律駆動するブリッジ
    /// </summary>
    [RequireComponent(typeof(Animator))]
    public class AutonomousVRMMotionBridge : MonoBehaviour
    {
        private Animator animator;
        private Vector3 currentGazeTarget = new Vector3(0, 1.3f, 1.0f);
        private float gazeWeight = 0.8f;

        private void Awake()
        {
            animator = GetComponent<Animator>();
        }

        /// <summary>
        /// JSONストリームからパケットを受信した際のディスパッチハンドラ
        /// </summary>
        public void ApplyMotionStream(string jsonString)
        {
            if (string.IsNullOrEmpty(jsonString)) return;

            MotionPayload payload = JsonUtility.FromJson<MotionPayload>(jsonString);
            if (payload == null) return;

            // 1. 動的クロスフェード（GUIステートマシンの遷移矢印を使わない直接ブレンド）
            if (!string.IsNullOrEmpty(payload.motion_tag))
            {
                animator.CrossFadeInFixedTime(payload.motion_tag, payload.blend_duration);
            }

            // 2. 視線注視点の更新
            currentGazeTarget = payload.gaze_target;
            gazeWeight = payload.procedural_weight;
        }

        /// <summary>
        /// プロシージャルIKによる視線・頭部追従（毎フレーム幾何計算）
        /// </summary>
        private void OnAnimatorIK(int layerIndex)
        {
            if (animator == null) return;

            // 頭部・首・瞳をターゲット座標へリアルタイムに追従
            animator.SetLookAtWeight(gazeWeight, 0.4f, 0.7f, 0.0f, 0.5f);
            animator.SetLookAtPosition(currentGazeTarget);
        }
    }
}