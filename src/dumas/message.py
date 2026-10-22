from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .configuration import Configuration

GROOVY_COMMANDS: tuple[str, ...] = ("-p", "-skip", "-loop", "-q", "-clear", "-remove", "-dc")
DUMAS_COMMANDS: tuple[str, ...] = (
    "&help",
    "&start",
    "&stop",
    "&random",
    "&get-config",
    "&show-config",
)
ZERO_WIDTH_PREFIXES: tuple[str, ...] = ("\u200b", "\u200d", "\ufeff")


@dataclass(slots=True)
class Message:
    author_id: int
    content: str

    def is_relevant(self, configuration: Configuration) -> bool:
        if self.content.startswith(ZERO_WIDTH_PREFIXES):
            return False
        if self.author_id == configuration.bot_app:
            return False
        if len(self.content) < configuration.message_length:
            return False
        if self.content.startswith(GROOVY_COMMANDS):
            return False
        return not self.content.startswith(DUMAS_COMMANDS)
