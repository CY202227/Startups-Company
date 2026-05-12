"""结算规则与边界用例。"""

from __future__ import annotations

from dataclasses import replace

from startups.scoring import compute_scores
from startups.engine import setup_game


def test_majority_pays_holder_and_scores_are_tripled() -> None:
    state = setup_game(player_count=3, seed=1)
    holder = replace(
        state.players[0],
        cash=0,
        hand=(),
        portfolio=(3, 0, 0, 0, 0, 0),
    )
    payer = replace(
        state.players[1],
        cash=5,
        hand=(),
        portfolio=(1, 0, 0, 0, 0, 0),
    )
    state = replace(
        state,
        players=(holder, payer, state.players[2]),
    )
    state, score = compute_scores(state)
    assert state.players[0].flipped_coins == 1
    assert state.players[1].cash == 4
    assert score.scores[0] == 0 + 1 * 3


def test_tie_means_no_payout() -> None:
    state = setup_game(player_count=3, seed=2)
    p0 = replace(
        state.players[0],
        cash=0,
        hand=(),
        portfolio=(2, 0, 0, 0, 0, 0),
    )
    p1 = replace(
        state.players[1],
        cash=0,
        hand=(),
        portfolio=(2, 0, 0, 0, 0, 0),
    )
    p2 = replace(
        state.players[2],
        cash=0,
        hand=(),
        portfolio=(1, 0, 0, 0, 0, 0),
    )
    state = replace(state, players=(p0, p1, p2))
    _, score = compute_scores(state)
    assert score.scores == (0, 0, 0)
    assert not score.payouts


def test_short_payment_creates_penalty_points() -> None:
    state = setup_game(player_count=3, seed=3)
    holder = replace(
        state.players[0],
        cash=0,
        hand=(),
        portfolio=(4, 0, 0, 0, 0, 0),
    )
    payer = replace(
        state.players[1],
        cash=0,
        hand=(),
        portfolio=(3, 0, 0, 0, 0, 0),
    )
    player2 = replace(state.players[2], hand=(), portfolio=(0,) * 6)
    state = replace(state, players=(holder, payer, player2))
    _, score = compute_scores(state)
    assert score.payouts[0].payer_id == 1
    assert score.payouts[0].required == 3
    assert score.scores[1] == -3
