"""核心状态机。"""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Sequence

from .domain import (
    Action,
    ActionResult,
    CompanyState,
    GameState,
    MarketCard,
    PlayerState,
)
from .rules import ActionType, ErrorCode, GameRules, TurnStage
from .rules import DEFAULT_COMPANIES


def setup_game(player_count: int, seed: int | None = None) -> GameState:
    """创建一局新游戏。"""
    rules = GameRules(player_count=player_count)
    if not (rules.min_players <= player_count <= rules.max_players):
        raise ValueError(
            f"Player count must be in [{rules.min_players}, {rules.max_players}].",
        )

    rng = random.Random(seed)
    deck = _build_deck(rng)
    deck = deck[rules.remove_from_deck :]
    deck = tuple(deck)

    hand_size = rules.start_hand_size
    players: list[PlayerState] = []
    for player_id in range(player_count):
        hand = deck[player_id * hand_size : (player_id + 1) * hand_size]
        players.append(
            PlayerState(
                player_id=player_id,
                cash=rules.starting_capital,
                hand=hand,
                portfolio=(0,) * len(DEFAULT_COMPANIES),
            )
        )
    deck = deck[player_count * hand_size :]

    companies = tuple(
        CompanyState(company_id=cfg.company_id, anti_monopoly_owner=None)
        for cfg in DEFAULT_COMPANIES
    )

    return GameState(
        rules=rules,
        players=tuple(players),
        deck=deck,
        market=(),
        companies=companies,
        stage=TurnStage.TAKE,
        current_player=0,
        turn_number=1,
        last_took_company=None,
        last_took_from_market=False,
        game_end_triggered=False,
        events=("game_started",),
    )


def apply_action(
    state: GameState,
    player_id: int,
    action: Action,
) -> ActionResult:
    """执行一个动作并返回新状态。"""
    if state.is_finished():
        return ActionResult(
            state=state,
            code=ErrorCode.INVALID_STATE,
            message="engine_game_ended",
            accepted=False,
        )
    if player_id != state.current_player:
        return ActionResult(
            state=state,
            code=ErrorCode.NOT_YOUR_TURN,
            message="engine_not_your_turn",
            accepted=False,
        )

    if action.action_type in {ActionType.TAKE_FROM_DECK, ActionType.TAKE_FROM_MARKET}:
        if state.stage != TurnStage.TAKE:
            return ActionResult(
                state=state,
                code=ErrorCode.INVALID_PHASE,
                message="engine_invalid_take_stage",
                accepted=False,
            )
        if action.action_type == ActionType.TAKE_FROM_DECK:
            return _take_from_deck(state)
        return _take_from_market(state, action.index)

    if action.action_type in {
        ActionType.PLAY_TO_PORTFOLIO,
        ActionType.PLAY_TO_MARKET,
    }:
        if state.stage != TurnStage.PLAY:
            return ActionResult(
                state=state,
                code=ErrorCode.INVALID_PHASE,
                message="engine_invalid_play_stage",
                accepted=False,
            )
        if action.action_type == ActionType.PLAY_TO_PORTFOLIO:
            return _play_to_portfolio(state, action.index)
        return _play_to_market(state, action.index)

    return ActionResult(
        state=state,
        code=ErrorCode.INVALID_MOVE,
        message="engine_unknown_action",
        accepted=False,
    )


def _build_deck(rng: random.Random) -> tuple[int, ...]:
    cards: list[int] = []
    for idx, cfg in enumerate(DEFAULT_COMPANIES):
        cards.extend([idx] * cfg.card_count)
    rng.shuffle(cards)
    return tuple(cards)


def _take_from_deck(state: GameState) -> ActionResult:
    player = state.current_player_state()
    if not state.deck:
        return ActionResult(
            state=state,
            code=ErrorCode.INVALID_STATE,
            message="engine_deck_empty",
            accepted=False,
        )

    payable = 0
    for card in state.market:
        owner = _company_holder(state, card.company_id)
        if owner != state.current_player:
            payable += 1
    if player.cash < payable:
        return ActionResult(
            state=state,
            code=ErrorCode.NOT_ENOUGH_CAPITAL,
            message="engine_need_cash",
            accepted=False,
        )

    drawn = state.deck[0]
    new_deck = state.deck[1:]
    new_market = tuple(
        _add_coin(
            card, exempt=_company_holder(state, card.company_id) == state.current_player
        )
        for card in state.market
    )
    new_hand = player.hand + (drawn,)
    new_player = replace(
        player,
        cash=player.cash - payable,
        hand=new_hand,
        history=player.history + (f"take_deck:{drawn}",),
    )
    players = list(state.players)
    players[state.current_player] = new_player
    game_end = len(new_deck) == 0

    next_stage = TurnStage.PLAY
    events = state.events + (
        f"P{state.current_player} take_deck card={drawn} pay={payable}",
    )
    return ActionResult(
        state=replace(
            state,
            players=tuple(players),
            deck=new_deck,
            market=new_market,
            last_took_company=drawn,
            last_took_from_market=False,
            game_end_triggered=game_end,
            stage=next_stage,
            events=events,
        ),
        code=ErrorCode.OK,
        message="engine_market_taken",
        accepted=True,
    )


