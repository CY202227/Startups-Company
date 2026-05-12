"""结算与积分计算。"""

from __future__ import annotations

from dataclasses import replace
from dataclasses import dataclass
from typing import Optional

from .domain import GameState, PlayerState
from .rules import DEFAULT_COMPANIES


@dataclass(frozen=True)
class Payout:
  """单次支付记录。"""

  payer_id: int
  holder_id: int
  company_id: int
  paid: int
  required: int


@dataclass(frozen=True)
class ScoreSnapshot:
  """某回合结算结果。"""

  scores: tuple[int, ...]
  payouts: tuple[Payout, ...]
  winner: Optional[int]


def compute_scores(state: GameState) -> tuple[GameState, ScoreSnapshot]:
  """返回结算后状态和积分。"""
  players = list(state.players)
  payouts: list[Payout] = []

  # 对每家公司进行股东收益结算。
  for company_id in range(len(DEFAULT_COMPANIES)):
    players_by_stock = [
      (idx, player.portfolio[company_id]) for idx, player in enumerate(players)
    ]
    max_stock = max(stock for _, stock in players_by_stock)
    if max_stock <= 0:
      continue
    top = [idx for idx, stock in players_by_stock if stock == max_stock]
    if len(top) != 1:
      # 平分导致无赢家，不付息。
      continue
    holder_id = top[0]
    for payer_id, stock in players_by_stock:
      if payer_id == holder_id or stock >= max_stock:
        continue
      if stock == 0:
        continue
      required = stock
      payer = players[payer_id]
      paid = min(payer.cash, required)
      unpaid = required - paid
      if paid > 0:
        players[payer_id] = replace(payer, cash=payer.cash - paid)
        holder = players[holder_id]
        players[holder_id] = replace(
          holder,
          flipped_coins=holder.flipped_coins + paid,
          history=holder.history + (f"earn:{company_id}:{paid}",),
        )
      if unpaid:
        holder = players[payer_id]
        players[payer_id] = replace(
          holder,
          penalty=holder.penalty - unpaid,
          history=holder.history + (f"unpaid:{company_id}:{unpaid}",),
        )
      payouts.append(
        Payout(
          payer_id=payer_id,
          holder_id=holder_id,
          company_id=company_id,
          paid=paid,
          required=required,
        )
      )

  scores = tuple(_score_player(player) for player in players)
  winner = _winner(scores)
  return replace(state, players=tuple(players)), ScoreSnapshot(
    scores=scores,
    payouts=tuple(payouts),
    winner=winner,
  )


def _score_player(player: PlayerState) -> int:
  return player.cash + player.flipped_coins * 3 + player.penalty


def _winner(scores: tuple[int, ...]) -> Optional[int]:
  if not scores:
    return None
  best = max(scores)
  contenders = [idx for idx, score in enumerate(scores) if score == best]
  if len(contenders) != 1:
    return None
  return contenders[0]
