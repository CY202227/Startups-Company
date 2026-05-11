"""重放与确定性测试。"""

from __future__ import annotations

from startups.engine import setup_game


def test_seed_reproducible_initial_state() -> None:
  a = setup_game(player_count=4, seed=101)
  b = setup_game(player_count=4, seed=101)
  assert a.to_dict() == b.to_dict()