def _take_from_market(state: GameState, index: int | None) -> ActionResult:
    if index is None:
        return ActionResult(
            state=state,
            code=ErrorCode.INVALID_INDEX,
            message="engine_require_market_index",
            accepted=False,
        )
    if not 0 <= index < len(state.market):
        return ActionResult(
            state=state,
            code=ErrorCode.INVALID_INDEX,
            message="engine_market_oob",
            accepted=False,
        )

    card = state.market[index]
    if _company_holder(state, card.company_id) == state.current_player:
        return ActionResult(
            state=state,
            code=ErrorCode.INVALID_MOVE,
            message="engine_anti_monopoly_restrict",
            accepted=False,
        )

    new_market = tuple(
        existing
        for existing_idx, existing in enumerate(state.market)
        if existing_idx != index
    )
    player = state.current_player_state()
    new_hand = player.hand + (card.company_id,)
    if card.coins:
        # 市场上的代价筹码会一并拿走。
        new_player = replace(
            player,
            cash=player.cash + card.coins,
            hand=new_hand,
            history=player.history + (f"take_market:{card.company_id}:{card.coins}",),
        )
    else:
        new_player = replace(
            player,
            hand=new_hand,
            history=player.history + (f"take_market:{card.company_id}:0",),
        )
    players = list(state.players)
    players[state.current_player] = new_player
    events = state.events + (
        f"P{state.current_player} take_market idx={index} company={card.company_id} coins={card.coins}",
    )
    return ActionResult(
        state=replace(
            state,
            players=tuple(players),
            market=new_market,
            last_took_company=card.company_id,
            last_took_from_market=True,
            game_end_triggered=state.game_end_triggered,
            stage=TurnStage.PLAY,
            events=events,
        ),
        code=ErrorCode.OK,
        message="engine_take_success",
        accepted=True,
    )


def _play_to_portfolio(state: GameState, hand_index: int | None) -> ActionResult:
    if hand_index is None:
        return ActionResult(
            state=state,
            code=ErrorCode.INVALID_INDEX,
            message="engine_require_hand_index",
            accepted=False,
        )
    player = state.current_player_state()
    if not player.hand:
        return ActionResult(
            state=state,
            code=ErrorCode.INVALID_STATE,
            message="engine_hand_empty",
            accepted=False,
        )
    if not 0 <= hand_index < len(player.hand):
        return ActionResult(
            state=state,
            code=ErrorCode.INVALID_INDEX,
            message="engine_hand_oob",
            accepted=False,
        )

    company_id = player.hand[hand_index]
    new_portfolio = list(player.portfolio)
    new_portfolio[company_id] += 1
    new_hand = player.hand[:hand_index] + player.hand[hand_index + 1 :]
    new_player = replace(
        player,
        hand=new_hand,
        portfolio=tuple(new_portfolio),
        history=player.history + (f"play_portfolio:{company_id}",),
    )
    players = list(state.players)
    players[state.current_player] = new_player
    companies = _recompute_anti_monopoly(tuple(players), state.companies)
    events = state.events + (
        f"P{state.current_player} play_portfolio company={company_id}",
    )
    new_state = _finish_turn(
        replace(
            state,
            players=tuple(players),
            companies=companies,
            last_took_company=None,
            last_took_from_market=False,
            events=events,
        ),
    )
    return ActionResult(
        state=new_state,
        code=ErrorCode.OK,
        message="engine_play_portfolio_success",
        accepted=True,
    )


