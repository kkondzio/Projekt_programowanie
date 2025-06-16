from enum import Enum, auto


class GameState(Enum):
    """Enumeracja reprezentująca różne stany gry."""

    HOMEPAGE = auto()
    STARTPAGE = auto()
    INSTRUCTIONPAGE = auto()
    GAMEPAGE = auto()
    RESULTPAGE = auto()
    END = auto()
    DIFFICULTY_SELECT = auto()
    HARDMODE_INSTRUCTION = auto()
