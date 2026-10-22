from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .configuration import Configuration

GROOVY_COMMANDS: frozenset[str] = frozenset(
    {
        "-p",
        "-skip",
        "-loop",
        "-q",
        "-clear",
        "-remove",
        "-dc",
    }
)
DUMAS_COMMANDS: frozenset[str] = frozenset(
    {
        "&help",
        "&start",
        "&stop",
        "&random",
        "&get-config",
        "&show-config",
    }
)
ZERO_WIDTH_PREFIXES: tuple[str, ...] = ("\u200b", "\u200d", "\ufeff")


@dataclass(slots=True, frozen=True)
class Message:
    author_id: int
    content: str

    def is_relevant(self, configuration: Configuration) -> bool:
        stripped = self.content.strip()
        if stripped.startswith(ZERO_WIDTH_PREFIXES):
            return False
        if self.author_id == configuration.bot_app:
            return False
        if len(stripped) < configuration.message_length:
            return False
        tokens = stripped.lower().split()
        if not tokens:
            return False
        first_token = tokens[0]
        return first_token not in GROOVY_COMMANDS and first_token not in DUMAS_COMMANDS
