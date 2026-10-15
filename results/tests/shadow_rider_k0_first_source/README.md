# Shadow Rider versus Iron Thorns: nonanticipatory first-search source

## Research question

The [prior K1 upper bound](../shadow_rider_paid_search_allocation/) allows the entire six-Prize configuration to influence the selected search route. It found **7.327398814%** first-turn access to Radiant Eternatus's two-VMAX launch under an opposing Path to the Peak + Active Iron Thorns ex board and a hypothetical champion 60 with one Canceling Cologne and one Flutter Mane. Can the first search *source* be chosen without prior knowledge of those Prizes, or does that upper bound depend on an information advantage available only after inspecting the deck?

For this **precisely restricted** source model, an exact K0 first-source policy achieves the original K1 feasibility result. That is a useful information-boundary result, subject to substantial gameplay limitations below.

## Mechanism

The decision observation contains only the accepted seven-card opener and the first natural draw, including their visible card identities. The six Prize cards are hidden. The player chooses **one initial source** without that information:

| First source | Legality and immediate transaction |
| --- | --- |
| Direct | Radiant, Path answer, and Thorns answer all already accessible; no search occurs |
| Fog Crystal | Play a held Fog; after inspecting deck, choose Marshadow, Shadow Rider Calyrex V or Basic Psychic Energy |
| Mysterious Treasure | Held Treasure; pay one held Basic Psychic Energy, inspect deck, then fetch Radiant/Marshadow/V |
| Quick Ball | Held Quick Ball; pay one held Basic Psychic Energy, inspect deck, then fetch Radiant/Marshadow/V |
| Forest Seal Stone | Held Stone with a held Shadow Rider V host; inspect deck, then fetch Radiant/Cologne/Marshadow/Path answer |

Source availability and mandatory payments are checked against the *visible* hand. The **search target** can depend on the Prizes inferred when a legal full-deck search is performed, as permitted by the bundled rules. The remaining actions are evaluated by the existing K1-style paid-search feasibility solver. Every physical Fog, Treasure, Quick Ball and Stone is consumed at most once; Treasure/Quick discard payments are actually removed from the hand.

For each observable opening/first-draw configuration `o`, sum the winning Prize-mask weights for each first source `a`. A K0 policy chooses the source maximizing that conditional sum. Crucially, this source choice is shared across all worlds with observation `o`; only the target and subsequent search choices may respond to later legal deck inspection.

## Exact conditional results

| Quantity | Exact full-60-card probability |
| --- | ---: |
| Prior K1 omniscient-source upper bound | **7.327398814%** |
| K0 first-source policy | **7.327398814%** |
| Gap caused by choosing the first source without Prize knowledge | **0.000000000 percentage points** |

A deterministic tie-break chooses the first equally optimal source in the table above. The successful-opening probability attributable to each resulting first-source choice is:

| Source choice | Weighted successful opening probability |
| --- | ---: |
| Direct | 0.754912715% |
| Fog Crystal | 4.105412612% |
| Mysterious Treasure | 1.929538251% |
| Quick Ball | 0.324318979% |
| Forest Seal Stone | 0.213216257% |

These five classes are mutually exclusive under the chosen deterministic K0 policy and sum to 7.327398814%. The figures **do not** measure how often each source is played in every game, or the chance that a particular source individually succeeds across all possible hands.

**Interpretation:** for every accepted observable opening configuration in this exact restricted model, at least one first-source choice covers every hidden-Prize world where a successful route exists. The source can be selected using the visible cards; upon searching, its target can be adapted to the revealed full-deck contents. This is stronger than merely discovering after the fact that a source works in each individual world.

## Validation

The [source-policy reproducer](reproduce.py) uses exact integer combinatorial weights over 60-card Basic-valid opening seven, first natural draw, and six hidden Prize cards. It imports the prior paid-search solver and its physical Prize-mask representation, and asserts exact equality to its published rational numerator `26946742764678720 / 367753188390588000`.

The [independent physical oracle](physical_oracle.py) enumerates **83,720 labeled small-deck opening/Prize/draw worlds**, grouping them by the player's actual observable cards. It finds 2,490 possible K1 launch worlds and 2,490 achievable with the K0 first-source commitment. It also checks mandatory paid-search cost and a Radiant-active Bench geometry rejection.

Both physical oracle and full-60-card calculation **passed manual Windows CI [run 38730079380](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38730079380)**. Reproduce with `python -m results.tests.shadow_rider_k0_first_source.physical_oracle` and `python -m results.tests.shadow_rider_k0_first_source.reproduce`.

## Important limitations

The finding removes one *specific* information privilege from a **restricted launch-access abstraction**. Its use of the original K1 feasibility continuation means this does **not** prove a complete executable turn policy or even an achievable end-to-end K0 launch percentage. Other sources, search targets, paid fodder besides Psychic Energy, whole-turn action ordering, Active/Bench movement, opposite-hand knowledge and strategic opportunity costs are intentionally omitted. Source targets remain limited to those used in the preceding study. The opposing Path + Thorns state is stipulated rather than sampled from a realistic opponent policy.

The [turn-boundary audit](../shadow_rider_thorns_continuation/) remains essential: Cologne expires with Climactic Gate's turn, whereas a surviving Active Flutter Mane can sustain suppression for next-turn Underworld Door. Achieving a first-turn launch does not establish a powered VMAX attack, matchup victory or win probability. No change to the tournament-supported champion list is justified by this information-boundary result alone.

**Next:** strengthen the K0 policy into explicit legal action traces, incorporate Flutter's survival and next-turn Energy/pivot paths, and test other opponent lock packages. A broader paid-search model may genuinely have nonzero first-source information value even though this restricted one does not.
