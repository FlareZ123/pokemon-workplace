"""Public reveal tokens derived from physically materialized card identity.

The projection is deliberately declared: a deck name, an exact print ID, or a
previously chosen variant/reprint class. It does not synthesize a print ID from
a coarser card class or accept an unrelated free-form observation string.
"""

from __future__ import annotations

from card_class_namespace import CardClassNamespace
from identity_materialization import CardInstance


_SUPPORTED_STRUCTURAL_CLASSES = frozenset({
    CardClassNamespace.EXACT_PRINT,
    CardClassNamespace.CONSERVATIVE_VARIANT,
    CardClassNamespace.OFFICIAL_REPRINT,
})


def public_reveal_label(
    instance: CardInstance,
    namespace: CardClassNamespace = CardClassNamespace.DECK_NAME,
) -> str:
    """Project a revealed instance to an identity label at declared granularity."""
    namespace = CardClassNamespace(namespace)
    if namespace == CardClassNamespace.DECK_NAME:
        return instance.card_name
    if namespace not in _SUPPORTED_STRUCTURAL_CLASSES:
        raise ValueError("unsupported public reveal identity namespace")

    prefix = f"{namespace.value}:"
    if not instance.card_class.startswith(prefix):
        raise ValueError(
            "materialized card class cannot supply the requested public identity"
        )
    value = instance.card_class[len(prefix):]
    if not value:
        raise ValueError("materialized identity token must be non-empty")
    return value
