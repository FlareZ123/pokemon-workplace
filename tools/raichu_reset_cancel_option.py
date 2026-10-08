"""Paired simulation of the option to cancel a destructive reset after K1."""

from __future__ import annotations

import argparse
from math import sqrt

import numpy as np

import raichu_draw_engine_fallback as base


def _stats(total: float, squared: float, count: int) -> tuple[float, float, list[float]]:
    mean = total / count
    variance = max(0.0, (squared - count * mean * mean) / (count - 1))
    se = sqrt(variance / count)
    return mean, se, [mean - 1.96 * se, mean + 1.96 * se]


def simulate(
    samples: int = 1_000_000,
    seed: int = 20261008,
    batch_size: int = 50_000,
) -> dict:
    rng = np.random.default_rng(seed)
    branch_states = 0
    modes = {
        name: {
            "capable": 0,
            "immediate": 0,
            "forced_sum": 0.0,
            "gain": 0.0,
            "gain_sq": 0.0,
        }
        for name in ("later", "first")
    }

    for offset in range(0, samples, batch_size):
        batch = min(batch_size, samples - offset)
        order = np.argsort(rng.random((batch, 60)), axis=1)
        exposed = base.DECK_LABELS[order[:, :14]]
        openings = exposed[:, :7]
        prizes = exposed[:, 7:13]
        draws = exposed[:, 13]

        opening_counts = np.zeros((batch, 13), dtype=np.int8)
        prize_counts = np.zeros((batch, 13), dtype=np.int8)
        rows = np.arange(batch)
        for slot in range(7):
            np.add.at(opening_counts, (rows, openings[:, slot]), 1)
        for slot in range(6):
            np.add.at(prize_counts, (rows, prizes[:, slot]), 1)

        valid = (
            opening_counts[:, base.CROBAT]
            + opening_counts[:, base.DEDENNE]
            + opening_counts[:, base.SQUAWK]
            + opening_counts[:, base.GIRATINA]
            + opening_counts[:, base.OTHER_STARTER]
        ) > 0

        for row in np.flatnonzero(valid):
            hand = opening_counts[row].astype(np.int16).copy()
            active = base._active_from_opening(hand)
            hand[active] -= 1
            hand[int(draws[row])] += 1

            if (
                hand[base.TARGET] > 0
                or hand[base.QUICK] == 0
                or hand[base.GLADION] == 0
                or hand[base.DISP] + hand[base.GIRATINA] == 0
            ):
                continue

            branch_states += 1

            direct_visible = hand[base.ULTRA] > 0 or hand[base.COMPUTER] > 0
            hosted_forest = (
                hand[base.FOREST] > 0
                and (active == base.CROBAT or hand[base.CROBAT] > 0)
            )
            if direct_visible or hosted_forest:
                continue

            deck = (
                base.DECK_COUNTS
                - opening_counts[row].astype(np.int16)
                - prize_counts[row].astype(np.int16)
            )
            deck[int(draws[row])] -= 1

            post_hand = base._pay_quick_ball(
                hand,
                base._legacy_payment_choice(hand),
            )
            target_prized = deck[base.TARGET] == 0
            immediate = base._endpoint_success(
                base._compress(post_hand),
                base._compress(deck),
                target_prized,
                active == base.CROBAT,
            )
            forest_host = active == base.CROBAT or post_hand[base.CROBAT] > 0
            forced_reset_success = base._draw_success_probability(
                base._compress(deck),
                6,
                (0,) * 8,
                target_prized,
                forest_host,
            )

            later_capable = post_hand[base.DEDENNE] > 0
            first_capable = (
                later_capable
                or post_hand[base.SQUAWK] > 0
                or active == base.SQUAWK
            )

            for name, capable in (
                ("later", later_capable),
                ("first", first_capable),
            ):
                gain = 0.0
                if capable:
                    modes[name]["capable"] += 1
                    modes[name]["forced_sum"] += forced_reset_success
                    if immediate:
                        modes[name]["immediate"] += 1
                        gain = 1.0 - forced_reset_success
                modes[name]["gain"] += gain
                modes[name]["gain_sq"] += gain * gain

    result = {
        "samples": samples,
        "seed": seed,
        "observable_branch_states": branch_states,
    }

    for name, row in modes.items():
        mean, se, ci = _stats(row["gain"], row["gain_sq"], branch_states)
        result[name] = {
            "reset_capable_states": row["capable"],
            "reset_capable_fraction_branch": row["capable"] / branch_states,
            "immediate_success_states": row["immediate"],
            "immediate_fraction_reset_capable": (
                row["immediate"] / row["capable"]
            ),
            "forced_reset_mean_success_reset_capable": (
                row["forced_sum"] / row["capable"]
            ),
            "cancel_option_gain_branch": mean,
            "cancel_option_gain_branch_se": se,
            "cancel_option_gain_branch_95ci": ci,
            "cancel_option_gain_reset_capable": row["gain"] / row["capable"],
        }

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=1_000_000)
    parser.add_argument("--seed", type=int, default=20261008)
    args = parser.parse_args()

    import json

    print(json.dumps(simulate(samples=args.samples, seed=args.seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
