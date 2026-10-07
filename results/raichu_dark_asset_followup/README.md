# Harto Miki Raichu/Electrode: bounded connector follow-up after Dark Asset

## Question

The preceding first-order model stops after Crobat V's Dark Asset directly draws Alolan Raichu, Gladion, or Forest Seal Stone.

How much additional Alolan Raichu access appears if Dark Asset is allowed to draw an executable **Ultra Ball or Computer Search**, and the model then permits exactly one additional search action when its two-card discard cost is still payable?

Implementation: `tools/raichu_dark_asset_followup.py`  
Independent labeled regression: `results/raichu_dark_asset_followup/reproduce.py`

## Scope

This result deliberately adds one bounded continuation layer rather than a recursive full-turn planner.

It preserves the preceding Harto Miki assumptions:

- 60 cards;
- valid seven-card opening;
- six Prize cards;
- one later ordinary draw;
- conservative 12-card disposable pool;
- open Bench space;
- no relevant Item, Tool, or Ability lock;
- one unused VSTAR Power;
- ordinary one-Supporter bandwidth.

After Quick Ball or Ultra Ball searches a deck-resident Crobat V and Dark Asset resolves, the model now credits:

- a drawn Ultra Ball searching deck-resident Alolan Raichu when two disposable cards remain;
- a drawn Computer Search searching Alolan Raichu when it remains in deck;
- a drawn Computer Search searching Gladion when Alolan Raichu is known Prized and Gladion remains in deck.

The continuation stops after that search. It does not recurse into another draw engine, another Crobat V, Dedenne-GX, Squawkabilly ex, Battle Compressor, VS Seeker, or arbitrary follow-up actions.

## Main result

| Measurement | Exact probability |
| --- | ---: |
| Search-completed Forest Seal access | 34.466609% |
| First-order Dark Asset access | 35.092509% |
| **Bounded post-Dark-Asset connector access** | **35.225031%** |
| **Increment from one additional connector action** | **+0.132521 pp** |
| Quick Ball branch contribution | +0.128306 pp |
| Ultra Ball branch contribution after Quick | +0.004216 pp |
| Increment while Raichu remains in deck | +0.124815 pp |
| Increment while Raichu is Prized | +0.007707 pp |
| Target-Prized conditional access, first-order | 35.601961% |
| Target-Prized conditional access, bounded follow-up | **35.678624%** |

The Quick Ball branch supplies about 96.82% of the added value. The Ultra Ball branch supplies the remainder.

## Finding 1: draw-to-six can create a later cost gate, not only a direct hit

The first-order result treated Dark Asset as a direct exposure event. This extension shows another role.

A Dark Asset draw can expose a search connector, but the connector is useful only if its own discard cost remains payable after the earlier search-to-Crobat action.

For the Quick Ball branch:

`Quick Ball -> discard 1 -> Crobat V -> Dark Asset 1`

A newly drawn Ultra Ball or Computer Search needs two further disposable cards. The route therefore appears only in states that had at least three disposable cards before Quick Ball was paid.

This is a second-order DCI interaction. The first discard payment changes the feasibility of a later connector reached through the draw effect.

## Finding 2: Ultra Ball's deeper Dark Asset draw rarely rescues itself

Ultra Ball leaves a smaller hand and therefore Dark Asset draws two cards. That sounds favorable for follow-up search.

Its earlier two-card payment also depletes the same disposable stock needed by a drawn Computer Search. In the target-Prized branch, a follow-up Computer Search can still work in two ways:

1. at least two disposable cards remain after Ultra Ball, so drawing Computer Search is enough;
2. exactly one disposable remains, and the two-card Dark Asset sample contains both Computer Search and another conservative disposable card.

After integrating those conditions over Prize uncertainty, Ultra's extra bounded contribution is only **+0.004216 percentage points**.

The deeper draw and the higher payment therefore pull in opposite directions.

## Finding 3: almost all of the extension helps target-in-deck states

Of the +0.132521-point total gain:

- +0.124815 points occur while Alolan Raichu remains in deck;
- +0.007707 points occur while it is Prized.

When Raichu remains in deck, either Ultra Ball or Computer Search can become a direct target connector. When Raichu is Prized, only Computer Search can convert its unrestricted search into Gladion access under this bounded continuation.

This sharpens the earlier K0/K1 observation: information about the target's zone changes which newly drawn connectors are live.

## Exact marginalization of unspecified Prize identities

The preceding model explicitly tracks Prize counts for Alolan Raichu, Gladion, Forest Seal Stone, and Crobat V while aggregating other Prize identities.

This continuation additionally needs to know whether Ultra Ball, Computer Search, and conservative disposable cards survive the Prize zone.

Rather than expanding the state space to enumerate every such Prize composition, the implementation integrates them exactly with hypergeometric survivor moments.

For a subcategory with `n` cards inside an aggregated pool of size `O`, after `o` cards from that pool become Prizes:

- the expected surviving count is `n * (O-o) / O`;
- pair events use the exact two-card survival factor `(O-o)(O-o-1) / (O(O-1))`.

Because Dark Asset draws at most two cards in this snapshot, first and second moments are sufficient.

## Independent validation

The reproducer contains a separate labeled 14-card physical enumerator with:

- seven-card openings;
- setup materialization;
- an ordinary draw;
- two Prize cards;
- labeled Crobat V and Gladion copies;
- exact Quick Ball and Ultra Ball discard payments;
- physical search-to-Crobat movement;
- every one-card or two-card Dark Asset sample;
- one bounded post-Dark-Asset search action.

The labeled enumerator does not use the category-level survivor-moment formulas. It matches the exact model for state mass, pre-Dark-Asset access, first-order Dark Asset access, and bounded follow-up access to floating-point precision.

## Interpretation

The added probability is small, but the mechanism is structurally important.

A draw engine should not be represented only as "draw N cards" or "chance to hit target." Its value can depend on which connectors it exposes, whether earlier actions consumed the resources those connectors require, and whether information acquired earlier changes which outputs are strategically live.

This result therefore extends the repository's connector realism synthesis from:

`payment -> search -> draw volume`

to:

`payment -> search -> draw volume -> newly exposed action -> residual payment gate`

## Limits

This remains an access model for one singleton objective, not a full game or full turn evaluator.

It still omits:

- secondary Quick Ball lines that search other draw Pokémon;
- Dedenne-GX and Squawkabilly ex;
- repeated draw engines;
- Battle Compressor and VS Seeker;
- exact identities of discarded cards beyond the conservative disposable pool;
- Bench competition;
- lock effects;
- Supporter opportunity cost beyond assuming Gladion's window is unused;
- Forest Seal Stone's opportunity cost against other VSTAR Power uses;
- evolution and attack readiness;
- matchup-specific preservation.

Computer Search's unrestricted exact-one physical selection rule also matters on strategic misses, as documented in `results/unrestricted_search_selection/`. This result only executes Computer Search when the intended target or Gladion is actually available, so forced fallback selection does not affect the reported objective.

## Next useful work

The next deck-specific step is a small recursive turn planner over the same physical resource state. It should allow Dark Asset to expose Quick Ball, Ultra Ball, Computer Search, Forest Seal Stone, Gladion, and draw-engine Pokémon while preserving:

- exact card-zone movement;
- one-use Dark Asset;
- residual discard identities;
- one-Supporter bandwidth;
- one VSTAR Power;
- Bench capacity;
- K0/K1 timing.

An orthogonal integration remains valuable: execute representative Quick Ball and Ultra Ball witnesses through the repository's conserved Trainer transaction and Bench-state layers so the probabilistic model and physical state kernels share the same transition semantics.
