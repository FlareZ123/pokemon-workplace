"""Materialize stable physical identity only when card copies stop being exchangeable."""

from __future__ import annotations

from dataclasses import dataclass

from multicopy_zone_state import ZoneCountState


@dataclass(frozen=True)
class CardInstance:
    instance_id: str
    card_class: str
    card_name: str
    zone: str
    attached_to: str | None = None
    board_object_id: str | None = None

    def __post_init__(self) -> None:
        if not self.instance_id:
            raise ValueError("instance_id must be non-empty")
        if not self.card_class:
            raise ValueError("card_class must be non-empty")
        if not self.card_name:
            raise ValueError("card_name must be non-empty")
        if not self.zone:
            raise ValueError("zone must be non-empty")
        if self.zone == "attached":
            if self.attached_to is None or self.board_object_id is not None:
                raise ValueError("attached instances require only attached_to")
        elif self.zone == "in_play":
            if self.board_object_id is None or self.attached_to is not None:
                raise ValueError("in-play instances require only board_object_id")
        elif self.attached_to is not None or self.board_object_id is not None:
            raise ValueError("off-board instances cannot have board bindings")


@dataclass(frozen=True)
class IdentityLedger:
    exchangeable: ZoneCountState
    instances: tuple[CardInstance, ...] = ()

    def __post_init__(self) -> None:
        ids = [row.instance_id for row in self.instances]
        if len(ids) != len(set(ids)):
            raise ValueError("materialized instance IDs must be unique")
        if self.instances != tuple(
            sorted(self.instances, key=lambda row: row.instance_id)
        ):
            raise ValueError("instances must be sorted by instance_id")

    def instance(self, instance_id: str) -> CardInstance:
        for row in self.instances:
            if row.instance_id == instance_id:
                return row
        raise KeyError(instance_id)

    def materialized_count(self, card_class: str) -> int:
        return sum(row.card_class == card_class for row in self.instances)

    def total(self, card_class: str) -> int:
        return self.exchangeable.total(card_class) + self.materialized_count(card_class)

    def totals(self) -> dict[str, int]:
        classes = {
            card_class
            for card_class, _zone, _count in self.exchangeable.counts
        }
        classes.update(row.card_class for row in self.instances)
        return {card_class: self.total(card_class) for card_class in sorted(classes)}


def _exchangeable_mapping(state: ZoneCountState) -> dict[tuple[str, str], int]:
    return {
        (card_class, zone): count
        for card_class, zone, count in state.counts
    }


def materialize(
    ledger: IdentityLedger,
    *,
    card_class: str,
    card_name: str,
    source_zone: str,
    instance_id: str,
) -> IdentityLedger:
    """Convert one exchangeable copy into one stable physical instance."""

    try:
        ledger.instance(instance_id)
    except KeyError:
        pass
    else:
        raise ValueError(f"instance_id already exists: {instance_id}")

    counts = _exchangeable_mapping(ledger.exchangeable)
    key = (card_class, source_zone)
    available = counts.get(key, 0)
    if available < 1:
        raise ValueError(f"no exchangeable {card_class!r} in {source_zone!r}")
    if available == 1:
        counts.pop(key)
    else:
        counts[key] = available - 1

    row = CardInstance(instance_id, card_class, card_name, source_zone)
    return IdentityLedger(
        ZoneCountState.from_mapping(counts),
        tuple(sorted(ledger.instances + (row,), key=lambda current: current.instance_id)),
    )


def move_instance(
    ledger: IdentityLedger,
    instance_id: str,
    destination_zone: str,
    *,
    attached_to: str | None = None,
    board_object_id: str | None = None,
) -> IdentityLedger:
    current = ledger.instance(instance_id)
    replacement = CardInstance(
        current.instance_id,
        current.card_class,
        current.card_name,
        destination_zone,
        attached_to,
        board_object_id,
    )
    rows = [
        replacement if row.instance_id == instance_id else row
        for row in ledger.instances
    ]
    return IdentityLedger(
        ledger.exchangeable,
        tuple(sorted(rows, key=lambda row: row.instance_id)),
    )


