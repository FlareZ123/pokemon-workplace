from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_setup_inference import KAZUMA_IRON_NONBASIC_COUNTS
from iron_thorns_mail_gladion import COUNTS, exact_probability
from iron_thorns_trainers_mail import MailLineCounts, exact_mail_line_probability
from iron_thorns_turn1_probability import (
    baseline_route,
    exact_probability as turn1_probability,
    information_aware_route,
)


def close(actual: float, expected: float) -> None:
    assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12)


def main() -> None:
    counts = KAZUMA_IRON_NONBASIC_COUNTS
    assert counts["Guzma & Hala"] == 2
    assert counts["Tag Call"] == 2
    assert counts["Thunder Mountain ♢"] == 1
    assert counts["Double Colorless Energy"] == 1
    assert counts["Gladion"] == 1
    assert counts["Trainers' Mail"] == 3
    assert COUNTS == (4, 2, 2, 1, 1, 1, 3, 39, 7)

    combined = float(exact_probability())
    close(combined, 0.3895826619980364)

    mail_only = float(
        exact_mail_line_probability(
            MailLineCounts(4, 2, 2, 1, 1, 3, 40, 7)
        ).mail_probability
    )
    close(mail_only, 0.38821051379263183)

    baseline, _ = turn1_probability(baseline_route)
    information_only, _ = turn1_probability(information_aware_route)
    close(baseline, 0.3378150571059306)
    close(information_only, 0.34008906143861073)

    assert combined > mail_only
    assert combined > information_only

    naive_additive = mail_only + (information_only - baseline)
    assert combined < naive_additive

    close(combined - mail_only, 0.0013721482054045442)
    close(naive_additive - combined, 0.0009018561272705277)

    print("iron_thorns_mail_gladion: all assertions passed")
    print("mail only:", f"{mail_only:.12%}")
    print("mail + K0/K1 Gladion:", f"{combined:.12%}")
    print("Gladion increment after Mail:", f"{combined - mail_only:.12%}")
    print("naive additive overstatement:", f"{naive_additive - combined:.12%}")


if __name__ == "__main__":
    main()
