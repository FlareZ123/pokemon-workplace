"""SFT: exact T2 natural evolution materials for fourth-place 2026 Aichi Raichu.

A valid starting seven, ordinary draw before turn one, ordinary draw on turn
two, and zero other draw/search effects. Prizes are marginalized. Both bases
must be available at the end of the first own turn, both evolutions by turn two.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from itertools import product

from reproduce import (
    MANIFEST, choose, native_bases, source_card,
    two_evolution_bases, validate_sources,
)

# Voltorb, Pikachu, Ditto, Electrode-GX, Alolan Raichu,
# other Basic Pokemon, and remaining cards.
POP = (2, 1, 1, 3, 2, 9, 42)


def count_sequential() -> tuple[int, int, int]:
    """Seven-hand multiplicities times two sequential one-card draw outcomes."""
    denominator = 0
    full = 0
    native = 0
    for six in product(*(range(n + 1) for n in POP[:-1])):
        x = 7 - sum(six)
        if not 0 <= x <= POP[-1]:
            continue
        seven = (*six, x)
        v, p, d, _, _, o, _ = seven
        if v + p + d + o == 0:
            continue
        mult = math.prod(choose(n, k) for n, k in zip(POP, seven))
        denominator += mult * 53 * 52

        for i in range(len(POP)):
            first_remaining = POP[i] - seven[i]
            if first_remaining <= 0:
                continue
            eight = list(seven)
            eight[i] += 1
            if not two_evolution_bases(*eight[:3]):
                continue
            native_first_eight = native_bases(eight[0], eight[1])
            for j in range(len(POP)):
                second_remaining = POP[j] - eight[j]
                if second_remaining <= 0:
                    continue
                nine = list(eight)
                nine[j] += 1
                if nine[3] > 0 and nine[4] > 0:
                    subtotal = mult * first_remaining * second_remaining
                    full += subtotal
                    if native_first_eight:
                        native += subtotal
    return denominator, full, native


def count_eight_plus_one() -> tuple[int, int]:
    """Independent eight-card hypergeometric grouping plus ninth-card supply."""
    full = 0
    native = 0
    for six in product(*(range(n + 1) for n in POP[:-1])):
        x = 8 - sum(six)
        if not 0 <= x <= POP[-1]:
            continue
        eight = (*six, x)
        v, p, d, electrode, raichu, *_ = eight
        if not two_evolution_bases(v, p, d):
            continue
        mult = math.prod(choose(n, k) for n, k in zip(POP, eight))
        if electrode and raichu:
            ninth_options = 52
        elif electrode:
            ninth_options = POP[4]
        elif raichu:
            ninth_options = POP[3]
        else:
            ninth_options = 0
        full += mult * ninth_options
        if native_bases(v, p):
            native += mult * ninth_options
    return full, native


def main() -> None:
    validate_sources()
    q = {
        row["name"]: row["quantity"]
        for row in json.loads(MANIFEST.read_text(encoding="utf-8"))["cards"]
    }
    assert q["Electrode-GX"] == 3 and q["Alolan Raichu"] == 2
    assert source_card("sm7-48")["evolvesFrom"] == "Voltorb"
    assert source_card("sm11-57")["evolvesFrom"] == "Pikachu"
    assert sum(POP) == 60

    denominator, full, native = count_sequential()
    independent_full, independent_native = count_eight_plus_one()
    initial_valid = Fraction(choose(60, 7) - choose(47, 7), choose(60, 7))
    assert denominator == (choose(60, 7) - choose(47, 7)) * 53 * 52
    # A qualifying first-eight selection necessarily started with a valid
    # opening seven, because one subsequent draw cannot create two Basic roles.
    assert Fraction(full, denominator) == (
        Fraction(independent_full, choose(60, 8) * 52) / initial_valid
    )
    assert Fraction(native, denominator) == (
        Fraction(independent_native, choose(60, 8) * 52) / initial_valid
    )

    full_prob = Fraction(full, denominator)
    native_prob = Fraction(native, denominator)
    dependent_prob = full_prob - native_prob
    assert full_prob == Fraction(1269021526, 222764325069)
    assert native_prob == Fraction(41327540, 17135717313)
    assert native_prob > 0 and dependent_prob > 0

    print(json.dumps({
        "event": "two evolution bases by first own turn; Electrode-GX and Alolan Raichu in nine cards by second",
        "conditional_valid_opening_seven": True,
        "full_natural_t2_material_probability": float(full_prob),
        "native_bases_t2_material_probability": float(native_prob),
        "ditto_dependent_t2_material_probability": float(dependent_prob),
        "ditto_fraction_of_qualifying_t2_material": float(dependent_prob / full_prob),
        "exact_full_fraction": str(full_prob),
        "exact_native_fraction": str(native_prob),
        "method_agreement": "sequential labeled hand and eight-plus-one independent count",
        "limit": "Physical material only: excludes full attack Energy, search, evolution lock, opponent, KO",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
