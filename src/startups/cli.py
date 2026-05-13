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
from .i18n.catalog import DEFAULT_LOCALE, SUPPORTED_LOCALES, normalize_locale, translate
from .rules import ActionType, DEFAULT_COMPANIES, TurnStage
from .scoring import ScoreSnapshot, compute_scores


def main() -> None:
    """启动本地命令行交互。"""
    parser = argparse.ArgumentParser(description="Startups CLI")
    parser.add_argument("--players", type=int, default=3)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--load", type=Path)
    parser.add_argument(
        "--locale",
        default=DEFAULT_LOCALE,
        choices=tuple(sorted(SUPPORTED_LOCALES)),
        help="语言: zh 或 en",
    )
    parser.add_argument(
        "--single-player",
        action="store_true",
        help="启用单人局：当前玩家(P0)为真人，其余为 AI。",
    )
    args = parser.parse_args()
    locale = normalize_locale(args.locale)

    rng = random.Random(args.seed)
    if args.load is not None:
        with args.load.open("r", encoding="utf-8") as infile:
            payload = json.load(infile)
        state = GameState.from_dict(payload)
    else:
        state = setup_game(args.players, args.seed)

    print(translate(locale, "cli_started"))
    _run_loop(state, args.single_player, rng, locale)


def _run_loop(
    state: GameState,
    single_player: bool,
    rng: random.Random,
    locale: str,
) -> None:
    human_player = 0 if single_player else None
    while not state.is_finished():
        _print_state(state, locale)
        if single_player and state.current_player != human_player:
            try:
                action = _choose_ai_action(state, rng)
                print(
                    translate(
                        locale,
                        "cli_ai_decision",
                        player=state.current_player,
                        action=action.action_type.name,
                    )
                )
            except RuntimeError as error:
                print(translate(locale, "cli_ai_fallback", error=error))
                action = _fallback_ai_action(state)
                if action is None:
                    raise SystemExit(translate(locale, "cli_ai_no_action")) from error
        else:
            if state.stage == TurnStage.TAKE:
                action = _auto_take_action(state)
                if action is not None:
                    print(translate(locale, "cli_auto_take"))
                else:
                    action = _read_action(state, locale)
            else:
                action = _read_action(state, locale)
            if action is None:
                continue
        result = apply_action(state, state.current_player, action)
        if not result.accepted:
            print(_translate_result(locale, result.message))
            continue
        state = result.state

    _, score = compute_scores(state)
    _print_scores(state, score, locale)


def _choose_ai_action(state: GameState, rng: random.Random) -> Action:
    decision = ai.choose_action(state, state.current_player, rng)
    return decision.action


def _fallback_ai_action(state: GameState) -> Optional[Action]:
    player = state.current_player_state()
    if state.stage == TurnStage.TAKE:
        legal_market = []
        for idx, card in enumerate(state.market):
            if (
                state.companies[card.company_id].anti_monopoly_owner
                != state.current_player
            ):
                legal_market.append(idx)
        if state.deck:
            cost = _market_take_cost(state)
            if not legal_market:
                if player.cash >= cost:
                    return Action(action_type=ActionType.TAKE_FROM_DECK)
                return None
            if player.cash >= cost:
                return Action(action_type=ActionType.TAKE_FROM_DECK)
            return Action(
                action_type=ActionType.TAKE_FROM_MARKET,
                index=legal_market[0],
            )
        if legal_market:
            return Action(
                action_type=ActionType.TAKE_FROM_MARKET,
                index=legal_market[0],
            )
        return None
    if player.hand:
        legal_market_plays = [
            idx
            for idx, card in enumerate(player.hand)
            if not (state.last_took_from_market and state.last_took_company == card)
        ]
        if legal_market_plays:
            return Action(
                action_type=ActionType.PLAY_TO_MARKET, index=legal_market_plays[0]
            )
        return Action(action_type=ActionType.PLAY_TO_PORTFOLIO, index=0)
    return None


def _read_action(state: GameState, locale: str) -> Optional[Action]:
    prompt = _prompt(state, locale)
    raw = input(prompt).strip()
    if raw.lower() in {"q", "quit", "exit"}:
        raise SystemExit
    if raw.lower() in {"h", "help"}:
        _print_help(locale)
        return None
    if raw.lower().startswith("state"):
        _print_state(state, locale)
        return None
    action = parse_action(raw)
    if action is None:
        print(translate(locale, "cli_unrecognized_command"))
        return None
    if state.stage == TurnStage.TAKE:
        if action.action_type in {
            ActionType.TAKE_FROM_DECK,
            ActionType.TAKE_FROM_MARKET,
        }:
            return action
        print(translate(locale, "cli_take_only"))
        return None
    if state.stage == TurnStage.PLAY:
        if action.action_type in {
            ActionType.PLAY_TO_PORTFOLIO,
            ActionType.PLAY_TO_MARKET,
        }:
            return action
        print(translate(locale, "cli_play_only"))
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
    cost = _market_take_cost(state)
    if state.current_player_state().cash >= cost:
        return Action(action_type=ActionType.TAKE_FROM_DECK)
    return None


