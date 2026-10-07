from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_setup_inference import (
    KAZUMA_IRON_NONBASIC_COUNTS,
    KOHEI_IRON_NONBASIC_COUNTS,
    RYOYA_IRON_NONBASIC_COUNTS,
)
from iron_thorns_trainers_mail import (
    MailLineCounts,
    exact_mail_line_probability,
)


ENERGY_NAMES = {
    "Speed Lightning Energy",
    "Capture Energy",
    "Spiky Energy",
    "Double Colorless Energy",
}


def compile_counts(nonbasic: dict[str, int]) -> MailLineCounts:
    energy_total = sum(nonbasic.get(name, 0) for name in ENERGY_NAMES)
    trainer_total = sum(nonbasic.values()) - energy_total

    gnh = nonbasic["Guzma & Hala"]
    tag = nonbasic["Tag Call"]
    thunder = nonbasic["Thunder Mountain ♢"]
    dce = nonbasic["Double Colorless Energy"]
    mail = nonbasic["Trainers' Mail"]

    return MailLineCounts(
        iron_thorns=4,
        guzma_hala=gnh,
        tag_call=tag,
        thunder_mountain=thunder,
        double_colorless=dce,
        trainers_mail=mail,
        other_trainers=trainer_total - gnh - tag - thunder - mail,
        other_nontrainers=energy_total - dce,
    )


def assert_close(actual: float, expected: float) -> None:
    if not math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    kazuma = compile_counts(KAZUMA_IRON_NONBASIC_COUNTS)
    ryoya = compile_counts(RYOYA_IRON_NONBASIC_COUNTS)
    kohei = compile_counts(KOHEI_IRON_NONBASIC_COUNTS)

    assert kazuma == MailLineCounts(4, 2, 2, 1, 1, 3, 40, 7)
    assert ryoya == MailLineCounts(4, 2, 2, 1, 3, 4, 39, 5)
    assert kohei == MailLineCounts(4, 2, 2, 1, 1, 2, 41, 7)

    results = {
        "Kazuma": exact_mail_line_probability(kazuma),
        "Ryoya": exact_mail_line_probability(ryoya),
        "Kohei": exact_mail_line_probability(kohei),
    }

    expected = {
        "Kazuma": (0.3378150571059356, 0.38821051379263183),
        "Ryoya": (0.39107850627345275, 0.466234204093109),
        "Kohei": (0.3378150571059356, 0.3719558243095575),
    }

    for name, result in results.items():
        baseline, mail = expected[name]
        assert_close(float(result.baseline_probability), baseline)
        assert_close(float(result.mail_probability), mail)
        assert result.mail_probability >= result.baseline_probability

    print("iron_thorns_trainers_mail: all assertions passed")
    for name, result in results.items():
        print(
            name,
            f"baseline={float(result.baseline_probability):.12%}",
            f"mail={float(result.mail_probability):.12%}",
            f"increment={float(result.mail_increment):.12%}",
        )


if __name__ == "__main__":
    main()
