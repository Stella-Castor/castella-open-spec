"""
Castor System: 11. Autonomous Motion Core
思考・感情タグおよび注視点座標をUnity VRMブリッジへ非同期配信するエンジンモジュール。
"""

import asyncio
import json
import time
from pathlib import Path

DEFAULT_PORT = 8765
HOST = "127.0.0.1"


async def dispatch_motion(websocket):
    """
    自律エージェントの思考状態に応じた運動制御ストリームを生成・送信する。
    """
    print(f"[MotionCore] Client connected: {websocket.remote_address}")
    try:
        while True:
            # 感情と注視点の計算例（エージェントの内部状態・モーションタグと連動）
            payload = {
                "timestamp": time.time(),
                "motion_tag": "Talk",
                "emotion": {
                    "valence": 0.75,
                    "arousal": 0.50,
                    "intensity": 0.80,
                },
                "gaze_target": {"x": 0.0, "y": 1.3, "z": 1.2},
                "blend_duration": 0.3,
                "procedural_weight": 0.85,
            }

            await websocket.send(json.dumps(payload))
            await asyncio.sleep(1.0)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"[MotionCore] Stream interrupted: {e}")
    finally:
        print(f"[MotionCore] Client disconnected.")


async def start_server():
    import websockets

    print(
        f"[MotionCore] Starting motion server on ws://{HOST}:{DEFAULT_PORT}..."
    )
    async with websockets.serve(dispatch_motion, HOST, DEFAULT_PORT):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\n[MotionCore] Terminated cleanly.")