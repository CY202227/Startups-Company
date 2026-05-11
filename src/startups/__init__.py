"""Startups 桌游核心引擎。"""

from .engine import apply_action, setup_game
from .scoring import ScoreSnapshot, compute_scores
from .rules import ActionType, ErrorCode, GameRules, TurnStage

__all__ = [
  "ActionType",
  "apply_action",
  "compute_scores",
  "ErrorCode",
  "GameRules",
  "ScoreSnapshot",
  "setup_game",
  "TurnStage",
]
