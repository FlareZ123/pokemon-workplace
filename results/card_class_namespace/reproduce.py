from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from card_class_namespace import (
    CardClassKey,
    CardClassNamespace,
    conservative_variant,
    deck_name,
    exact_print,
    official_reprint,
)
from multicopy_zone_state import ZoneCountState


def main():
    raw = "Copycat"
    keys = (
        exact_print(raw),
        conservative_variant(raw),
        official_reprint(raw),
        deck_name(raw),
    )
    assert len(set(keys)) == 4
    assert len({key.token() for key in keys}) == 4

    state = ZoneCountState.from_mapping({
        (official_reprint("copycat-functional-class").token(), "hand"): 2,
    })
    assert state.total("official_reprint:copycat-functional-class") == 2

    custom = CardClassKey(CardClassNamespace.CUSTOM, "experiment-a")
    assert custom.token() == "custom:experiment-a"

    print("card class namespace regressions passed")


if __name__ == "__main__":
    main()
