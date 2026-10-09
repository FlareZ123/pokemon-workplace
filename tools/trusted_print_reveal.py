"""Source-validated identity for materialized paper Expanded card printings.

A caller-supplied instance may contain an exact-print class key and an arbitrary
name. This helper binds those two fields to the repository's effective-legality
card identity catalog before treating the instance as a trusted public reveal.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from card_class_namespace import CardClassNamespace
from identity_materialization import CardInstance
from revealed_target_identity import public_reveal_label

if TYPE_CHECKING:
    from card_identity import IdentityIndex


def validate_materialized_print(
    instance: CardInstance,
    identity_index: IdentityIndex,
    *,
    require_legal: bool = True,
) -> str:
    """Return the card ID only if material identity matches its source record."""
    print_id = public_reveal_label(
        instance, CardClassNamespace.EXACT_PRINT
    )
    record = identity_index.prints_by_id.get(print_id)
    if record is None:
        raise ValueError(f"unknown Expanded-scope exact print: {print_id}")
    if record.name != instance.card_name:
        raise ValueError(
            f"materialized name disagrees with print {print_id}: "
            f"{instance.card_name!r} vs {record.name!r}"
        )
    if require_legal and record.effective_status != "Legal":
        raise ValueError(f"print {print_id} is not legal in paper Expanded")
    return print_id
