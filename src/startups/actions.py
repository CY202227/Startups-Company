"""动作模型与命令解析。"""

from __future__ import annotations

from typing import Optional

from .domain import Action
from .rules import ActionType


def parse_action(input_text: str) -> Optional[Action]:
  """将 CLI 输入解析为动作对象。"""
  text = input_text.strip().lower()
  if not text:
    return None
  if text in {"d", "draw", "deck"}:
    return Action(action_type=ActionType.TAKE_FROM_DECK, index=None)
  if text.startswith("m "):
    idx = _parse_index(text)
    if idx is None:
      return None
    return Action(action_type=ActionType.TAKE_FROM_MARKET, index=idx)
  if text.startswith("p "):
    idx = _parse_index(text)
    if idx is None:
      return None
    return Action(action_type=ActionType.PLAY_TO_PORTFOLIO, index=idx)
  if text.startswith("s "):
    idx = _parse_index(text)
    if idx is None:
      return None
    return Action(action_type=ActionType.PLAY_TO_MARKET, index=idx)
  return None


def _parse_index(text: str) -> Optional[int]:
  parts = text.split()
  if len(parts) != 2:
    return None
  try:
    return int(parts[1])
  except ValueError:
    return None
