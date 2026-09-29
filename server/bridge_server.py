"""
ローカル・エージェント通信ブリッジサーバー
(Local Agent Communication Bridge Server)
"""

import asyncio
import json
from pathlib import Path
import websockets

CONNECTED_CLIENTS = set()

async def handler(websocket):
    CONNECTED_CLIENTS.add(websocket)
    print(f"[Server] ブラウザ拡張機能が接続されました: {websocket.remote_address}")
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "RESPONSE_CAPTURED":
                response_text = data.get("text", "")
                print("\n[Server] === 母艦からの応答を受信 ===")
                print(f"受信文字数: {len(response_text)} 文字")
                print("================================")
                
                # 受信ログをローカルの相対パスで保存
                log_dir = Path("logs")
                log_dir.mkdir(parents=True, exist_ok=True)
                with open(log_dir / "latest_response.txt", "w", encoding="utf-8") as f:
                    f.write(response_text)
                    
    except websockets.exceptions.ConnectionClosed:
        print("[Server] ブラウザ拡張機能との接続が切断されました。")
    finally:
        CONNECTED_CLIENTS.remove(websocket)

async def test_send_prompt():
    """ターミナルからテスト用プロンプトを注入するためのループ"""
    await asyncio.sleep(2)
    while True:
        prompt = await asyncio.to_thread(input, "\n[送信テスト] 母艦へ送るテキストを入力 (qで終了): ")
        if prompt.lower() == 'q':
            break
        if not CONNECTED_CLIENTS:
            print("[Server] エラー: ブラウザ拡張機能が接続されていません。")
            continue
            
        payload = json.dumps({
            "type": "INJECT_PROMPT",
            "text": prompt
        })
        for client in CONNECTED_CLIENTS:
            await client.send(payload)
        print("[Server] ブラウザ側へプロンプトを送信しました。")

async def main():
    server = await websockets.serve(handler, "127.0.0.1", 8765)
    print("[Server] ローカルブリッジサーバー起動 (ws://127.0.0.1:8765)")
    await asyncio.gather(server.wait_closed(), test_send_prompt())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Server] サーバーを終了しました。")
