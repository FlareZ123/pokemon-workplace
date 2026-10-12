"""SFT: exact physical labeled-card oracle and legal Regidrago swap."""
from collections import Counter
from datetime import date
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.regidrago_basic_search_frontier import Build, access
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

BASE = ROOT / 'results' / 'competitive_deck_baselines' / 'regidrago_haruku_2026.json'
CANDIDATE = Path(__file__).with_name('regidrago_extra_dragapult_minus_vip.json')


def physical(build: Build, *, prizes: int = 2, opener: int = 3) -> dict[str, Fraction]:
    groups = {
        'rv': (build.regidrago_v, True),
        'basics': (build.other_basics, True),
        'dp': (build.dragapult_ex, False),
        'vip': (build.vip_pass, False),
        'qb': (build.quick_ball, False),
        'mt': (build.mysterious_treasure, False),
        'safe': (build.safe_filler, False),
    }
    other = build.deck_size - sum(count for count, _ in groups.values())
    assert other >= 0
    groups['other'] = (other, False)
    cards = [
        (name, basic)
        for name, (count, basic) in groups.items()
        for _ in range(count)
    ]
    weighted = Counter()
    worlds = 0
    for opening in combinations(range(build.deck_size), opener):
        if not any(cards[i][1] for i in opening):
            continue
        after_opener = [i for i in range(build.deck_size) if i not in opening]
        for prize in combinations(after_opener, prizes):
            prize_set = set(prize)
            after_prize = [i for i in after_opener if i not in prize_set]
            for draw in after_prize:
                worlds += 1
                seen = Counter(cards[i][0] for i in (*opening, draw))
                deck = Counter(cards[i][0] for i in after_prize if i != draw)
                held = seen['rv'] > 0
                vip = seen['vip'] > 0
                paid_item = seen['qb'] + seen['mt'] > 0
                can_search = deck['rv'] > 0
                free = can_search and vip
                ideal = can_search and paid_item
                safe = ideal and seen['safe'] > 0
                payload = ideal and seen['dp'] > 0
                events = {
                    'regidrago_held': held,
                    'vip_held': vip,
                    'vip_only_when_no_regidrago': vip and not held,
                    'access_vip_or_held': held or free,
                    'access_any_ideal': held or free or ideal,
                    'access_any_safe': held or free or safe,
                    'access_with_payload_payment': held or free or safe or payload,
                    'vip_unique_safe': not held and free and not safe,
                    'vip_unique_ideal': not held and free and not ideal,
                    'searchable_regidrago': can_search,
                    'no_regidrago_held': not held,
                    'vip_out_accessible': not held and free,
                    'payload_payment_route': payload,
                    'payload_payment_unique': (
                        not held and not free and not safe and payload
                    ),
                }
                for key, occurred in events.items():
                    if occurred:
                        weighted[key] += 1
    return {key: Fraction(weighted[key], worlds) for key in events}


def verify_manifest() -> None:
    baseline = json.loads(BASE.read_text(encoding='utf-8'))
    candidate = json.loads(CANDIDATE.read_text(encoding='utf-8'))
    old = {row['name']: row for row in baseline['cards']}
    new = {row['name']: row for row in candidate['cards']}
    assert old.keys() == new.keys()
    for name in old:
        expected = old[name]['quantity']
        if name == 'Dragapult ex':
            expected += 1
        if name == 'Battle VIP Pass':
            expected -= 1
        assert new[name]['quantity'] == expected, name
        assert new[name]['print_id'] == old[name]['print_id'], name
        assert new[name]['category'] == old[name]['category'], name
    assert sum(row['quantity'] for row in candidate['cards']) == 60
    assert candidate['source']['classification'] == 'hypothetical research variant'
    records = load_all_card_records(ROOT / 'resources')
    basics = sum(
        row['quantity'] for row in candidate['cards']
        if records[row['print_id']].is_basic_pokemon
    )
    assert basics == 15
    proof = adjudicate_deck(
        tuple(DeckEntry(row['print_id'], row['quantity']) for row in candidate['cards']),
        ROOT / 'resources',
        as_of=date(2026, 10, 12),
    )
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == 'eligible_snapshot', proof.disposition
    assert all(p.eligibility == 'eligible' for p in proof.print_proofs)
    print('PASS 60-card candidate, 15 Basics, exact-print Expanded snapshot eligibility')


def verify() -> None:
    cases = (
        Build(regidrago_v=2, other_basics=2, dragapult_ex=1,
              vip_pass=1, quick_ball=1, mysterious_treasure=1,
              safe_filler=1, deck_size=12),
        Build(regidrago_v=2, other_basics=2, dragapult_ex=2,
              vip_pass=1, quick_ball=1, mysterious_treasure=1,
              safe_filler=1, deck_size=12),
        Build(regidrago_v=1, other_basics=1, dragapult_ex=2,
              vip_pass=2, quick_ball=2, mysterious_treasure=1,
              safe_filler=0, deck_size=11),
        Build(regidrago_v=1, other_basics=1, dragapult_ex=1,
              vip_pass=1, quick_ball=1, mysterious_treasure=2,
              safe_filler=1, deck_size=11),
    )
    for case in cases:
        exact = access(case, prizes=2, opener=3)
        oracle = physical(case)
        assert exact == oracle, {
            key: (exact[key], oracle[key])
            for key in oracle if exact[key] != oracle[key]
        }
        print('PASS independently labeled physical oracle', case)
    for disposable in (0, 5, 10, 20, 30):
        original = access(Build(safe_filler=disposable))
        candidate = access(Build(dragapult_ex=2, vip_pass=2, safe_filler=disposable))
        assert original['access_any_safe'] <= original['access_with_payload_payment']
        assert candidate['access_any_safe'] <= candidate['access_with_payload_payment']
        assert original['access_with_payload_payment'] <= original['access_any_ideal']
        assert candidate['access_with_payload_payment'] <= candidate['access_any_ideal']
        assert candidate['access_vip_or_held'] < original['access_vip_or_held']
        assert candidate['payload_payment_unique'] > original['payload_payment_unique']
        print('PASS sensitivity', disposable, {
            'published': f"{100 * float(original['access_with_payload_payment']):.9f}%",
            'candidate': f"{100 * float(candidate['access_with_payload_payment']):.9f}%",
        })
    verify_manifest()
    print('PASS exact Regidrago V access and legal candidate deck')


if __name__ == '__main__':
    verify()
