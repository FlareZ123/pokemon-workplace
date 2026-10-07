from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from card_class_namespace import deck_name
from identity_materialization import IdentityLedger, materialize, move_instance
from multicopy_zone_state import ZoneCountState
from prize_belief_kernel import PrizeBelief
from prize_inference_from_search import infer_exact_prize_belief_after_full_deck_search

lele = deck_name("Tapu Lele-GX").token()
gladion = deck_name("Gladion").token()
physical = IdentityLedger(ZoneCountState.from_mapping({
    (lele, "prize"): 1,
    (gladion, "deck"): 1,
}))
prior = PrizeBelief.from_hypergeometric(
    {"lele": 1, "gladion": 1}, pool_size=53, prize_count=6
)
assert not prior.is_exact() and prior.entropy_bits() > 0.0

exact = infer_exact_prize_belief_after_full_deck_search(
    physical,
    {"lele": lele, "gladion": gladion},
    {"lele": 1, "gladion": 1},
    prize_count=6,
)
assert exact.is_exact() and exact.entropy_bits() == 0.0
state, probability = exact.state_dicts()[0]
assert probability == 1.0
assert state == {"lele": 1, "gladion": 0}

after = materialize(
    physical, card_class=gladion, card_name="Gladion",
    source_zone="deck", instance_id="gladion-copy"
)
after = move_instance(after, "gladion-copy", "hand")
assert infer_exact_prize_belief_after_full_deck_search(
    after,
    {"lele": lele, "gladion": gladion},
    {"lele": 1, "gladion": 1},
    prize_count=6,
).state_dicts() == exact.state_dicts()

print("search Prize inference regressions passed")
