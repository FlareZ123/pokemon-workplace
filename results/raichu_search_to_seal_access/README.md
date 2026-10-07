# Harto Miki Raichu/Electrode: executable search-to-Forest-Seal sequencing

## Question

How much additional direct access to the singleton Alolan Raichu comes from using Harto Miki's two Quick Ball, or an otherwise stranded Ultra Ball, to find Crobat V before using an exposed Forest Seal Stone?

This extends `results/raichu_forest_seal_access/`. The earlier component only credited Forest Seal Stone when Crobat V was already exposed or had been chosen as the setup Active Pokemon. The new model admits two concrete search-to-gate continuations while preserving discard costs and Prize information timing.

Implementation: `tools/raichu_search_to_seal_access.py`  
Independent labeled regression: `results/raichu_search_to_seal_access/reproduce.py`

## Deck and card basis

The modeled Harto Miki package contains:

- 1 Alolan Raichu;
- 2 Gladion;
- 3 Ultra Ball;
- 1 Computer Search;
- 1 Forest Seal Stone;
- 2 Crobat V;
- 2 Quick Ball;
- 11 Special Energy treated as disposable non-starters under the preserved conservative DCI policy;
- 1 Giratina treated as both setup-eligible and disposable;
- 13 other setup-eligible Basic Pokemon.

The published 2024 Champions League Aichi list has exactly these counts for the named cards. The bundled card database gives the relevant text semantics used here: Quick Ball `swsh1-179` discards one other card to search a Basic Pokemon, Ultra Ball searches any Pokemon after a two-card discard, Crobat V `swsh3-104` is a Basic Pokemon V, Forest Seal Stone `swsh12-156` gives an attached Pokemon V the Star Alchemy VSTAR Power, and Gladion `sm4-95` retrieves a face-down Prize card.

## Modeled action policies

The direct baseline is unchanged from the preceding results. It credits Alolan Raichu already in hand, Ultra Ball or Computer Search to Raichu when Raichu remains in deck, Gladion already in hand when Raichu is Prized, and Computer Search to Gladion after its deck inspection reveals that Raichu is absent.

The direct-ready Forest Seal layer is also unchanged. Forest Seal Stone succeeds when the Tool is exposed, Crobat V is already available in play or hand, and Star Alchemy can search Raichu or a deck-resident Gladion.

The new executable continuations are:

`Quick Ball -> Crobat V -> Forest Seal Stone -> Star Alchemy -> Raichu or Gladion`

Quick Ball pays one card from the conservative disposable pool before inspecting the deck. It always searches Crobat V for this policy. After that search establishes the Prize state, Star Alchemy takes Raichu if Raichu remains in deck or Gladion if Raichu is Prized.

`Ultra Ball -> inspect deck -> Raichu if present, otherwise Crobat V -> Forest Seal Stone -> Gladion`

Ultra Ball pays its two-card discard cost before deck inspection. If Raichu is present, the ordinary direct line takes it. If Raichu is absent and therefore known Prized, Ultra Ball can take Crobat V, then Forest Seal Stone can take a remaining Gladion. This is one causal policy because the target choice occurs during the search, after the deck is visible.

Computer Search does not create an additional gate-completion gain for this narrow objective. If Raichu is in deck it can take Raichu directly; if Raichu is Prized and Gladion is in deck it can take Gladion directly.

## Exact integration method

The state starts with a seven-card opening conditioned on at least one setup Basic. Setup chooses the Active Pokemon in the same objective-specific order as the preceding Forest Seal result: Crobat V first, another protected starter second, and Giratina last.

The game order sets six Prize cards and then exposes one later random draw. The calculation integrates the later draw before the Prize sample. This is only a probability-factorization change. Conditional on the opening, both procedures generate the same joint partition of the remaining cards because

`1 / C(53,6) / 47 = 1 / 53 / C(52,6)`.

After the later draw is fixed, only the Prize counts of Alolan Raichu, Gladion, and Crobat V can change the modeled search destinations. All other Prize identities can therefore be marginalized as one category. This reduces the exact calculation substantially while preserving the relevant joint state.

## Main result

Baseline assumptions are 60 cards, seven-card valid opening, six Prize cards, one later random draw, the preserved 12-card discard pool, no relevant Item/Tool/Ability lock, available Bench space, an unused VSTAR Power, and an open Tool slot on Crobat V.

