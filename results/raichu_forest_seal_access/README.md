# Harto Miki Raichu/Electrode: typed Forest Seal Stone access

## Question

How much does Forest Seal Stone improve direct access to the singleton Alolan Raichu in Harto Miki's 2024 Aichi Raichu/Electrode list once the Tool's actual Pokemon V gate is preserved?

This result extends `results/raichu_prize_access/`, which now models the overlap between Giratina's setup eligibility and discardability. It isolates one additional access layer before adding longer search-to-gate or draw-engine sequences.

Implementation: `tools/raichu_forest_seal_access.py`  
Independent exhaustive regression: `results/raichu_forest_seal_access/reproduce.py`

## Card and deck basis

The modeled list contains:

- 1 Alolan Raichu;
- 2 Gladion;
- 3 Ultra Ball;
- 1 Computer Search;
- 1 Forest Seal Stone;
- 2 Crobat V;
- 11 Special Energy treated as disposable non-starters under the preserved DCI policy;
- 1 Giratina treated as both a setup starter and a disposable card;
- 13 other setup-eligible starters.

Forest Seal Stone is a Pokemon Tool whose Star Alchemy VSTAR Power lets the attached Pokemon V's player search the deck for any card. The gate therefore has at least two distinct physical requirements: the Tool must be available and a Pokemon V must be available to receive it.

The result treats Crobat V as the relevant Pokemon V because Harto's list contains two copies. Crobat V is also a Basic Pokemon and therefore participates in valid-opening conditioning and setup materialization.

## Modeled action window

The baseline action snapshot follows:

1. condition on a valid seven-card opening;
2. move one setup-eligible Basic from the opening hand into the Active Spot;
3. set six Prize cards from the remaining deck;
4. expose one additional random card;
5. evaluate direct Alolan Raichu access.

The access package includes:

- Alolan Raichu already exposed in hand;
- Ultra Ball to Raichu when Raichu remains in the deck and the two-card discard cost is payable;
- Gladion already in hand when Raichu is Prized;
- Computer Search to Raichu when it remains in the deck;
- zone-adaptive Computer Search to Gladion when Raichu is Prized;
- Forest Seal Stone when the Tool is exposed and Crobat V is already available.

For the Forest Seal Stone route, if Raichu remains in the deck, Star Alchemy can take Raichu directly. If Raichu is Prized and a Gladion remains in the deck, Star Alchemy can take Gladion and the same action window can use that Supporter to retrieve Raichu.

This result deliberately does not use Ultra Ball, Computer Search, Quick Ball, or another effect to first find a missing Crobat V or Forest Seal Stone. Those longer paths are a separate sequencing problem.

## Setup policy

Crobat V, Giratina, and 13 other cards are setup-eligible starters.

When several starters are present in the opening hand, the narrow direct-access policy chooses the Active Pokemon in this order:

1. Crobat V;
2. another non-disposable starter;
3. Giratina.

This preserves Giratina in hand as a possible discard whenever another starter can satisfy setup. Crobat V is preferred because putting it Active already satisfies the Pokemon V side of the Forest Seal Stone gate. The model does not use Crobat V's Dark Asset draw Ability.

This is an objective-specific policy. A full gameplay planner may prefer a different Active Pokemon because retreat cost, Bench plans, Dark Asset timing, matchup pressure, or other considerations matter.

## Main result

Baseline assumptions:

- 60 cards;
- valid seven-card opening;
- six Prize cards;
- one later random draw;
- 16 setup-eligible starters;
- 12-card conservative discard pool with Giratina cross-classified as a starter;
- one Forest Seal Stone;
- two Crobat V;
- VSTAR Power unused;
- Crobat V has an open Tool slot;
- no relevant Tool, Ability, Item, or Bench lock.

| Measurement | Exact probability |
| --- | ---: |
| Valid opening before conditioning | 90.077711% |
| Singleton Alolan Raichu Prized | 10.052903% |
| Corrected Ultra Ball / Gladion / Computer Search baseline | 30.578700% |
| Forest Seal Stone exposed in the action hand | 12.874837% |
| Crobat V available in play or hand | 27.432224% |
| Both Forest Seal Stone and Crobat V ready | 3.264545% |
| Forest Seal Stone treated as ungated universal search | 40.261571% |
| Forest Seal Stone with the Pokemon V gate preserved | **33.139533%** |

