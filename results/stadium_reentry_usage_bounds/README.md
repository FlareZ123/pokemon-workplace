# Stadium return-to-play: exact identity-scope bounds

## Research question

A Stadium effect has been used once this turn. Can two Gothitelle
`xy3-41` Teleport Room sources move the **same physical Stadium card**
out of play and back, making its once-per-turn voluntary effect usable again?

The bundled Advanced Player's Rulebook and the located official Brooklet Hill
Q&A settle ordinary play quota versus effect placement, and establish that
a **different physical copy** gets a fresh voluntary effect use. They do not
directly settle returning the **same copy** through Teleport Room within one turn.

This result preserves that uncertainty explicitly, and computes exact
consequences under three transparent alternative usage scopes. It is a
model-boundary and sensitivity result, not a definitive ruling on same-copy
re-entry.

## Rule-grounded pieces

* Advanced Player's Rulebook I-B-04: only one ordinary Stadium play per turn;
  optional voluntary in-play Stadium effects can have their own once-per-turn
  timing.
* Gothitelle `xy3-41` Teleport Room: once during your turn before attacking,
  discard the current Stadium; if you did, put a differently named Stadium
  from your discard pile into play. This can be performed by different
  Gothitelle source instances without spending the ordinary Stadium-play quota.
* Grand Tree `sv7-136`: voluntary once-during-each-player's-turn effect,
  whose legal Stage 1 and optional Stage 2 evolution chain occurs within one
  activation. This experiment counts **activations**, rather than evolutions.
* Official Brooklet Hill FAQ: after one physical copy was used and removed
  with Field Blower, a **second physical copy** can be played and its
  once-per-turn effect used. This falsifies a blanket card-name-level
  usage ledger for the documented situation.

Relevant official ruling search:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%81%9B%E3%81%9B%E3%82%89%E3%81%8E%E3%81%AE%E4%B8%98&regulation_faq_main_item1=all

Relevant official Teleport Room clarification:
https://www.pokemon-card.com/rules/faq/details.php?id=9756

## Model and implementation

`tools/stadium_reentry_usage_bounds.py` uses the existing
`StadiumEntryState` as its **single canonical owner** of Stadium zone,
discard pile, ordinary Stadium play quota, and per-Gothitelle Ability usage.

A lightweight wrapper stores an entry epoch and historical successful Stadium
uses as triples `(epoch, physical_copy_id, name)`. No second physical card
inventory is constructed. When Teleport Room replaces the current Stadium,
the entry epoch increases. A transient `StadiumEffectState` projects the
current physical Stadium as an in-play instance for the existing effect-usage
kernel, without copying the material zones.

Three interpretations of the usage ledger:

1. **entry**: one use per in-play entry epoch. Re-entry of the same physical
   card generates a fresh allowance.
2. **physical_copy**: once a physical card has used its effect in a player's
   turn, leaving and re-entering does not refresh that copy.
3. **name**: once per name and player turn. This deliberately over-restrictive
   negative control conflicts with the second-copy Brooklet Hill ruling.

All three respect actual physical Teleport Room replacements and per-source
once-per-turn limits. The `entry` and `physical_copy` alternatives both
permit use of a *different* physical Stadium card upon return.

## Exact bounded exhaustive census

Initial state: Grand Tree copy 1 in play, one Brooklet Hill in discard,
optionally a second Grand Tree copy in discard, the ordinary Stadium-play
allowance already spent, and 0 to 4 declared unused Gothitelle source IDs.
No Item plays, Stadium plays, additional retrieval, attacks, locks, or
opponent actions. Enough legal Grand Tree targets are assumed, so each
available activation can hypothetically resolve successfully.

The search exhaustively explores all physical Teleport Room successor options,
source orders, and Grand Tree activation opportunities, then maximizes the
number of successful voluntary activations in the turn.

| Grand Tree copies | Gothitelle sources | Per entry | Per physical copy | Per name |
|---|---:|---:|---:|---:|
| 1 | 0 | 1 | 1 | 1 |
| 1 | 1 | 1 | 1 | 1 |
| 1 | 2 | 2 | 1 | 1 |
| 1 | 3 | 2 | 1 | 1 |
| 1 | 4 | 3 | 1 | 1 |
| 2 | 0 | 1 | 1 | 1 |
| 2 | 1 | 1 | 1 | 1 |
| 2 | 2 | 2 | 2 | 1 |
| 2 | 3 | 2 | 2 | 1 |
| 2 | 4 | 3 | 2 | 1 |

For the specified two-Stadium-name population, every return to Grand Tree
needs two Teleport Room uses: Grand Tree to Brooklet Hill, then Brooklet Hill
back to Grand Tree. Thus the per-entry maximum is
`1 + floor(n_gothitelle / 2)` for these 0 to 4 sources.
Under a physical-copy ledger, only `min(n_tree_copies,
1 + floor(n_gothitelle / 2))` activations are possible. The exhaustive
search independently verifies the formulas over the declared census.

A concrete same-copy witness is:

`Grand Tree G1 [use] -> Gothitelle A: Brooklet Hill B -> Gothitelle B:
Grand Tree G1 [possible second use]`

At the final state, entry-use would permit a second activation, whereas
physical-copy-use would reject it. The material card configuration and the
ordinary Stadium-play quota are **identical** in both branches.

A concrete different-copy witness, established in principle by the official
fresh-copy rule, is:

`Grand Tree G1 [use] -> Brooklet Hill B -> Grand Tree G2 [use]`

Both per-entry and per-physical-copy usage policies permit the second use.
The card-name policy wrongly blocks it.

## Reproduction

`python results/stadium_reentry_usage_bounds/reproduce.py`

The regression checks that all named cards are legal in the repository's
bundled Expanded snapshot, verifies the source and Stadium rules, asserts
actual source-specific Teleport Room usage and card-copy conservation,
checks the two identity witnesses, and runs the 10-case by 3-policy census.

This makes uncertainty explicit at the precise state boundary that
competing game-state models otherwise silently choose.

## Limitations and next work

* No located general or card-specific official ruling directly resolves the
  same-physical-copy reentry case. Further official evidence could eliminate
  one of the remaining branches. Do not report per-entry reuse as legal solely
  because the code can represent it.
* This is conditional availability of an effect source, not a guarantee of
  actionable Grand Tree evolution. Stage targets, deck contents, Prize cards,
  abilities under lock, and physical search are excluded.
* Four Gothitelle source IDs are a declared scenario. The model does not
  construct the Stage 2 board or evaluate its realistic cost.
* A full planner should combine the authoritative physical entry state, the
  source effects, and a single current turn budget. It should retain the
  copy-versus-entry policy distinction until verified by official rules.