| Measurement | Exact probability |
| --- | ---: |
| Valid opening before conditioning | 90.077711% |
| Singleton Alolan Raichu Prized | 10.052903% |
| Direct Ultra Ball / Gladion / Computer Search baseline | 30.578700% |
| Direct-ready typed Forest Seal access | 33.139533% |
| Search-completed typed Forest Seal access | **34.466609%** |
| Search-to-gate gain over direct-ready Forest Seal | **+1.327077 pp** |
| Incremental Quick Ball states | +1.253545 pp |
| Incremental Ultra Ball pivot states after Quick Ball attribution | +0.073531 pp |
| Incremental Quick Ball states below the two-card discard threshold | +0.763831 pp |
| Hypothetical ungated Forest Seal access | 40.261571% |
| Remaining ungated overstatement after search-to-gate sequencing | **5.794962 pp** |

Search-to-gate sequencing recovers 18.6334% of the earlier 7.122039-point direct-ready gate gap. The majority of the physical prerequisite remains relevant.

## Finding 1: Quick Ball supplies almost all of the new gate-completion value

Quick Ball accounts for 1.253545 of the 1.327077 new percentage points under the disjoint route attribution, or 94.4591% of the gain.

Its lower payment threshold is central. Of the Quick Ball increment, 0.763831 points occur in states with enough conservative discard material to pay Quick Ball while the two-card Ultra Ball or Computer Search cost remains unavailable. That is 60.9337% of Quick Ball's incremental contribution.

This is a concrete interaction between connector typing and DCI. Two Pokemon-search Items can point at the same Crobat V gate while having materially different executable reach because one consumes half as much current discard stock.

## Finding 2: Ultra Ball gains a small state-adaptive second role

The direct model used Ultra Ball only as a route to Alolan Raichu. Search-to-gate sequencing adds a second output policy in target-Prized states: pay the cost, inspect the deck, observe Raichu's absence, take Crobat V, then use Forest Seal Stone to find Gladion.

After states already gained by Quick Ball are assigned to Quick Ball, this Ultra Ball pivot contributes 0.073531 percentage points overall. Its raw route is available in 0.109197% of modeled states before overlap removal.

The small average value is strategically concentrated. Conditional on Alolan Raichu being Prized, direct-ready Forest Seal access is 31.781059%; executable search-to-gate sequencing raises it to **33.825012%**, a 2.043953-point conditional gain.

## Finding 3: most new access occurs while Raichu is still in deck

Of the 1.327077-point total increment, 1.121600 points occur in states where Raichu remains in deck. The remaining 0.205477 points occur in target-Prized states.

This means the most common benefit is structurally simple: Forest Seal Stone is already exposed, Crobat V is missing, and Quick Ball converts a one-card discard into the Pokemon V prerequisite that lets Star Alchemy search Raichu.

## Finding 4: search reachability still does not erase the physical Tool gate

The ungated universal-search abstraction gives 40.261571% access. After adding the executable Quick Ball and Ultra Ball continuations, the typed model reaches 34.466609%.

The remaining 5.794962-point gap can arise from missing Forest Seal Stone, missing or Prized Crobat V, absent playable Pokemon search, insufficient discard material, or the modeled output being unavailable. A graph edge from Forest Seal Stone to any card still overstates realized access unless those prerequisite states are represented.

## Evidence type and validation

The 60-card values are exact combinatorial calculations under the stated state partition and action policy.

The independent regression uses a separate labeled 13-card deck. It exhaustively enumerates every valid three-card opening, every disjoint two-card Prize set, and every legal next draw. Setup movement, one-card and two-card discard thresholds, direct Forest Seal readiness, Quick Ball gate completion, and the Ultra Ball Prize-state pivot are evaluated directly from physical labels. Every reported probability field matches the category model to floating-point tolerance.

The new implementation also reproduces the preceding 30.578700% direct baseline, 33.139533% direct-ready Forest Seal result, and 40.261571% ungated comparison within numerical tolerance.

## Limitations

This remains a direct-access component rather than a full deck simulator. It assumes open Bench and Tool capacity, no relevant lock, an unused VSTAR Power, and a Crobat V that can be put into play when exposed.

The model still omits Crobat V's Dark Asset draw, Dedenne-GX, Squawkabilly ex, Battle Compressor, Rescue Stretcher, Hisuian Heavy Ball, evolution readiness for Alolan Raichu, Electrode-GX setup, Energy requirements, competing uses of Quick Ball and Ultra Ball, VSTAR Power opportunity cost, and matchup-specific preservation rules. The discard policy remains the same conservative binary pool used by the earlier agent2 results.

## Next useful work

The strongest deck-specific continuation is to add Crobat V's Dark Asset as a real draw transition after a search-to-Crobat line. That extension should preserve the hand-size-dependent number of cards drawn and should compare whether using Quick Ball or Ultra Ball to materialize Crobat improves Raichu access enough to justify the connector and Bench commitment.

A second useful continuation is to execute representative successful and failed Harto states through the repository's newer conserved Trainer transaction and turn-budget kernels. That would test whether the exact category result survives the shared physical-state infrastructure without turning the deck-specific model into a separate simulator.
