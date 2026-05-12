"""规则与阶段基础断言。"""

from __future__ import annotations

import pytest

from startups.engine import setup_game


def test_setup_counts_match_rules() -> None:
    state = setup_game(player_count=3, seed=123)
    assert state.player_count() == 3
    assert not state.is_finished()
    assert len(state.market) == 0
    assert state.current_player == 0
    assert all(len(player.hand) == 3 for player in state.players)
    assert all(player.cash == 10 for player in state.players)
    total_start_cards = 3 * len(state.players)
    expected_deck = 45 - total_start_cards - 5
    assert len(state.deck) == expected_deck


def test_invalid_player_count() -> None:
    with pytest.raises(ValueError, match="Player count"):
        setup_game(player_count=2)
