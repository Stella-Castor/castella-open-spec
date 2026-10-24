"""
Triune Box Architecture - Common Interfaces
Specification: 12_triune_box_architecture_spec.md
Standards: OS-independent via pathlib, Linux/Docker ready.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class TaskDomain(Enum):
    """汎用タスク領域の定義"""
    CONVERSATION = "conversation"
    REASONING = "reasoning"
    MODELING_3D = "modeling_3d"
    AVATAR_MOTION = "avatar_motion"
    CODING = "coding"
    DATA_ANALYSIS = "data_analysis"


@dataclass
class IdentityContext:
    """抽象化されたエージェント規範（固有名詞は外部設定から注入）"""
    agent_id: str = "Agent-Core"
    operator_id: str = "Operator"
    security_policy: str = "Strict IP Protection / Local Isolated Execution"


class BaseSoul(ABC):
    """【1. 魂ボックスの共通型】"""
    @abstractmethod
    def get_system_context(self, domain: TaskDomain) -> str:
        """思考エンジンへ注入するアイデンティティ・規範コンテキストを生成"""
        pass


class BaseBrain(ABC):
    """【2. 脳ボックスの共通型】"""
    @abstractmethod
    def route_and_think(self, prompt: str, domain: TaskDomain) -> str:
        """領域に応じたモデルを選定し、魂コンテキストをバインドして推論"""
        pass


class BaseFunctionalAdapter(ABC):
    """【3. 機能ボックス（アダプター）の共通型】"""
    def __init__(self, domain: TaskDomain):
        self.domain = domain

    @abstractmethod
    def execute(self, payload: Any) -> bool:
        """脳からディスパッチされた命令ペイロードを実行"""
        pass