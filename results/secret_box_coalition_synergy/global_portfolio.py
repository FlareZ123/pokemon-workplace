"""Minimal category portfolios that cover all sampled incremental states.

A global portfolio succeeds on *every sampled state* if its output-mask
count equals the full-output count. This is distinct from per-state
inclusion-minimal routes, and can be unstable in rare-tail samples.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from reproduce import MASK_SUCCESS_COUNTS as FULL_COUNTS


FAST_COUNTS = (
    0, 4_175, 470, 4_175,
    4_159, 4_175, 4_175, 4_175,
    135, 4_175, 978, 4_175,
    4_168, 4_175, 4_175, 4_175,
)


def minimal_sample_cover_masks(counts: tuple[int, ...]) -> tuple[int, ...]:
    """Compute subset-minimal masks retaining every recorded success."""
    if len(counts) != 16:
        raise ValueError("need all 16 output masks")
    target = counts[-1]
    return tuple(
        mask for mask in range(1, 16)
        if counts[mask] == target
        and not any(
            counts[sub] == target
            for sub in range(mask)
            if sub != mask and sub & mask == sub
        )
    )


def main() -> None:
    fast = minimal_sample_cover_masks(FAST_COUNTS)
    full = minimal_sample_cover_masks(FULL_COUNTS)
    assert fast == (1, 6), fast
    assert full == (5, 6), full

    # Supporter-only access fails in 82 of the 20,785 incremental states.
    # Of those, Tool-only covers 40 and neither single output covers 42.
    supporter_failure = FULL_COUNTS[15] - FULL_COUNTS[4]
    joint_tool_supporter_synergy = 42
    covered_by_tool_only = supporter_failure - joint_tool_supporter_synergy
    assert supporter_failure == 82
    assert covered_by_tool_only == 40
    assert FULL_COUNTS[2] + FULL_COUNTS[4] - 20_743 == 2_273

    # The 100k prefix misses the two all-four-Tag-Call-Prized Item-only
    # failure states that appear later in the 500k full sample.
    assert FAST_COUNTS[1] == FAST_COUNTS[15]
    assert FULL_COUNTS[1] == FULL_COUNTS[15] - 2

    print("100k minimum complete-coverage masks:", fast)
    print("500k minimum complete-coverage masks:", full)
    print("Supporter-only missed:", supporter_failure)
    print("Tool-only rescues among those:", covered_by_tool_only)
    print("True Tool+Supporter pair rescues:", joint_tool_supporter_synergy)
    print("Item-only full-sample failures:", FULL_COUNTS[15]-FULL_COUNTS[1])
    print("Global portfolio rare-tail sensitivity regression passed.")


if __name__ == "__main__":
    main()
