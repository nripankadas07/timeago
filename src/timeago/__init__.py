"""Timeago: format datetime deltas as human-readable relative time strings."""

from timeago.core import format
from timeago.parser import parse
from timeago.errors import TimeagoError

__version__ = "1.0.0"
__author__ = "nripankadas07"
__all__ = ["format", "parse", "TimeagoError"]
