"""动作约束与阶段流程。"""

from __future__ import annotations

from dataclasses import replace

from startups.domain import Action, CompanyState, MarketCard
from startups.engine import apply_action, setup_game
from startups.rules import ActionType, ErrorCode


def test_take_from_market_blocked_by_anti_monopoly() -> None:
  state = setup_game(player_count=3, seed=1)
  # 直接构造当前市场，并让当前玩家持有公司 0 的反垄断筹码。
  market = (MarketCard(company_id=0, coins=0),)
  companies = tuple(
    CompanyState(company_id=cfg.company_id, anti_monopoly_owner=0)
    if cfg.company_id == 0
    else CompanyState(
      company_id=cfg.company_id,
      anti_monopoly_owner=None,
    )
    for cfg in state.companies
  )
  state = replace(
    state,
    market=market,
    companies=companies,
  )

  result = apply_action(state, 0, Action(action_type=ActionType.TAKE_FROM_MARKET, index=0))
  assert result.code == ErrorCode.INVALID_MOVE
  assert not result.accepted


def test_cannot_take_deck_when_not_enough_capital() -> None:
  state = setup_game(player_count=3, seed=5)
  player = state.current_player_state()
  poor_state_player = replace(
    player,
    cash=0,  # 无法支付市场费用
  )
  state = replace(
    state,
    players=(poor_state_player,) + state.players[1:],
    market=(MarketCard(company_id=0, coins=0),),
  )

  result = apply_action(state, 0, Action(action_type=ActionType.TAKE_FROM_DECK))
  assert result.code == ErrorCode.NOT_ENOUGH_CAPITAL
  assert not result.accepted


def test_play_to_market_forbidden_after_taking_same_company() -> None:
  state = setup_game(player_count=3, seed=7)
  # 强制让当前玩家手上有可控牌，且市场中有一张公司牌。
  state = replace(
    state,
    players=(
      replace(
        state.players[0],
        player_id=0,
        hand=(1, 1),
        portfolio=(0,) * 6,
      ),
    )
    + state.players[1:],
    market=(MarketCard(company_id=1, coins=0),),
    last_took_company=None,
    last_took_from_market=False,
  )

  result = apply_action(
    state,
    0,
    Action(action_type=ActionType.TAKE_FROM_MARKET, index=0),
  )
  assert result.accepted
  assert result.state.stage.name == "PLAY"
  play_result = apply_action(
    result.state,
    0,
    Action(action_type=ActionType.PLAY_TO_MARKET, index=0),
  )
  assert play_result.code == ErrorCode.INVALID_MOVE
  assert not play_result.accepted
