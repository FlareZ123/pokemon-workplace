"""SFT: complete physical Aichi Bellelba-discard first-reset payoff witness."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.aichi_post_gnh_prize_reset import DECK, endpoint_success
from tools.aichi_jirachi_ticket_search import prepare_with_deferred_stellar, stellar_available
from tools.aichi_jirachi_payment_frontier import prior_full_deck_search
from tools.aichi_tagcall_payment_reachability import additional_tag_call
from tools.aichi_tagcall_bellelba_payload import (
    GNH, BELLELBA, PROTECTED_OUTPUTS,
    supplement_with_bellelba, endpoint_paths, chance,
)
from tools.aichi_repeated_ticket_access import PACKAGES


ORDER=(
    52,19,25,26,57,41,33,
    29,22,56,28,27,24,
    1,
    50,39,49,13,36,10,20,34,51,32,17,23,11,38,31,9,2,
    5,18,58,6,48,42,37,59,4,44,30,0,46,55,21,7,8,
    15,40,16,53,3,12,43,54,35,45,47,14,
)
assert len(ORDER)==60 and sorted(ORDER)==list(range(60))


def main():
    opener=tuple(DECK[i] for i in ORDER[:7])
    prizes=tuple(DECK[i] for i in ORDER[7:13])
    drawn=DECK[ORDER[13]]
    first_five=tuple(DECK[i] for i in ORDER[14:19])
    state,deferred=prepare_with_deferred_stellar(list(ORDER))
    assert state is not None and state.active=="Jirachi"
    assert state.gnh_access and state.hand["Tag Call"]>=1
    assert state.remaining[GNH]==0 and state.remaining[BELLELBA]==1
    assert (deferred or stellar_available(list(ORDER),state.active))
    assert not prior_full_deck_search(list(ORDER),state.active,deferred)
    print("opening",opener)
    print("prizes",prizes)
    print("normal draw",drawn)
    print("initial unused Jirachi top five",first_five)
    print("G&H already reserved, hand",dict(state.hand))
    print("searchable G&H",state.remaining[GNH],
          "searchable Bellelba",state.remaining[BELLELBA])

    g_only=additional_tag_call(state)
    with_b=supplement_with_bellelba(state)
    assert g_only is None and with_b is not None
    assert with_b.hand[BELLELBA]==state.hand[BELLELBA]+1
    objective="item_plus_pidgeot"
    assignment=PACKAGES["two_tickets_one_map"]
    paths_regular=endpoint_paths(state,objective,PROTECTED_OUTPUTS)
    paths_protected=endpoint_paths(with_b,objective,frozenset((BELLELBA,)))
    paths_paid=endpoint_paths(with_b,objective,frozenset())
    old=chance(paths_regular,assignment,True)
    safe=chance(paths_protected,assignment,True)
    improved=chance(paths_paid,assignment,True)
    assert abs(old-1/9)<1e-14
    assert abs(safe-5/43)<1e-14
    assert improved==1.0
    paid_witness=[
        path for path in paths_paid
        if path.paid_with == ("Artazon",BELLELBA)
        and chance((path,),assignment,True)==1.0
    ]
    assert paid_witness
    selected=paid_witness[0]
    assert endpoint_success(objective, selected.hand, selected.remaining,state.active)
    assert selected.hand["Technical Machine: Evolution"]>=1
    assert selected.hand["Jet Energy"]>=1
    print("G&H payment",selected.paid_with)
    print("postpayment hand",dict(selected.hand))
    print("postpayment deck size",sum(selected.remaining.values()))
    print("before first-reset access",old)
    print("Bellelba protected first-reset access",safe)
    print("Bellelba discardable first-reset access",improved)
    print("local payoff above protected",improved-safe)
    print("PHYSICAL WITNESS VALIDATED")


if __name__=="__main__":
    main()
