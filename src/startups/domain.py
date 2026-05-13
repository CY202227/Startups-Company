"""游戏领域对象与不可变状态定义。"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

from .rules import (
    ActionType,
    ErrorCode,
    GameRules,
    TurnStage,
)


@dataclass(frozen=True)
class MarketCard:
    """市场中的一张公司卡。"""

    company_id: int
    coins: int = 0


@dataclass(frozen=True)
class PlayerState:
    """玩家状态。"""

    player_id: int
    cash: int
    hand: tuple[int, ...]
    portfolio: tuple[int, ...]
    flipped_coins: int = 0
    penalty: int = 0
    history: tuple[str, ...] = ()

    def shares(self, company_id: int) -> int:
        return self.portfolio[company_id]

    def with_share(
        self,
        company_id: int,
        new_count: int,
    ) -> "PlayerState":
        portfolio = list(self.portfolio)
        portfolio[company_id] = new_count
        return replace(self, portfolio=tuple(portfolio))


@dataclass(frozen=True)
class CompanyState:
    """单家公司公共状态。"""

    company_id: int
    anti_monopoly_owner: Optional[int]


@dataclass(frozen=True)
class GameState:
    """完整游戏状态。"""

    rules: GameRules
    players: tuple[PlayerState, ...]
    deck: tuple[int, ...]
    market: tuple[MarketCard, ...]
    companies: tuple[CompanyState, ...]
    stage: TurnStage
    current_player: int
    turn_number: int
    last_took_company: Optional[int]
    last_took_from_market: bool
    game_end_triggered: bool
    events: tuple[str, ...]

    def current_player_state(self) -> PlayerState:
        return self.players[self.current_player]

    def player_count(self) -> int:
        return len(self.players)

    def is_finished(self) -> bool:
        return self.stage == TurnStage.FINISHED

    def to_dict(self) -> dict[str, object]:
        return {
            "rules": {
                "player_count": self.rules.player_count,
                "start_hand_size": self.rules.start_hand_size,
                "starting_capital": self.rules.starting_capital,
                "remove_from_deck": self.rules.remove_from_deck,
                "min_players": self.rules.min_players,
                "max_players": self.rules.max_players,
            },
            "players": [
                {
                    "player_id": player.player_id,
                    "cash": player.cash,
                    "hand": list(player.hand),
                    "portfolio": list(player.portfolio),
                    "flipped_coins": player.flipped_coins,
                    "penalty": player.penalty,
                    "history": list(player.history),
                }
                for player in self.players
            ],
            "deck": list(self.deck),
            "market": [
                {"company_id": card.company_id, "coins": card.coins}
                for card in self.market
            ],
            "companies": [
                {"company_id": c.company_id, "anti_owner": c.anti_monopoly_owner}
                for c in self.companies
            ],
            "stage": self.stage.name,
            "current_player": self.current_player,
            "turn_number": self.turn_number,
            "last_took_company": self.last_took_company,
            "last_took_from_market": self.last_took_from_market,
            "game_end_triggered": self.game_end_triggered,
            "events": list(self.events),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "GameState":
        rules_payload = payload["rules"]
        rules = GameRules(
            player_count=int(rules_payload["player_count"]),
            start_hand_size=int(rules_payload["start_hand_size"]),
            starting_capital=int(rules_payload["starting_capital"]),
            remove_from_deck=int(rules_payload["remove_from_deck"]),
            min_players=int(rules_payload["min_players"]),
            max_players=int(rules_payload["max_players"]),
        )
        players = tuple(
            PlayerState(
                player_id=int(player["player_id"]),
                cash=int(player["cash"]),
                hand=tuple(int(card) for card in player["hand"]),
                portfolio=tuple(int(count) for count in player["portfolio"]),
                flipped_coins=int(player["flipped_coins"]),
                penalty=int(player["penalty"]),
                history=tuple(str(x) for x in player["history"]),
            )
            for player in payload["players"]
        )
        market = tuple(
            MarketCard(company_id=int(card["company_id"]), coins=int(card["coins"]))
            for card in payload["market"]
        )
        companies = tuple(
            CompanyState(
                company_id=int(company["company_id"]),
                anti_monopoly_owner=(
                    int(company["anti_owner"])
                    if company["anti_owner"] is not None
                    else None
                ),
            )
            for company in payload["companies"]
        )
        return cls(
            rules=rules,
            players=players,
            deck=tuple[int, ...](int(x) for x in payload["deck"]),
            market=market,
            companies=companies,
            stage=TurnStage[payload["stage"]],
            current_player=int(payload["current_player"]),
            turn_number=int(payload["turn_number"]),
            last_took_company=(
                int(payload["last_took_company"])
                if payload["last_took_company"] is not None
                else None
            ),
            last_took_from_market=bool(payload["last_took_from_market"]),
            game_end_triggered=bool(payload["game_end_triggered"]),
            events=tuple(str(x) for x in payload["events"]),
        )


@dataclass(frozen=True)
class Action:
    """行动对象。"""

    action_type: ActionType
    index: Optional[int] = None


@dataclass(frozen=True)
class ActionResult:
    """动作执行结果。"""

    state: GameState
    code: ErrorCode
    message: str = ""
    accepted: bool = True
