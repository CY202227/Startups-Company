"""规则常量与枚举。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TurnStage(Enum):
    """回合阶段。"""

    TAKE = auto()
    PLAY = auto()
    FINISHED = auto()


class ActionType(Enum):
    """玩家可执行动作类型。"""

    TAKE_FROM_DECK = auto()
    TAKE_FROM_MARKET = auto()
    PLAY_TO_PORTFOLIO = auto()
    PLAY_TO_MARKET = auto()


class ErrorCode(Enum):
    """动作执行错误码。"""

    OK = auto()
    NOT_YOUR_TURN = auto()
    INVALID_PHASE = auto()
    INVALID_INDEX = auto()
    INVALID_MOVE = auto()
    NOT_ENOUGH_CAPITAL = auto()
    INSUFFICIENT_STATE = auto()
    INVALID_PLAYER_COUNT = auto()


@dataclass(frozen=True)
class CompanyConfig:
    """单家公司静态配置。"""

    company_id: int
    name: str
    card_count: int


@dataclass(frozen=True)
class GameRules:
    """封装游戏可配参数。"""

    player_count: int
    start_hand_size: int = 3
    starting_capital: int = 10
    remove_from_deck: int = 5
    min_players: int = 3
    max_players: int = 7


DEFAULT_COMPANIES: tuple[CompanyConfig, ...] = (
    CompanyConfig(company_id=0, name="EMT", card_count=8),
    CompanyConfig(company_id=1, name="Flaming Soft", card_count=8),
    CompanyConfig(company_id=2, name="Hippo Powertech", card_count=7),
    CompanyConfig(company_id=3, name="Bowwow Games", card_count=7),
    CompanyConfig(company_id=4, name="Giraffe Beer", card_count=5),
    CompanyConfig(company_id=5, name="Elephant Mars Travel", card_count=10),
)

TOTAL_CARDS: int = sum(company.card_count for company in DEFAULT_COMPANIES)

if TOTAL_CARDS != 45:
    raise ValueError("默认牌组卡牌数量不是 45，无法初始化。")
