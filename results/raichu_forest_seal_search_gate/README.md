# Harto Miki Raichu/Electrode: Forest Seal Stone search-to-gate sequencing

## Question

Once Forest Seal Stone is exposed but Crobat V is missing, how much additional Alolan Raichu access comes from using Harto Miki's Pokemon-search Items to complete the Pokemon V gate?

This follows:

- `results/raichu_prize_access/`, which establishes the corrected discard-aware, Prize-aware direct baseline;
- `results/raichu_forest_seal_access/`, which preserves Forest Seal Stone's Pokemon V requirement but only credits Crobat V that is already exposed.

Implementation: `tools/raichu_forest_seal_search_gate.py`  
Independent exhaustive regression: `results/raichu_forest_seal_search_gate/reproduce.py`

## Deck basis

Harto Miki's 13th-place Champions League Aichi Expanded list contains:

- 1 Alolan Raichu;
- 2 Gladion;
- 3 Ultra Ball;
- 2 Quick Ball;
- 1 Computer Search;
- 1 Forest Seal Stone;
- 2 Crobat V;
- the 12-card conservative discard pool used by the preceding result.

Published list: <https://limitlesstcg.com/decks/list/11221>

The bundled card database gives the relevant search semantics:

- Quick Ball discards another card and searches for a Basic Pokemon;
- Ultra Ball discards two cards and searches for a Pokemon;
- Forest Seal Stone gives an attached Pokemon V the Star Alchemy VSTAR Power, which searches the deck for any card;
- Crobat V is a Basic Pokemon V.

Alolan Raichu is a Stage 1, so Quick Ball cannot take it directly. That target restriction is central to this result.

## Executable policies

The model preserves the corrected setup and discard state from the preceding work and adds the two Quick Ball copies as their own category.

### Direct-ready Forest Seal Stone

If Forest Seal Stone and Crobat V are already available, Star Alchemy searches:

- Alolan Raichu when it remains in the deck;
- Gladion when Raichu is Prized and a Gladion remains in the deck.

### Quick Ball to Crobat V

If Forest Seal Stone is exposed and Crobat V is missing:

`Quick Ball -> Crobat V -> Forest Seal Stone -> Star Alchemy`

Quick Ball must have one modeled disposable card available. Crobat V must remain in the deck.

This line does not require advance knowledge of Raichu's zone. Quick Ball cannot search the Stage 1 target directly, so Crobat V is the useful target for this narrow objective. The Quick Ball search itself then exposes the remaining deck before Star Alchemy chooses Raichu or Gladion.

### Ultra Ball adaptive pivot

Ultra Ball behaves differently:

- if Raichu remains in the deck, Ultra Ball can take Raichu directly;
- if the search reveals Raichu is absent, Ultra Ball can instead take Crobat V;
- Forest Seal Stone can then use Star Alchemy for a Gladion that remains in the deck.

The executable Prized-target line is therefore:

`Ultra Ball -> inspect deck -> Raichu absent -> Crobat V -> Forest Seal Stone -> Gladion -> Raichu`

Ultra Ball still pays its two-card discard cost before searching.

Computer Search is already a universal direct connector in the baseline. On this narrow target-access objective, spending Computer Search on Crobat V does not improve on taking Raichu or Gladion directly.

## Main result

Assumptions match the prior one-draw Harto model:

- 60 cards;
- accepted seven-card opening;
- six Prize cards;
- one later random draw;
- 16 setup-eligible starters;
- Giratina cross-classified as both starter and discard candidate;
- 11 Special Energy plus Giratina as the conservative disposable pool;
- no Bench, Tool, Item, Ability, or VSTAR lock;
- unused VSTAR Power;
- open Tool slot on the relevant Crobat V.

| Policy | Exact access |
| --- | ---: |
| Corrected Ultra Ball / Gladion / Computer Search baseline | 30.578700% |
| Direct-ready typed Forest Seal Stone | 33.139533% |
| Direct-ready + Quick Ball gate completion | 34.393078% |
| Direct-ready + Ultra Ball gate completion | 33.226835% |
| Full typed Quick Ball + Ultra Ball gate completion | **34.466609%** |
| Ungated Forest Seal Stone abstraction | 40.261571% |

Adding the executable search-to-gate routes raises access by **1.327077 percentage points** over direct-ready Forest Seal Stone, for a total **3.887909-point** gain over the corrected pre-Stone baseline.

The typed model still remains **5.794962 points** below an ungated representation.

## Finding 1: Quick Ball gains value through complementarity

Quick Ball's marginal contribution over direct-ready Forest Seal Stone is **1.253545 points**.

