"""Dumas - Discord bot that brings back chat memories."""

__version__ = "0.2.0"

from .configuration import Configuration
from .dumas import Dumas

__all__ = ["Configuration", "Dumas", "__version__"]
