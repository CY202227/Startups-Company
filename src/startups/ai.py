"""AI 决策策略（单人局）。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from dataclasses import replace
from typing import Optional

from .domain import Action, GameState
from .rules import ActionType, TurnStage


@dataclass(frozen=True)
class AiDecision:
  """AI 决策结果。"""

  action: Action
  policy: str
  reason: str


def choose_action(state: GameState, player_id: int, rng: random.Random) -> AiDecision:
  """在当前回合为单个 AI 玩家选择动作。"""
  policy = rng.choice(["greedy", "anti_pressure"])
  observed_state = _hide_other_hands(state, player_id)
  if observed_state.stage == TurnStage.TAKE:
    decision = _choose_take_action(observed_state, player_id, policy, rng)
  else:
    decision = _choose_play_action(observed_state, player_id, policy, rng)
  return AiDecision(action=decision, policy=policy, reason="auto")


def _hide_other_hands(state: GameState, player_id: int) -> GameState:
  """返回 AI 可见状态：只保留自身手牌，隐藏他人手牌。"""
  players = list(state.players)
  for idx, player in enumerate(players):
    if idx != player_id:
      players[idx] = replace(player, hand=())
  return replace(state, players=tuple(players))


def _company_holder(state: GameState, company_id: int) -> Optional[int]:
  return state.companies[company_id].anti_monopoly_owner


def _deck_payable_cost(state: GameState, player_id: int) -> int:
  cost = 0
  for card in state.market:
    owner = _company_holder(state, card.company_id)
    if owner != player_id:
      cost += 1
  return cost


def _choose_take_action(
  state: GameState,
  player_id: int,
  policy: str,
  rng: random.Random,
) -> Action:
  player = state.current_player_state()
  cost = _deck_payable_cost(state, player_id)
  legal_market = [
    idx
    for idx, card in enumerate(state.market)
    if _company_holder(state, card.company_id) != player_id
  ]

  if not state.deck:
    if legal_market:
      return Action(
        action_type=ActionType.TAKE_FROM_MARKET,
        index=rng.choice(legal_market),
      )
    raise RuntimeError("AI 在抽牌阶段无可用动作。")

  if policy == "anti_pressure":
    # 优先从市场拿高价值筹码，优先减少抽牌成本压力。
    if legal_market:
      best_idx = max(
        legal_market,
        key=lambda idx: state.market[idx].coins,
      )
      if state.market[best_idx].coins > 0:
        return Action(action_type=ActionType.TAKE_FROM_MARKET, index=best_idx)
    if player.cash >= cost:
      return Action(action_type=ActionType.TAKE_FROM_DECK)
    if legal_market:
      best_idx = rng.choice(legal_market)
      return Action(action_type=ActionType.TAKE_FROM_MARKET, index=best_idx)
    return Action(action_type=ActionType.TAKE_FROM_DECK)

  # greedy 策略：默认优先从牌堆拿牌，除非无法支付。
  if legal_market and player.cash < cost:
    best_idx = max(
      legal_market,
      key=lambda idx: state.market[idx].coins,
    )
    return Action(action_type=ActionType.TAKE_FROM_MARKET, index=best_idx)
  return Action(action_type=ActionType.TAKE_FROM_DECK)


def _company_max_others(
  state: GameState,
  player_id: int,
  company_id: int,
) -> int:
  return max(
    player.portfolio[company_id]
    for i, player in enumerate(state.players)
    if i != player_id
  )


def _choose_play_action(
  state: GameState,
  player_id: int,
  policy: str,
  rng: random.Random,
) -> Action:
  player = state.current_player_state()
  if not player.hand:
    raise RuntimeError("AI 在打牌阶段无可用手牌。")

  best_portfolio_indices: list[int] = []
  best_market_indices: list[int] = []
  best_portfolio_score = float("-inf")
  best_market_score = float("-inf")

  for hand_idx, company_id in enumerate(player.hand):
    shares = player.portfolio[company_id]
    opponent_max = _company_max_others(state, player_id, company_id)
    holder = _company_holder(state, company_id)

    if policy == "greedy":
      portfolio_score = shares + 1
      if shares + 1 > opponent_max:
        portfolio_score += 3
      if holder == player_id:
        portfolio_score += 2
      market_score = 1
    else:
      # anti_pressure: 倾向避开可能增加未来被追缴的持股公司，保留对冲性。
      risk_penalty = max(0, opponent_max - shares)
      if holder is not None and holder != player_id:
        risk_penalty += 1
      portfolio_score = -risk_penalty
      market_score = 1
      if holder == player_id:
        portfolio_score += 1

    if portfolio_score > best_portfolio_score:
      best_portfolio_score = portfolio_score
      best_portfolio_indices = [hand_idx]
    elif portfolio_score == best_portfolio_score:
      best_portfolio_indices.append(hand_idx)

    if market_score > best_market_score:
      best_market_score = market_score
      best_market_indices = [hand_idx]
    elif market_score == best_market_score:
      best_market_indices.append(hand_idx)

  if policy == "greedy":
    if best_portfolio_score >= best_market_score:
      return Action(
        action_type=ActionType.PLAY_TO_PORTFOLIO,
        index=rng.choice(best_portfolio_indices),
      )
  else:
    if best_market_score > best_portfolio_score:
      return Action(
        action_type=ActionType.PLAY_TO_MARKET,
        index=rng.choice(best_market_indices),
      )

  return Action(
    action_type=ActionType.PLAY_TO_PORTFOLIO,
    index=rng.choice(best_portfolio_indices),
  )
