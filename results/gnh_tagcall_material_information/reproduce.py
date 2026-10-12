"""SFT: independently enumerate physical Prize deals and Jirachi top-card samples."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from math import comb

from tools.gnh_tagcall_material_information import calculate, NAMED, EXTRA_GNH


def physical(
    unseen: int, prizes: int, inspect: int, penalty: Fraction,
) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction]:
    """Labeled physical-cards oracle, independent of four-name grouping."""
    cards = NAMED + tuple(f"GuzmaHala{i}" for i in range(EXTRA_GNH))
    cards += tuple(f"Filler{i}" for i in range(unseen-len(cards)))

    total = successful = 0
    base_keep = base_pay = base_k1 = thinned_keep = thinned_pay = thin_k1 = Fraction()

    def wish_success(pool: tuple[str, ...]) -> Fraction:
        targets = sum("Ticket" in chosen for chosen in combinations(pool, inspect))
        return Fraction(targets, comb(len(pool), inspect))

    for picked in combinations(cards, prizes):
        total += 1
        prized = set(picked)
        remaining = tuple(card for card in cards if card not in prized)
        available = tuple(card for card in remaining if card.startswith("GuzmaHala"))
        if not available:
            continue
        successful += 1
        retained_after_tagcall = set(available[:2])
        def stage(*, preview: bool, paid: bool) -> tuple[str, ...]:
            return tuple(
                card for card in remaining
                if (not preview or card not in retained_after_tagcall)
                and card != "Artazon"
                and (not paid or card not in ("TM", "Jet"))
            )

        keep, pay = wish_success(stage(preview=False, paid=False)), (
            wish_success(stage(preview=False, paid=True))-penalty)
        tkeep, tpay = wish_success(stage(preview=True, paid=False)), (
            wish_success(stage(preview=True, paid=True))-penalty)
        base_keep += keep
        base_pay += pay
        base_k1 += max(keep,pay)
        thinned_keep += tkeep
        thinned_pay += tpay
        thin_k1 += max(tkeep,tpay)

    assert successful > 0
    return (
        Fraction(successful,total),
        max(base_keep,base_pay)/successful,
        base_k1/successful,
        max(thinned_keep,thinned_pay)/successful,
        thin_k1/successful,
    )


def main() -> None:
    tested = 0
    for unseen in (8, 9, 10):
        for prizes in range(0, min(3, unseen-6)+1):
            for inspect in range(1,min(3, unseen-prizes-5)+1):
                for cost in (Fraction(), Fraction(1,100), Fraction(1,10)):
                    calc = calculate(unseen, prizes, inspect, cost)
                    brute = physical(unseen, prizes, inspect, cost)
                    assert (calc.successful_preview_probability, calc.baseline_k0,
                            calc.baseline_free_k1, calc.material_only_k0,
                            calc.material_plus_information) == brute, (
                            unseen, prizes, inspect, cost, calc, brute)
                    assert calc.gross_preview_gain == (
                        calc.material_gain + calc.preview_information_gain)
                    tested += 1
    print(f"PASS: {tested} exact models checked against labeled Prize and Wish enumeration")

    result = calculate(52, 6, 5, Fraction(10,2499))
    assert result.successful_preview_probability == Fraction(1104,1105)
    assert result.baseline_k0 == Fraction(5195,52992)
    assert result.baseline_free_k1 == Fraction(2406750833,24355993704)
    assert result.material_only_k0 == Fraction(17788265,172890816)
    assert result.material_plus_information == Fraction(3511495835,33886599936)
    assert result.material_gain > result.preview_information_gain > 0
    print("PASS: U52/P6 Tag Call two-copy thinning versus K1 decision separated")
    print("Tag Call successful mass:", result.successful_preview_probability)
    print("Baseline K0:", result.baseline_k0)
    print("Material-only K0:", result.material_only_k0)
    print("Material plus K1:", result.material_plus_information)
    print("Material delta:", result.material_gain)
    print("Information delta:", result.preview_information_gain)
    print("Total preview delta:", result.gross_preview_gain)


if __name__ == "__main__":
    main()
