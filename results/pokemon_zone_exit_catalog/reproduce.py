"""Reproduce the conservative Pokemon zone-exit card-text catalog."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from pokemon_zone_exit_catalog import catalog_pokemon_zone_exits


def _row(rows: list[dict], card_id: str) -> dict:
    matches = [row for row in rows if row["id"] == card_id]
    if len(matches) != 1:
        raise AssertionError((card_id, matches))
    return matches[0]


def main() -> None:
    result = catalog_pokemon_zone_exits(ROOT / "resources")
    summary = result["summary"]
    rows = result["rows"]

    assert summary["prints"] == 146
    assert summary["unique_names"] == 73
    assert summary["timing_print_counts"] == {
        "direct_effect": 143,
        "knockout_triggered": 3,
    }
    assert summary["timing_unique_name_counts"] == {
        "direct_effect": 70,
        "knockout_triggered": 3,
    }
    assert summary["route_print_counts"] == {
        "deck->deck": 85,
        "hand->discard": 12,
        "hand->hand": 49,
    }
    assert summary["route_unique_name_counts"] == {
        "deck->deck": 46,
        "hand->discard": 5,
        "hand->hand": 22,
    }

    scoop = _row(rows, "bw10-95")
    assert (
        scoop["pokemon_destination"],
        scoop["attachment_destination"],
    ) == ("hand", "hand")

    cassius = _row(rows, "xy1-115")
    assert (
        cassius["pokemon_destination"],
        cassius["attachment_destination"],
    ) == ("deck", "deck")

    az = _row(rows, "xy4-91")
    assert (
        az["pokemon_destination"],
        az["attachment_destination"],
    ) == ("hand", "discard")

    accelgor = _row(rows, "bw5-11")
    assert accelgor["source_kind"] == "attack"
    assert accelgor["effect_name"] == "Deck and Cover"
    assert (
        accelgor["pokemon_destination"],
        accelgor["attachment_destination"],
    ) == ("deck", "deck")

    swoobat = _row(rows, "rsv10pt5-37")
    assert swoobat["effect_name"] == "Happy Return"
    assert (
        swoobat["pokemon_destination"],
        swoobat["attachment_destination"],
    ) == ("hand", "hand")

    rescue_scarf = _row(rows, "bw6-115")
    assert rescue_scarf["timing_class"] == "knockout_triggered"

    splash_energy = _row(rows, "xy9-113")
    assert splash_energy["timing_class"] == "knockout_triggered"

    celebi = _row(rows, "xyp-XY93")
    assert celebi["timing_class"] == "knockout_triggered"

    for direct in (scoop, cassius, az, accelgor, swoobat):
        assert direct["timing_class"] == "direct_effect"

    banned_ids = {
        "swsh2-22",
        "swsh45sv-SV013",
        "swsh10tg-TG02",
        "swshp-SWSH022",
    }
    assert not banned_ids & {row["id"] for row in rows}

    print(summary)
    for row in (scoop, cassius, az, accelgor, swoobat):
        print(
            row["id"],
            row["name"],
            row["source_kind"],
            row["effect_name"],
            row["pokemon_destination"],
            row["attachment_destination"],
        )


if __name__ == "__main__":
    main()
