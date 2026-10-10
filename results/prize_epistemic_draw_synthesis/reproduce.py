"""Integration regression for the paper Expanded Prize epistemic/draw program.

Each component has its own focused oracle. This runner executes the shared
pre-existing foundations and the new bounded research regressions together,
so incompatible interface changes cannot silently split the result family.
"""

from pathlib import Path
from runpy import run_path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]

REGRESSIONS = (
    "results/prize_position_belief/reproduce.py",
    "results/prize_slot_visibility/reproduce.py",
    "results/prize_top_swap_belief/reproduce.py",
    "results/prize_position_top_swap/reproduce.py",
    "results/prize_swap_lumpability/reproduce.py",
    "results/observer_positioned_prize_truth/reproduce.py",
    "results/prize_position_choice_signaling/reproduce.py",
    "results/prize_choice_policy_information/reproduce.py",
    "results/prize_epistemic_trace/reproduce.py",
    "results/realized_prize_epistemic/reproduce.py",
    "results/prize_top_draw_pool/reproduce.py",
    "results/prize_top_two_order/reproduce.py",
    "results/prize_deck_prefix/reproduce.py",
    "results/prize_prefix_draw_exposure/reproduce.py",
    "results/prize_joint_draw_requirements/reproduce.py",
    "results/prize_resource_allocation_exposure/reproduce.py",
)


def main() -> None:
    started = perf_counter()
    for index, relative in enumerate(REGRESSIONS, start=1):
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        print(f"[{index}/{len(REGRESSIONS)}] {relative}", flush=True)
        run_path(str(path), run_name="__main__")
    print(
        f"PASS: all {len(REGRESSIONS)} integrated regressions; "
        f"elapsed {perf_counter() - started:.3f}s",
        flush=True,
    )


if __name__ == "__main__":
    main()
