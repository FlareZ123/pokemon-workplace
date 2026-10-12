"""Physical 53-card placement oracle for conditioned two-VMAX launch."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.shadow_rider_conditional_vmax_draw import ConditionalVMAXDraw


def physical_oracle(model:ConditionalVMAXDraw)->tuple[Fraction,Fraction,Fraction]:
    """Independently enumerate VMAX physical placements among unseen slots.

    Slots [0:P) are six Prize cards. The next two positions represent the
    first and second cards of the randomized remaining draw deck. Uniform
    placement of the four VMAX physical identities is enough by symmetry.
    """
    n=model.deck_size-model.opening_size
    k=model.vmax_total-model.vmax_in_opening
    prize_count=model.prizes
    seen_first=seen_second=lost=total=0
    for positions in combinations(range(n),k):
        prized=sum(pos<prize_count for pos in positions)
        after_prize=k-prized
        first_remaining=after_prize-int(prize_count in positions)
        second_remaining=first_remaining-int(prize_count+1 in positions)
        first_ok=first_remaining>=model.min_remaining
        second_ok=second_remaining>=model.min_remaining
        seen_first+=int(first_ok)
        seen_second+=int(second_ok)
        lost+=int(first_ok and not second_ok)
        total+=1
    return Fraction(seen_first,total),Fraction(seen_second,total),Fraction(lost,total)


def test_small()->None:
    cases=(
        ConditionalVMAXDraw(11,3,2,3,0,2),
        ConditionalVMAXDraw(12,3,2,4,1,2),
        ConditionalVMAXDraw(13,4,3,4,0,3),
    )
    for model in cases:
        oracle=physical_oracle(model)
        assert oracle==(
            model.probability(1),model.probability(2),model.one_extra_draw_loss()
        )


def benchmark()->None:
    model=ConditionalVMAXDraw()
    first=model.probability(1)
    second=model.probability(2)
    loss=model.one_extra_draw_loss()
    assert loss==Fraction(189,58565)
    assert first==Fraction(58236,58565)
    assert second==Fraction(58047,58565)
    assert physical_oracle(model)==(first,second,loss)
    print('Condition: both Basic entry triggers + non-target Basic in opener, no VMAX initially held')
    print('One natural draw:',f'{float(first):.12%}')
    print('Bonus plus natural:',f'{float(second):.12%}')
    print('Loss from taking bonus:',f'{float(loss):.12%}',f'[{loss}]')
    print('PASS: physical assignment of four VMAX among all 53 unseen cards')


if __name__=='__main__':
    test_small()
    benchmark()