def attach_instance(
    ledger: IdentityLedger,
    instance_id: str,
    holder_id: str,
) -> IdentityLedger:
    if not holder_id:
        raise ValueError("holder_id must be non-empty")
    return move_instance(
        ledger,
        instance_id,
        "attached",
        attached_to=holder_id,
    )


def put_in_play_instance(
    ledger: IdentityLedger,
    instance_id: str,
    board_object_id: str,
) -> IdentityLedger:
    if not board_object_id:
        raise ValueError("board_object_id must be non-empty")
    return move_instance(
        ledger,
        instance_id,
        "in_play",
        board_object_id=board_object_id,
    )


def detach_instance(
    ledger: IdentityLedger,
    instance_id: str,
    destination_zone: str,
) -> IdentityLedger:
    current = ledger.instance(instance_id)
    if current.attached_to is None:
        raise ValueError("instance is not attached")
    if destination_zone == "attached":
        raise ValueError("detach destination must not be attached")
    return move_instance(ledger, instance_id, destination_zone)


def dematerialize(
    ledger: IdentityLedger,
    instance_id: str,
) -> IdentityLedger:
    """Return a relation-free physical instance to its exchangeable count class."""

    current = ledger.instance(instance_id)
    if current.attached_to is not None or current.board_object_id is not None:
        raise ValueError("board-bound instance cannot be dematerialized")

    counts = _exchangeable_mapping(ledger.exchangeable)
    key = (current.card_class, current.zone)
    counts[key] = counts.get(key, 0) + 1
    instances = tuple(
        row for row in ledger.instances if row.instance_id != instance_id
    )
    return IdentityLedger(
        ZoneCountState.from_mapping(counts),
        instances,
    )


def assert_conserved(
    before: IdentityLedger,
    after: IdentityLedger,
) -> None:
    if before.totals() != after.totals():
        raise AssertionError(
            f"card totals changed: {before.totals()} -> {after.totals()}"
        )


def validate_board_attachment_bindings(
    ledger: IdentityLedger,
    board,
) -> None:
    """Require materialized attachments to match the board-object layer."""

    expected: dict[str, tuple[str, str]] = {}
    for pokemon in board.objects:
        for energy in pokemon.energy:
            if energy.instance_id in expected:
                raise ValueError(f"duplicate board attachment ID: {energy.instance_id}")
            expected[energy.instance_id] = (pokemon.object_id, energy.card_name)
        if pokemon.tool is not None:
            if pokemon.tool.instance_id in expected:
                raise ValueError(f"duplicate board attachment ID: {pokemon.tool.instance_id}")
            expected[pokemon.tool.instance_id] = (
                pokemon.object_id,
                pokemon.tool.card_name,
            )

    actual = {
        row.instance_id: (row.attached_to, row.card_name)
        for row in ledger.instances
        if row.zone == "attached"
    }
    if set(actual) != set(expected):
        raise ValueError(
            "attached instance IDs differ between identity ledger and board: "
            f"ledger={sorted(actual)}, board={sorted(expected)}"
        )

    for instance_id, binding in expected.items():
        if actual[instance_id] != binding:
            raise ValueError(
                f"attachment binding mismatch for {instance_id}: "
                f"ledger={actual[instance_id]!r}, board={binding!r}"
            )


def validate_board_position_stack_bindings(
    ledger: IdentityLedger,
    board,
) -> None:
    """Require in-play materialized Pokemon cards to match board evolution stacks."""

    expected: dict[str, tuple[str, str]] = {}
    for pokemon in board.pokemon:
        for card in pokemon.stack:
            if card.card_id in expected:
                raise ValueError(f"duplicate board stack card ID: {card.card_id}")
            expected[card.card_id] = (pokemon.pokemon_id, card.name)

    actual = {
        row.instance_id: (row.board_object_id, row.card_name)
        for row in ledger.instances
        if row.zone == "in_play"
    }
    if set(actual) != set(expected):
        raise ValueError(
            "in-play instance IDs differ between identity ledger and board: "
            f"ledger={sorted(actual)}, board={sorted(expected)}"
        )

    for instance_id, binding in expected.items():
        if actual[instance_id] != binding:
            raise ValueError(
                f"stack binding mismatch for {instance_id}: "
                f"ledger={actual[instance_id]!r}, board={binding!r}"
            )
