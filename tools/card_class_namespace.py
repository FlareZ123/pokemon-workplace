"""Typed keys for exchangeable card-class counts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CardClassNamespace(str, Enum):
    EXACT_PRINT = "exact_print"
    CONSERVATIVE_VARIANT = "conservative_variant"
    OFFICIAL_REPRINT = "official_reprint"
    DECK_NAME = "deck_name"
    CUSTOM = "custom"


@dataclass(frozen=True, order=True)
class CardClassKey:
    namespace: CardClassNamespace
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("card-class value must be non-empty")

    def token(self) -> str:
        return f"{self.namespace.value}:{self.value}"


def exact_print(print_id: str) -> CardClassKey:
    return CardClassKey(CardClassNamespace.EXACT_PRINT, print_id)


def conservative_variant(variant_id: str) -> CardClassKey:
    return CardClassKey(CardClassNamespace.CONSERVATIVE_VARIANT, variant_id)


def official_reprint(class_id: str) -> CardClassKey:
    return CardClassKey(CardClassNamespace.OFFICIAL_REPRINT, class_id)


def deck_name(name: str) -> CardClassKey:
    return CardClassKey(CardClassNamespace.DECK_NAME, name)