def _market_take_cost(state: GameState) -> int:
    """计算当前玩家从牌堆拿牌时应支付的筹码数。"""
    player = state.current_player
    cost = 0
    for card in state.market:
        owner = state.companies[card.company_id].anti_monopoly_owner
        if owner != player:
            cost += 1
    return cost


def _print_help(locale: str) -> None:
    print(translate(locale, "command_help_title"))
    print(translate(locale, "command_help_draw"))
    print(translate(locale, "command_help_market"))
    print(translate(locale, "command_help_portfolio"))
    print(translate(locale, "command_help_to_market"))
    print(translate(locale, "command_help_state"))
    print(translate(locale, "command_help_quit"))


def _prompt(state: GameState, locale: str) -> str:
    player = state.current_player
    if state.stage == TurnStage.TAKE:
        return translate(locale, "cli_prompt_take", player=player)
    if state.stage == TurnStage.PLAY:
        return translate(locale, "cli_prompt_play", player=player)
    return translate(locale, "cli_prompt_end")


def _company_name(company_id: int) -> str:
    return DEFAULT_COMPANIES[company_id].name


def _print_state(state: GameState, locale: str) -> None:
    print("-" * 80)
    print(translate(locale, "cli_turn", value=state.turn_number))
    print(translate(locale, "cli_stage", value=_stage_text(locale, state.stage.name)))
    print(translate(locale, "cli_current_player", value=state.current_player))
    print(translate(locale, "cli_deck_left", value=len(state.deck)))
    current = state.players[state.current_player]
    token_names = [
        _company_name(cfg.company_id)
        for cfg in state.companies
        if cfg.anti_monopoly_owner == state.current_player
    ]
    if token_names:
        print(
            translate(
                locale,
                "cli_cash_anti",
                cash=current.cash,
                holders=", ".join(token_names),
            )
        )
    else:
        print(translate(locale, "cli_no_anti", cash=current.cash))
    print(translate(locale, "cli_hand_title"))
    for idx, card in enumerate(current.hand):
        total_all = DEFAULT_COMPANIES[card].card_count
        print(
            translate(
                locale,
                "cli_hand_item",
                idx=idx,
                name=_company_name(card),
                total=total_all,
            )
        )
    print(translate(locale, "cli_market_title"))
    if not state.market:
        print(translate(locale, "cli_market_empty"))
    else:
        for idx, card in enumerate(state.market):
            print(
                translate(
                    locale,
                    "cli_market_item",
                    idx=idx,
                    name=_company_name(card.company_id),
                    total=DEFAULT_COMPANIES[card.company_id].card_count,
                    coins=card.coins,
                )
            )
    print(translate(locale, "cli_token_title"))
    for cfg in state.companies:
        owner = state.companies[cfg.company_id].anti_monopoly_owner
        if owner is None:
            continue
        print(translate(locale, "cli_token_row", name=_company_name(cfg.company_id), value=owner))
    print(translate(locale, "cli_actions_title"), end=" ")
    if state.stage == TurnStage.TAKE:
        options = translate(locale, "cli_actions_take")
        if state.market:
            options = translate(locale, "cli_actions_take_market")
        print(options)
    elif state.stage == TurnStage.PLAY:
        print(translate(locale, "cli_actions_play"))
    print(translate(locale, "cli_help_tip"))


def _print_scores(state: GameState, score: ScoreSnapshot, locale: str) -> None:
    print("=" * 80)
    print(translate(locale, "cli_score_title"))
    for pid, player in enumerate(state.players):
        print(
            translate(
                locale,
                "cli_score_row",
                idx=pid,
                cash=player.cash,
                flipped=player.flipped_coins,
                penalty=player.penalty,
                score=score.scores[pid],
            )
        )
    if score.winner is None:
        print(translate(locale, "cli_tie"))
    else:
        print(translate(locale, "cli_champion", winner=score.winner))
    print(translate(locale, "cli_payment_title"))
    for item in score.payouts:
        print(
            translate(
                locale,
                "cli_payment_row",
                payer=item.payer_id,
                holder=item.holder_id,
                paid=item.paid,
                required=item.required,
                name=_company_name(item.company_id),
            )
        )


def _translate_result(locale: str, raw_message: str) -> str:
    if raw_message.startswith("engine_"):
        if "|" in raw_message:
            key, raw_params = raw_message.split("|", 1)
            parts = raw_params.split(",") if raw_params else []
            params = {}
            for part in parts:
                if "=" in part:
                    name, value = part.split("=", 1)
                    params[name] = value
            return translate(locale, key, **params)
        return translate(locale, raw_message)
    return raw_message


def _stage_text(locale: str, stage: str) -> str:
    if stage == TurnStage.TAKE.name:
        return translate(locale, "stage_take")
    if stage == TurnStage.PLAY.name:
        return translate(locale, "stage_play")
    if stage == TurnStage.FINISHED.name:
        return translate(locale, "stage_finished")
    return stage


if __name__ == "__main__":
    main()
