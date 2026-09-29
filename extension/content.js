// Web-Local Agent Bridge Content Script
(function () {
  const WS_URL = "ws://127.0.0.1:8765";
  let socket = null;
  let isGenerating = false;

  function connect() {
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
      console.log("[Bridge] Connected to Local Bridge Server.");
    };

    socket.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "INJECT_PROMPT") {
          injectAndSubmit(data.text);
        }
      } catch (err) {
        console.error("[Bridge] Failed to parse message:", err);
      }
    };

    socket.onclose = () => {
      console.warn("[Bridge] Connection closed. Reconnecting in 3 seconds...");
      setTimeout(connect, 3000);
    };

    socket.onerror = (err) => {
      console.error("[Bridge] WebSocket Error:", err);
      socket.close();
    };
  }

  // 入力欄へのテキスト注入と送信イベント発火
  function injectAndSubmit(text) {
    const inputField = document.querySelector('div[contenteditable="true"], textarea');
    if (!inputField) {
      console.error("[Bridge] Chat input element not found.");
      return;
    }

    inputField.focus();
    if (inputField.tagName.toLowerCase() === 'textarea') {
      inputField.value = text;
    } else {
      inputField.innerText = text;
    }

    // 入力イベントを発火させてフレームワーク側の状態を更新
    inputField.dispatchEvent(new Event('input', { bubbles: true }));

    setTimeout(() => {
      // Enterキー押下イベントを発火
      const enterEvent = new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        key: 'Enter',
        code: 'Enter',
        keyCode: 13
      });
      inputField.dispatchEvent(enterEvent);
      console.log("[Bridge] Prompt injected and sent.");
      startWatchingResponse();
    }, 300);
  }

  // 回答の生成終了を監視してテキストを抜き出す
  function startWatchingResponse() {
    isGenerating = true;
    const observer = new MutationObserver((mutations, obs) => {
      // 送信ボタンの状態やストリーミング完了アイコンの変化を監視
      const stopButton = document.querySelector('button[aria-label*="停止"], button[aria-label*="Stop"]');
      if (!stopButton && isGenerating) {
        // 生成が完了したと判定
        isGenerating = false;
        obs.disconnect();
        extractAndSendLastResponse();
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  function extractAndSendLastResponse() {
    const responseElements = document.querySelectorAll('.model-response-text, message-content');
    if (responseElements.length === 0) return;

    const latestResponse = responseElements[responseElements.length - 1].innerText;
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: "RESPONSE_CAPTURED",
        text: latestResponse,
        timestamp: Date.now()
      }));
      console.log("[Bridge] Response successfully captured and sent to local agent.");
    }
  }

  // 起動時に接続開始
  connect();
})();
