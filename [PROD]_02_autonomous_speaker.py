import random
import threading
import time
from typing import Callable, Optional


class AutonomousSpeakerEngine:
  """確率変動型無音判定 ＆ 自律マイニング発話エンジン"""

  PROBABILITY_TABLE = {
      1: 0.005,  # 1分: 0.5%
      2: 0.010,  # 2分: 1.0%
      3: 0.015,  # 3分: 1.5%
      4: 0.020,  # 4分: 2.0%
      5: 0.200,  # 5分: 20.0% (変曲点)
      6: 0.250,  # 6分: 25.0%
      7: 0.300,  # 7分: 30.0%
      8: 0.400,  # 8分: 40.0%
      9: 0.500,  # 9分: 50.0%
      10: 1.000,  # 10分: 100.0% (確定発話)
  }

  def __init__(
      self,
      tts_callback: Callable[[str], None],
      miner_callback: Callable[[], str],
  ):
    self.tts_callback = tts_callback
    self.miner_callback = miner_callback
    self.last_activity_time = time.time()
    self.is_running = True
    self.evaluated_minutes = set()

  def record_activity(self):
    """ユーザー入力（音声・テキスト・操作）検知時にタイマーリセット"""
    self.last_activity_time = time.time()
    self.evaluated_minutes.clear()

  def start_loop(self):
    threading.Thread(target=self._monitor_loop, daemon=True).start()

  def _monitor_loop(self):
    while self.is_running:
      time.sleep(1.0)
      elapsed_sec = time.time() - self.last_activity_time
      elapsed_min = int(elapsed_sec // 60)

      if (
          elapsed_min in self.PROBABILITY_TABLE
          and elapsed_min not in self.evaluated_minutes
      ):
        self.evaluated_minutes.add(elapsed_min)
        prob = self.PROBABILITY_TABLE[elapsed_min]
        roll = random.random()

        # 確率抽選判定
        if roll < prob:
          # 当選: バックグラウンドで話題調達 ＆ 発話
          topic_text = self.miner_callback()
          if topic_text:
            self.tts_callback(topic_text)
            self.record_activity()  # 発話完了でリセット