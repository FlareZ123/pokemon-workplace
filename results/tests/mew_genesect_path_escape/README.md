# Mew/Genesect: Path-to-the-Peak early escape source frontier

## Question and deck proposal

The published 2026 Aichi Open League fifth-place Mew VMAX/Genesect V deck
includes **two Path to the Peak**, **two Sky Field**, **one Field Blower**,
**one Lost Vacuum**, and **three Trainers' Mail**. Path suppresses Genesect V's
Fusion Strike System Ability while in play. An opposing Path creates a
potentially severe draw-engine interruption.

What happens to early direct Path-removal *source access* if one of the
published two Path copies is exchanged for a third Sky Field?

The counterfactual is a complete sixty-card list defined by exactly:

- `Sky Field xy6-89`: 2 -> 3
- `Path to the Peak swsh6-148`: 2 -> 1

All other 58 physical cards are unchanged. The candidate keeps its 14
Pokémon, 42 Trainers, four Double Colorless Energy, eleven starting Basics
and one Secret Box ACE SPEC. The [executable regression](reproduce.py)
independently checks both list variants against the repository's paper
Expanded eligibility snapshot as of 2026-10-12.

## Exact results

The model conditions on a Basic-valid seven-card opening, six hidden Prize
cards, and the first natural draw, immediately after the opponent has put
Path to the Peak into play. It awards success when an eligible Path counter is
naturally held or reached through one or more *naturally held* Trainers' Mail.
Mail looks at four unseen deck cards per use, can choose one eligible Trainer,
and reshuffles the remaining inspected cards. Every held Mail is allowed
to resolve. Opposing Item lock is absent.

**Accessible counter cards:**

- Under the conservative restricted policy, two baseline Sky Field plus
  Field Blower are three accessible counter copies. The variant has four.
- Under the additional policy assuming Lost Vacuum's mandatory hand-to-Lost-
  Zone payment is available, the baseline has four counter copies and the
  variant has five. No strategic payment cost is scored.

| Source-access endpoint | Published Path2/Sky2 | Counterfactual Path1/Sky3 | Increase |
| --- | ---: | ---: | ---: |
| Counter accessible, excluding Lost Vacuum | 39.356522079% | 48.918875822% | +9.562353744 pp |
| Counter accessible, assuming Vacuum payable | 48.918875822% | 57.087568204% | +8.168692382 pp |
| Counter accessible given Genesect V naturally seen, excluding Vacuum | 37.954301459% | 47.315832734% | +9.361531275 pp |
| Counter accessible given Genesect V naturally seen, Vacuum payable | 47.315832734% | 55.373523050% | +8.057690316 pp |

The probability of naturally seeing at least one Genesect V in the first
eight physical cards, conditional on a Basic-valid seven-card opener, is
55.047009417% in both builds. The last two rows condition on this extra
event. They do **not** require Mew V to be present, a board to be fully
established, or Genesect's Ability to have already been used.

### Calculation

Let `O` be the number of modeled Path counter cards: 3 or 4 without
Vacuum, 4 or 5 if Vacuum is declared payable. Let `M=3` be the Mail count,
`G=4` Genesect V, `B=7` other eligible starting Basics, and
`R=60-G-B-O-M` other cards.

Enumerate every feasible multiset of the first eight *visible* cards.
Each class allocation receives the exact multivariate hypergeometric weight.
The conditional opening-validity weight excludes precisely the situations
where the eighth, post-Prize natural draw is the only Basic among the eight.

For a state with any held counter, access succeeds directly. Otherwise, if
`m` Mail copies are held and `p` counter copies are Prized, the deck after
the initial eight and six Prizes contains 46 cards with `O-p` counters.
The conditional Mail success probability is

```text
1 - [C(46 - (O-p), 4) / C(46, 4)]^m
```

weighted over the hypergeometric Prize distribution conditional on the
visible eight. A Mail miss leaves the shuffled deck's counter composition
unchanged, so repeated miss probabilities multiply. No Mail is allowed to
fetch another Mail, consistent with printed text.

A separate [labeled physical oracle](reproduce.py) exhausts all accepted
opening hands, Prize combinations, first draws and Mail top-card
inspection subsets for four toy decks. It matches the exact solver using
rational numbers, including the no-counter case and the Genesect-present
conditional numerator. The 60-card regression checks exact-print signatures
for all relevant Trainer cards and Genesect's Fusion Strike System Ability.

The proof passed [CI run 38293107728](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293107728).

## Strategic limits

This is a **restricted early-turn source-access comparison**. The model
omits Genesect draw actions, Quick Ball, Ultra Ball, Forest Seal Stone,
Secret Box, Stadium use on later turns, opponents' Item locks, and deliberate
discard of otherwise needed cards. In particular, Secret Box requires three
discard payments and can find a Stadium; a hand holding it may have an extra
route to Sky Field that is absent from the modeled source set.

The additional Sky Field is an immediate Path answer only if the turn's one
Stadium play is still available. A held Lost Vacuum requires a second card
available to put in the Lost Zone. Actual effects can be blocked or become
tactically inferior in particular game states.

**The counterfactual removes one copy of the deck's own Path to the Peak.**
That Stadium can disable opposing Rule Box Abilities; losing a copy may
worsen matchups where the published list deliberately plays Path after
using its own Genesect engine. Sky Field also widens both players' Bench
capacity and can create exposure when an eight-Bench state loses its Stadium.

There is no head-to-head game evidence supporting a higher match win rate
for this swap. It is a candidate for opponent-conditioned testing using the
pinned and behavior-audited headless engine.

## Reproduction

`tools/mew_path_escape_frontier.py` is the reusable Fraction-based source
solver. `results/tests/mew_genesect_path_escape/reproduce.py` contains the
independent physical oracle and deck-source legality assertions. The
automated workflow is
`.github/workflows/validate-mew-genesect-path-escape.yml`.

The source 60-card list appears in
[competitive deck baselines](../../competitive_deck_baselines/README.md).