The typed Forest Seal Stone layer adds **2.560832 percentage points** over the corrected baseline.

Treating Forest Seal Stone as a universal any-card search merely because its output says "search your deck for a card" would instead credit a **9.682871-point** gain over baseline. The difference between that ungated model and the typed model is **7.122039 percentage points**.

## Finding 1: gate readiness is much rarer than Tool exposure

Forest Seal Stone itself is exposed in 12.874837% of the modeled action snapshots. A Crobat V is available in 27.432224%.

Their joint readiness is only **3.264545%**.

The distinction matters because a graph with an edge such as:

`Forest Seal Stone -> any card`

silently collapses the Tool and Pokemon V requirements into the same event. The resulting graph makes a one-copy Tool look much closer to a standalone Computer Search than it is in this action window.

## Finding 2: the gate explains most of the apparent Forest Seal Stone gain

With the Crobat V requirement removed, Forest Seal Stone raises access from 30.578700% to 40.261571%.

With the gate preserved, access reaches 33.139533%.

The ungated representation therefore overstates the modeled access probability by **7.122039 points**. This is larger than Forest Seal Stone's actual typed contribution of 2.560832 points.

The result is a direct example of why connector evaluation needs typed prerequisites in addition to output domains.

## Finding 3: Prize-aware fallback still exists behind the Tool gate

Conditional on Alolan Raichu being Prized:

- the corrected baseline accesses it in 29.209000% of states;
- typed Forest Seal Stone raises that to **31.781059%**;
- ungated Forest Seal Stone would claim **38.935680%**.

Forest Seal Stone can therefore inherit the same zone-adaptive pattern already identified for Computer Search. When deck inspection establishes that the singleton target is absent, a universal search can switch its material output to Gladion.

The effect remains bounded by the Tool's own physical prerequisites.

## Evidence type

The 60-card values are exact calculations under the stated state partition and policy. Opening hands and Prize cards are integrated with multivariate hypergeometric probabilities; the later draw is averaged exactly without replacement.

The independent regression uses a separate labeled 12-card deck. It enumerates every accepted three-card opening, every disjoint two-card Prize set, and every possible next draw. Setup movement and the Forest Seal Stone/Crobat V gate are evaluated directly from card labels. The labeled result is compared field-by-field with the category model.

## Limitations

This is a direct-ready access component.

It assumes:

- VSTAR Power is unused;
- an available Crobat V can receive Forest Seal Stone;
- Crobat V can be put into play when it is in the action hand;
- Bench capacity permits that play;
- relevant Abilities and Tools are not locked;
- the opponent does not interfere before the modeled action window.

It omits:

- Quick Ball or Ultra Ball searching for Crobat V;
- Computer Search finding either Forest Seal Stone or Crobat V as an intermediate piece;
- Forest Seal Stone being retrieved by another Tool search;
- Crobat V's Dark Asset draw effect;
- Dedenne-GX and Squawkabilly ex;
- Battle Compressor;
- evolution readiness for Alolan Raichu;
- Electrode-GX and Energy loading;
- competing uses of the VSTAR Power;
- Tool-slot contention;
- Bench contention;
- matchup-specific sequencing.

The direct-ready result should therefore be read as a typed connector component, not full-deck consistency.

## Next useful work

The highest-value continuation is to add **search-to-gate sequencing** while preserving information timing and resource costs.

A particularly useful next transition is Quick Ball or Ultra Ball into Crobat V when Forest Seal Stone is already exposed. That path creates several interacting constraints:

- the Pokemon search itself has a discard cost;
- the search reveals the remaining deck before Forest Seal Stone chooses its output;
- Crobat V consumes Bench or Active space;
- Quick Ball and Ultra Ball have competing uses;
- Dark Asset may become available after Crobat V is benched;
- the deck may prefer to take Alolan Raichu directly with Ultra Ball instead of completing the Forest Seal Stone gate.

That extension should compare executable policies rather than simply adding graph reachability.
