"""命令行运行入口。"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Optional

from . import ai
from .actions import parse_action
from .domain import Action
from .domain import GameState
from .engine import apply_action, setup_game
from .rules import ActionType, DEFAULT_COMPANIES, TurnStage
from .scoring import ScoreSnapshot, compute_scores


def main() -> None:
  """启动本地命令行交互。"""
  parser = argparse.ArgumentParser(description="Startups CLI")
  parser.add_argument("--players", type=int, default=3)
  parser.add_argument("--seed", type=int, default=None)
  parser.add_argument("--load", type=Path)
  parser.add_argument(
    "--single-player",
    action="store_true",
    help="启用单人局：当前玩家(P0)为真人，其余为 AI。",
  )
  args = parser.parse_args()

  rng = random.Random(args.seed)
  if args.load is not None:
    with args.load.open("r", encoding="utf-8") as infile:
      payload = json.load(infile)
    state = GameState.from_dict(payload)
  else:
    state = setup_game(args.players, args.seed)

  print("游戏已开始：输入 help 查看可用命令。")
  _run_loop(state, args.single_player, rng)


def _run_loop(
  state: GameState,
  single_player: bool,
  rng: random.Random,
) -> None:
  human_player = 0 if single_player else None
  while not state.is_finished():
    _print_state(state)
    if single_player and state.current_player != human_player:
      try:
        action = _choose_ai_action(state, rng)
        print(
          f"[AI-P{state.current_player}] 决策: {action.action_type.name}",
        )
      except RuntimeError as error:
        print(f"[AI] 决策失败，使用兜底策略：{error}")
        action = _fallback_ai_action(state)
        if action is None:
          raise SystemExit("AI 无法进行可行动作，游戏终止。") from error
    else:
      if state.stage == TurnStage.TAKE:
        action = _auto_take_action(state)
        if action is not None:
          print("[AUTO] 仅能抽牌，已自动执行 d")
        else:
          action = _read_action(state)
      else:
        action = _read_action(state)
      if action is None:
        continue
    result = apply_action(state, state.current_player, action)
    if not result.accepted:
      print(f"非法动作：{result.message}")
      continue
    state = result.state

  _, score = compute_scores(state)
  _print_scores(state, score)


def _choose_ai_action(state: GameState, rng: random.Random) -> Action:
  decision = ai.choose_action(state, state.current_player, rng)
  return decision.action


def _fallback_ai_action(state: GameState) -> Optional[Action]:
  player = state.current_player_state()
  if state.stage == TurnStage.TAKE:
    if state.deck:
      return Action(action_type=ActionType.TAKE_FROM_DECK)
    for idx, card in enumerate(state.market):
      owner = state.companies[card.company_id].anti_monopoly_owner
      if owner != state.current_player:
        return Action(
          action_type=ActionType.TAKE_FROM_MARKET,
          index=idx,
        )
    return None
  if player.hand:
    return Action(
      action_type=ActionType.PLAY_TO_MARKET,
      index=0,
    )
  return None


def _read_action(state: GameState) -> Optional[Action]:
  prompt = _prompt(state)
  raw = input(prompt).strip()
  if raw.lower() in {"q", "quit", "exit"}:
    raise SystemExit
  if raw.lower() in {"h", "help"}:
    _print_help()
    return None
  if raw.lower().startswith("state"):
    _print_state(state)
    return None
  action = parse_action(raw)
  if action is None:
    print("无法识别命令。输入 help 查看。")
    return None
  if state.stage == TurnStage.TAKE:
    if action.action_type in {
      ActionType.TAKE_FROM_DECK,
      ActionType.TAKE_FROM_MARKET,
    }:
      return action
    print("当前阶段只能执行拿牌动作。")
    return None
  if state.stage == TurnStage.PLAY:
    if action.action_type in {
      ActionType.PLAY_TO_PORTFOLIO,
      ActionType.PLAY_TO_MARKET,
    }:
      return action
    print("当前阶段只能执行打牌动作。")
    return None
  return None


def _auto_take_action(state: GameState) -> Optional[Action]:
  """当 TAKE 阶段只有抽牌可行时返回自动动作。"""
  if state.stage != TurnStage.TAKE or not state.deck:
    return None
  for card in state.market:
    holder = state.companies[card.company_id].anti_monopoly_owner
    if holder != state.current_player:
      return None
  return Action(action_type=ActionType.TAKE_FROM_DECK)


def _print_help() -> None:
  print("命令说明：")
  print(" d / draw             从牌堆拿牌")
  print(" m <idx>              从市场拿牌，例如 m 0")
  print(" p <idx>              打到个人区域，例如 p 1")
  print(" s <idx>              打到市场，例如 s 1")
  print(" state                打印当前状态")
  print(" q                    退出")


def _prompt(state: GameState) -> str:
  player = state.current_player
  if state.stage == TurnStage.TAKE:
    return f"[P{player}] TAKE > "
  if state.stage == TurnStage.PLAY:
    return f"[P{player}] PLAY > "
  return "[END] "


def _company_name(company_id: int) -> str:
  return DEFAULT_COMPANIES[company_id].name


def _print_state(state: GameState) -> None:
  print("-" * 80)
  print(f"回合: {state.turn_number}")
  print(f"阶段: {state.stage.name}")
  print(f"当前玩家: P{state.current_player}")
  print(f"抽牌堆剩余: {len(state.deck)}")
  current = state.players[state.current_player]
  token_names = [
    _company_name(cfg.company_id)
    for cfg in state.companies
    if cfg.anti_monopoly_owner == state.current_player
  ]
  if token_names:
    print(f"现金: {current.cash} | 持有反垄断: {', '.join(token_names)}")
  else:
    print(f"现金: {current.cash} | 持有反垄断: 无")
  print("手牌:")
  for idx, card in enumerate(current.hand):
    total_all = DEFAULT_COMPANIES[card].card_count
    print(
      f"  {idx}: {_company_name(card)} "
      f"[总量:{total_all}]"
    )
  print("市场:")
  if not state.market:
    print("  空")
  else:
    for idx, card in enumerate(state.market):
      print(
        f"  {idx}: {_company_name(card.company_id)} "
        f"(coins:{card.coins})",
      )
  print("反垄断持有人:")
  for cfg in state.companies:
    owner = state.companies[cfg.company_id].anti_monopoly_owner
    if owner is None:
      continue
    print(f"  {_company_name(cfg.company_id)} -> P{owner}")
  print("可行动作：", end=" ")
  if state.stage == TurnStage.TAKE:
    options = "d"
    if state.market:
      options += ", m <idx>"
    print(options)
  elif state.stage == TurnStage.PLAY:
    print("p <idx> 或 s <idx>")
  print("输入 help 可查看详细命令。")


def _print_scores(state: GameState, score: ScoreSnapshot) -> None:
  print("=" * 80)
  print("结算完成")
  for pid, player in enumerate(state.players):
    print(
      f"P{pid}: cash={player.cash}, "
      f"flipped={player.flipped_coins}, "
      f"penalty={player.penalty}, score={score.scores[pid]}",
    )
  if score.winner is None:
    print("平局")
  else:
    print(f"冠军：P{score.winner}")
  print("支付明细:")
  for item in score.payouts:
    print(
      f"  P{item.payer_id} -> P{item.holder_id}: "
      f"{item.paid}/{item.required} for 公司 {_company_name(item.company_id)}",
    )


if __name__ == "__main__":
  main()
