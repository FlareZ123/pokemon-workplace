from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.discard_gate_probability import (
    conditional_payability,
    minimum_disposable_for_threshold,
    playable_probability,
    present_probability,
)


def pct(value: float) -> str:
    return f"{100 * value:.2f}%"


def main() -> None:
    deck_size = 60

    print("## Seven-card random sample")
    print()
    print("| Disposable non-action cards | Ultra Ball present | Ultra Ball playable (spares usable) | P(playable \\| present) | Secret Box present | Secret Box playable | P(playable \\| present) |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for disposable in (12, 20, 28):
        ultra_present = present_probability(deck_size, 4, 7)
        ultra_playable = playable_probability(
            deck_size, 4, disposable, 7, 2, spare_actions_disposable=True
        )
        ultra_conditional = conditional_payability(
            deck_size, 4, disposable, 7, 2, spare_actions_disposable=True
        )
        box_present = present_probability(deck_size, 1, 7)
        box_playable = playable_probability(deck_size, 1, disposable, 7, 3)
        box_conditional = conditional_payability(deck_size, 1, disposable, 7, 3)
        print(
            f"| {disposable} | {pct(ultra_present)} | {pct(ultra_playable)} | "
            f"{pct(ultra_conditional)} | {pct(box_present)} | {pct(box_playable)} | "
            f"{pct(box_conditional)} |"
        )

    print()
    print("## Disposable-pool thresholds for seven-card samples")
    print()
    print("| Conditional payability target | Ultra Ball, strict | Ultra Ball, spare copies usable | Secret Box |")
    print("| ---: | ---: | ---: | ---: |")
    for threshold in (0.5, 0.8, 0.9):
        strict = minimum_disposable_for_threshold(deck_size, 4, 7, 2, threshold)
        spares = minimum_disposable_for_threshold(
            deck_size, 4, 7, 2, threshold, spare_actions_disposable=True
        )
        secret = minimum_disposable_for_threshold(deck_size, 1, 7, 3, threshold)
        print(f"| {threshold:.0%} | {strict} | {spares} | {secret} |")

    print()
    print("## Hand-size sensitivity at 20 disposable non-action cards")
    print()
    print("| Sample size | Ultra Ball P(playable \\| present), spares usable | Secret Box P(playable \\| present) |")
    print("| ---: | ---: | ---: |")
    for hand_size in (5, 6, 7, 8):
        ultra = conditional_payability(
            deck_size, 4, 20, hand_size, 2, spare_actions_disposable=True
        )
        secret = conditional_payability(deck_size, 1, 20, hand_size, 3)
        print(f"| {hand_size} | {pct(ultra)} | {pct(secret)} |")


if __name__ == "__main__":
    main()