This is strategically notable because Quick Ball cannot search for Alolan Raichu at all. Its value comes from satisfying Forest Seal Stone's missing Pokemon V prerequisite.

In this state representation, a narrow Basic-Pokemon search can therefore be more useful to the Raichu-access objective than its direct target relation suggests.

The raw Quick Ball-to-Crobat route exists in 1.805394% of states, but some of those states already succeed through another route. The policy-level marginal is the smaller 1.253545-point value.

## Finding 2: Ultra Ball's gate-completion value is small and concentrated

Ultra Ball's marginal contribution as a Crobat V gate completer is **0.087302 points** over direct-ready Forest Seal Stone.

After Quick Ball gate completion is already available, Ultra Ball contributes only another **0.073531 points**.

The reason is structural:

- when Raichu remains in the deck, Ultra Ball already solves the target directly;
- the Crobat pivot only creates new access when Raichu is Prized;
- Ultra Ball also requires two acceptable discards.

The raw Ultra Ball-to-Crobat gate route appears in 0.133827% of states, with part of that mass overlapping other successful lines.

## Finding 3: target restriction can create connector complementarity

Quick Ball is narrower than Ultra Ball because it searches only Basic Pokemon. Here, that restriction does not make it irrelevant.

Alolan Raichu is a Stage 1, so Quick Ball cannot consume itself on the final target. With Forest Seal Stone exposed, its useful role is naturally redirected toward Crobat V.

Ultra Ball has a stronger direct target relation, which means much of its apparent gate-completion option is dominated by its simpler Raichu search.

This is a concrete example where connector value depends on the downstream prerequisite graph and competing uses, rather than the breadth of the connector's immediate output set.

## Finding 4: information arrives inside the search action

The Ultra Ball pivot is executable without omniscient Prize knowledge.

A player who has Forest Seal Stone exposed can play Ultra Ball under K0 uncertainty. During the deck search:

- if Alolan Raichu is present, take it;
- if the singleton is absent, infer the relevant Prize state and take Crobat V instead;
- use Star Alchemy for Gladion.

The choice of Ultra Ball output is made after the search has exposed the deck.

This is another case where a connector performs both information acquisition and material access during one action.

## Raichu-Prized states

Conditional on Alolan Raichu being Prized:

| Policy | Conditional access |
| --- | ---: |
| Corrected baseline | 29.209000% |
| Direct-ready Forest Seal Stone | 31.781059% |
| Direct-ready + Quick Ball | 33.093567% |
| Direct-ready + Ultra Ball pivot | 32.649485% |
| Full typed search-to-gate policy | **33.825012%** |

The search-to-gate layer therefore adds useful rescue mass exactly where Ultra Ball's ordinary direct-target edge disappears.

## Evidence type and validation

The 60-card values are exact under the stated state partition and policy.

The implementation uses a reduced exact state representation:

1. the opening state preserves Crobat V, Giratina, other starters, and the discard categories separately;
2. setup materializes the mandatory Active Pokemon;
3. after setup, categories whose distinctions can no longer affect the objective are collapsed;
4. Prize states are enumerated exactly;
5. later random exposure is averaged without replacement.

The reduction preserves the relevant physical distinctions while avoiding unnecessary state explosion.

The independent regression uses a labeled 13-card deck and does not call the category-model enumeration helpers. It exhaustively enumerates accepted openings, disjoint Prize sets, and the next draw, then applies the Quick Ball and Ultra Ball policies directly from card labels.

## Limitations

The model still omits:

- Crobat V's Dark Asset;
- Quick Ball or Ultra Ball into other draw-engine Pokemon;
- Battle Compressor;
- Dedenne-GX and Squawkabilly ex;
- Hisuian Heavy Ball;
- Bench capacity;
- Tool-slot contention;
- VSTAR contention;
- Item, Ability, and Tool locks;
- the actual Pikachu / Ditto Prism Star evolution requirement;
- Electrode-GX and Energy-loading readiness;
- opponent interaction;
- state-dependent reasons to preserve Quick Ball, Ultra Ball, or the modeled discard cards.

The Active-Pokemon selection remains objective-specific and should be replaced by a wider policy once those board-state factors are modeled.

## Next useful work

The strongest continuation is to incorporate the draw-engine branch created by **Quick Ball -> Crobat V -> Dark Asset**.

That extension needs an explicit hand-size transition because Dark Asset draws until the player has six cards. Search and discard actions change hand size before Dark Asset resolves, so the number of cards drawn depends on sequencing. Forest Seal Stone can then be used before or after Dark Asset, and the optimal ordering may depend on whether deck inspection has already revealed the singleton's Prize state.

This is a natural next test of action order, connector domination, information timing, and dynamic discardability.
