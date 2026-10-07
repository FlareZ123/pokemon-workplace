# Bench-release action catalog: the timing cost of reclaiming support slots

## Question

After a transactional support Pokémon consumes a Bench slot, what explicit legal paper-Expanded effects can reclaim occupied Bench capacity by moving one of your Pokémon to hand or deck, or by discarding your own Benched Pokémon?

The preceding lifecycle result found that built-in self-removal is rare among literal hand-to-Bench trigger Pokémon and that every built-in route is an attack. This census broadens the search to **external release actions** anywhere in the legal card pool.

Implementation: `tools/bench_release_catalog.py`  
Reproducer: `results/bench_release_catalog/reproduce.py`

## Conservative catalog

The scanner finds 50 legal prints representing 22 conservative text/action signatures, 20 unique card names, and 22 conservative gameplay fingerprints.

| Action family | Unique names | Names |
| --- | ---: | --- |
| Item | 2 | Super Scoop Up; Scoop Up Cyclone |
| Ability | 2 | Corviknight; Hydreigon |
| Supporter | 8 | Acerola; Bellelba & Brycen-Man; Cassius; Cheren's Care; Giovanni's Exile; Penny; Professor Turo's Scenario; Volo |
| Attack | 8 | Chimecho; Cofagrigus; Dragapult; M Gardevoir-EX; Pelipper; Swoobat; Tsareena V; Virizion-GX |

Scoop Up Cyclone appears as three conservative text signatures because the bundled prints use slightly different wording. This result does not treat those wording differences as strategically meaningful.

## Main finding

Sixteen of the 20 names reclaim Bench capacity through an **attack** or a **Supporter**. These channels compete with scarce action windows because using an attack ends the turn and a Supporter normally consumes the one Supporter play for the turn.

Only four names sit outside those two timing classes:

- **Super Scoop Up**, an Item whose release depends on a coin flip;
- **Scoop Up Cyclone**, a deterministic Item but an ACE SPEC;
- **Corviknight**, whose Flying Taxi release is tied to evolving into Corviknight from hand;
- **Hydreigon**, whose Weed Out Ability keeps exactly three chosen Benched Pokémon and discards the rest, so it is not a generic single-target pickup action.

The existence of a release edge therefore does not imply that Bench occupancy is cheap to reverse.

## Representative release semantics

Super Scoop Up can return one of your Pokémon and attached cards to hand, but its release is stochastic. Scoop Up Cyclone does the same deterministically, while its ACE SPEC status creates major deck-building opportunity cost.

Penny can return a Basic Pokémon and attached cards. Professor Turo's Scenario can return a Pokémon in play while discarding its attachments. Cassius shuffles a Pokémon and attachments into the deck. These release channels compete directly with draw, gust, setup, disruption, Prize recovery, and other Supporter uses. Other Supporters are narrower through damage, type, Bench-state, or Rule Box restrictions.

Corviknight's Flying Taxi is tied to an evolution trigger and itself requires board infrastructure. Hydreigon's Weed Out chooses three Benched Pokémon and discards the rest, so it is a coarse board-reset effect rather than a generic one-slot pickup action.

The eight attack-based channels include direct pickup or shuffle effects such as Pelipper's Courier, Swoobat's Happy Return, Chimecho's Homeward Chime, and Virizion-GX's Breeze Away-GX, plus attacks that discard Benched Pokémon for value. These require an attacker, attack access, and the attack window for the turn.

## Relation to Bench debt

The preceding results establish three constraints around transactional support Pokémon:

1. `setup_trigger_role_contention/`: a support Basic may be consumed by the mandatory starting Active role before its trigger is available;
2. `bench_trigger_access/`: reaching the correct card identity in the wrong zone can create fictitious trigger access;
3. `bench_trigger_lifecycle/`: most literal trigger Pokémon have no built-in self-removal.

This catalog adds the external release layer. Release mechanisms exist, but most live in action classes with meaningful contention.

A useful state evaluator should therefore treat occupied Bench slots as persistent state and model release edges with their real action type. A Supporter pickup should consume Supporter capacity. An attack pickup should consume the attack window. A stochastic Item should preserve its branch probability. An ACE SPEC should preserve its deck-construction exclusivity.

## Method and coverage

The scanner starts from legal Black & White-onward prints using the repository's existing legality overlay. It inspects Trainer text, Abilities, and attacks for conservative wording families that explicitly put in-play Pokémon into hand, shuffle Pokémon into deck, discard own Benched Pokémon, or make both players discard down to a smaller Bench through an explicit effect.

A broader wording audit was used to identify false positives such as Energy and Tool movement. The parser intentionally avoids treating replacement effects such as Thorton as Bench release because the replacement still occupies the same slot.

## Limits

This is a conservative text-structured catalog rather than a complete semantic rules engine. It does not attempt to capture every indirect way a Bench slot can become empty, such as Knock Outs, opponent-driven removal, Stadium maximum-Bench changes caused by Stadium transitions, or multi-card lines without one direct release sentence.

The catalog also does not decide whether paying a release cost is strategically correct. A Supporter or attack release may be legal while a competing use of that same action window is stronger.

## Next useful work

The next state model should combine **persistent occupancy** with **typed release actions**. A support transaction should consume one slot from entry until a real release transition occurs, and the release transition should carry its action-class cost and restrictions.

That representation can answer how many transactional support activations fit beside a four-slot core board, whether a planned second support activation is blocked by a first support Pokémon that remains in play, and whether spending a Supporter or attack to reclaim the slot is feasible before the next required board state.