def _play_to_market(state: GameState, hand_index: int | None) -> ActionResult:
    if hand_index is None:
        return ActionResult(
            state=state,
            code=ErrorCode.INVALID_INDEX,
            message="engine_require_hand_index",
            accepted=False,
        )
    player = state.current_player_state()
    if not player.hand:
        return ActionResult(
            state=state,
            code=ErrorCode.INVALID_STATE,
            message="engine_hand_empty",
            accepted=False,
        )
    if not 0 <= hand_index < len(player.hand):
        return ActionResult(
            state=state,
            code=ErrorCode.INVALID_INDEX,
            message="engine_hand_oob",
            accepted=False,
        )
    if state.last_took_from_market and state.last_took_company is not None:
        if state.last_took_company == player.hand[hand_index]:
            return ActionResult(
                state=state,
                code=ErrorCode.INVALID_MOVE,
                message="engine_play_market_forbidden",
                accepted=False,
            )

    company_id = player.hand[hand_index]
    new_hand = player.hand[:hand_index] + player.hand[hand_index + 1 :]
    new_player = replace(
        player,
        hand=new_hand,
        history=player.history + (f"play_market:{company_id}",),
    )
    players = list(state.players)
    players[state.current_player] = new_player
    new_market = state.market + (MarketCard(company_id=company_id, coins=0),)
    events = state.events + (
        f"P{state.current_player} play_market company={company_id}",
    )
    new_state = _finish_turn(
        replace(
            state,
            players=tuple(players),
            market=new_market,
            last_took_company=None,
            last_took_from_market=False,
            events=events,
        ),
    )
    return ActionResult(
        state=new_state,
        code=ErrorCode.OK,
        message="engine_play_market_success",
        accepted=True,
    )


def _finish_turn(state: GameState) -> GameState:
    if state.game_end_triggered:
        hand = state.current_player_state().hand
        # 游戏结束时将所有手牌放回股份，不再继续发牌。
        players = list(state.players)
        player = state.current_player_state()
        new_portfolio = list(player.portfolio)
        for company_id in hand:
            new_portfolio[company_id] += 1
        players[state.current_player] = replace(
            player,
            hand=(),
            portfolio=tuple(new_portfolio),
            history=player.history + ("auto_discard_hand",),
        )
        companies = _recompute_anti_monopoly(tuple(players), state.companies)
        return replace(
            state,
            players=tuple(players),
            companies=companies,
            stage=TurnStage.FINISHED,
            turn_number=state.turn_number,
            game_end_triggered=False,
            events=state.events + ("game_end",),
        )

    next_player = (state.current_player + 1) % state.player_count()
    return replace(
        state,
        current_player=next_player,
        turn_number=state.turn_number + 1,
        stage=TurnStage.TAKE,
        last_took_company=None,
        last_took_from_market=False,
        events=state.events + (f"turn_end->P{next_player}",),
    )


def _recompute_anti_monopoly(
    players: tuple[PlayerState, ...],
    companies: tuple[CompanyState, ...],
) -> tuple[CompanyState, ...]:
    holder: list[int | None] = []
    for company in companies:
        # Keep previous holder on ties when they are still tied at the top;
        # only transfer holder when someone becomes the unique new maximum.
        shares = [player.portfolio[company.company_id] for player in players]
        max_shares = max(shares) if shares else 0
        if max_shares <= 0:
            holder.append(None)
            continue
        candidates = [idx for idx, count in enumerate(shares) if count == max_shares]
        if len(candidates) != 1:
            if (
                company.anti_monopoly_owner is not None
                and shares[company.anti_monopoly_owner] == max_shares
            ):
                holder.append(company.anti_monopoly_owner)
            else:
                holder.append(None)
            continue
        holder.append(candidates[0])

    return tuple(
        CompanyState(company_id=company.company_id, anti_monopoly_owner=holder[idx])
        for idx, company in enumerate(companies)
    )


def _company_holder(state: GameState, company_id: int) -> int | None:
    return state.companies[company_id].anti_monopoly_owner


def _add_coin(card: MarketCard, exempt: bool) -> MarketCard:
    if exempt:
        return card
    return MarketCard(company_id=card.company_id, coins=card.coins + 1)


def market_company_names(state: GameState) -> tuple[str, ...]:
    """返回可打印的市场摘要。"""
    return tuple(DEFAULT_COMPANIES[card.company_id].name for card in state.market)


def portfolio_summary(state: GameState, player_id: int) -> Sequence[int]:
    """返回某名玩家每家公司持股摘要。"""
    return state.players[player_id].portfolio
