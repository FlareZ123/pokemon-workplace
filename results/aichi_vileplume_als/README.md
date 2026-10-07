# Aichi 2026 Vileplume Control: ALS consistency and connector allocation

## Question

How realistic is the first-turn-going-second Bunnelby line in Takahiro Ando's runner-up Vileplume Control deck from the 2026 Aichi Open League, and how much does connector allocation change the reachable endpoints?

The human prior describes the line as:

`Tag Call -> Guzma & Hala -> Jet Energy + TM: Evolution -> Bunnelby with Ω Barrage`

The published list gives enough redundancy to study the line as a state-dependent access problem.

Implementation: `tools/aichi_vileplume_als.py`

## Sources and deck identity

The official event page states that the Open League used Expanded regulation with 60-card decks and six Prize cards:

https://www.pokemon-card.com/info/005445.html

Limitless records Takahiro Ando in second place with Vileplume Control and lists the complete 60 cards:

https://www.limitlesstcg.com/tournaments/566/decklists

The relevant counts are:

- 4 Guzma & Hala and 4 Tag Call;
- 2 Bunnelby;
- 2 Technical Machine: Evolution;
- 2 Artazon;
- 2 Jet Energy;
- 1 Fan Rotom;
- 1 Jirachi;
- 2-2-2 Pidgeot ex;
- 2-2-1 Stoutland;
- 2-2-2 Vileplume plus 1 Vileplume-GX.

The bundled card database supplies the card texts used by the model. Important print IDs include `xy5-121` Bunnelby, `sm12-193` Guzma & Hala, `sm12-206` Tag Call, `sv4-178` Technical Machine: Evolution, `sv2-171` Artazon, `sv2-190` Jet Energy, `sv7-118` Fan Rotom, `sm9-99` Jirachi, `bw7-122` Stoutland, and `xy7-3` Vileplume.

## Why the line works

Bunnelby's Ω Barrage allows it to attack twice in one turn.

Technical Machine: Evolution costs one Colorless Energy and evolves up to two Benched Pokémon by searching the deck for cards that evolve from them. The Advanced Player's Rulebook states that this type of evolution effect can evolve during the first turn and can evolve a Pokémon that was put into play that turn unless the effect says otherwise.

Jet Energy both supplies the Colorless Energy and switches the Benched Bunnelby into the Active Spot.

Guzma & Hala can obtain a Stadium, a Pokémon Tool, and a Special Energy after discarding two other cards. This means one Supporter can supply Artazon, Technical Machine: Evolution, and Jet Energy.

Fan Rotom's Fan Call can search for up to three Colorless Pokémon with 100 HP or less during the first turn. In this list, the relevant Fan Call targets include Bunnelby, Pidgey, and Lillipup.

Artazon can instead put any non-Rule-Box Basic from the deck onto the Bench. It can therefore fetch Fan Rotom or patch a missing Basic directly.

Grand Tree is not treated as a first-turn substitute. Its own text prohibits evolving a Basic during the player's first turn and also prohibits evolving a Basic that entered play that turn.

## Model scope

The simulation conditions on an accepted seven-card opening containing at least one ordinary Basic Pokémon. There are 14 such Basics in the list. It then sets six Prize cards and draws one card for the first turn going second.

The Active choice uses Jirachi when Jirachi is in the opening, allowing one Stellar Wish before the line. Otherwise the model avoids starting Bunnelby when another Basic is available. Additional opening Basics stay in hand until the line needs them because setup Benching is optional.

Stellar Wish selects Guzma & Hala if present in the top five, with Tag Call as the fallback access card.

The reported route requires access to Guzma & Hala either directly or through Tag Call. This is deliberate. Natural hands that already contain the complete TM, Jet, and board package without Guzma & Hala are outside this measurement.

For each endpoint, the planner allocates the single Artazon use between a direct Basic and Fan Rotom. Fan Call then supplies any relevant missing small Colorless Basics that remain in the deck.

Evolution targets must still be in the deck when Technical Machine: Evolution resolves.

No opponent interaction is modeled. Matchup-specific preservation, Item lock from the opponent, Ability lock, strategic DCI costs, later-turn value, and full-game policy remain outside this result.

## Main result

A matched Monte Carlo run used 500,000 accepted-opening trials with seed `20261007`.

| Endpoint | Endpoint-aware probability | Approx. 95% Monte Carlo half-width |
| --- | ---: | ---: |
| Guzma & Hala access | 71.7356% | 0.1248 pp |
| Bunnelby double-Evolution core | 69.0818% | 0.1281 pp |
| Pidgeot ex Stage 2 established | 58.7272% | 0.1365 pp |
| Stoutland Stage 2 established | 47.9258% | 0.1385 pp |
| Pidgeot ex + Stoutland Stage 2 | 41.5690% | 0.1366 pp |
| Vileplume Item lock established | 32.9538% | 0.1303 pp |
| Vileplume Item lock + Pidgeot ex | 23.4156% | 0.1174 pp |
| Vileplume Item lock + Stoutland Stage 2 | 19.2330% | 0.1092 pp |

The Pidgeot and Stoutland rows mean that the Stage 2 is in play after the second Evolution attack. Stoutland's Sentinel requires Stoutland to be Active, so that row does not imply immediate Supporter lock. Vileplume's Irritating Pollen is an in-play Ability, so the Vileplume endpoint does establish Item lock as the turn passes.

The exact accepted-opening probability with 14 forced Basics is 86.140932%. The exact expected failed mulligans before acceptance is 0.160888. The 500,000-trial run produced 0.161318.


## Named route versus the broader first-turn ALS

The main 500,000-trial table deliberately requires Guzma & Hala access.

A second endpoint-aware planner allows the same TM: Evolution plus Jet Energy plus Bunnelby endpoint to be reached either through Guzma & Hala or through naturally drawn resources. When Jirachi starts Active, it also lets Stellar Wish choose among the relevant Trainer cards in the top five instead of always prioritizing Guzma & Hala or Tag Call.

A matched 100,000-state run with seed `20261007` gives:

| Endpoint | G&H-mediated route | Any modeled route | Increment outside named route |
| --- | ---: | ---: | ---: |
| Bunnelby double-Evolution core | 69.0900% | 70.0980% | +1.0080 pp |
| Pidgeot ex Stage 2 | 58.7290% | 59.4220% | +0.6930 pp |
| Stoutland Stage 2 | 48.1110% | 48.6780% | +0.5670 pp |
| Pidgeot ex + Stoutland | 41.7190% | 42.1810% | +0.4620 pp |
| Vileplume Item lock | 33.1290% | 33.4780% | +0.3490 pp |
| Item lock + Pidgeot ex | 23.6360% | 23.8600% | +0.2240 pp |
| Item lock + Stoutland | 19.5230% | 19.7030% | +0.1800 pp |

For the core, the named Guzma & Hala route accounts for about 98.56% of successes found by this broader planner.

This supports the ALS abstraction used in the human prior. The named line captures nearly all modeled first-turn executions of the same board plan, while a small residual comes from natural TM/Jet combinations and alternative Stellar Wish choices.

The broader planner still targets the same Bunnelby, Jet Energy, and TM: Evolution mechanism. It is not a complete enumeration of every possible first-turn play in the deck.

## Finding 1: the headline ALS is genuinely high-AMR within its stated route

The Guzma & Hala access rate is about 71.7%, and about 69.1% of accepted openings reach the Bunnelby plus TM: Evolution plus Jet Energy core.

The gap between those values is small because Guzma & Hala covers the Tool and Special Energy channels simultaneously. Artazon and Fan Rotom cover much of the Basic access channel.

This makes the line qualitatively different from a four-card combo assembled by independent natural draws.

## Finding 2: connector allocation changes the Vileplume result materially

A first-pass policy always used Artazon to fetch Fan Rotom when Fan Rotom was not already available. That policy is dominated in some Item-lock states because Fan Call cannot fetch Oddish.

The matched 500,000-state comparison is:

| Endpoint | Greedy Artazon -> Fan | Endpoint-aware routing | Improvement |
| --- | ---: | ---: | ---: |
| Vileplume Item lock | 25.4210% | 32.9538% | +7.5328 pp |
| Item lock + Pidgeot ex | 21.2934% | 23.4156% | +2.1222 pp |
| Item lock + Stoutland Stage 2 | 17.4674% | 19.2330% | +1.7656 pp |

The other modeled endpoints are unchanged by this routing choice.

This is a concrete instance of connector domination. Artazon has at least two strategically distinct uses inside the same ALS. Treating `Artazon -> Fan Rotom` as the default edge can reduce line success even though Fan Rotom is a powerful connector.

## Finding 3: Fan Rotom and Artazon carry different parts of the redundancy

A 120,000-trial sensitivity run used the same seed for each configuration.

| Configuration | Core | Pidgeot | Stoutland | Pidgeot + Stoutland | Item lock | Item + Pidgeot | Item + Stoutland |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full endpoint-aware model | 69.0300% | 58.7300% | 48.0617% | 41.7217% | 33.1683% | 23.6725% | 19.5583% |
| No Stellar Wish | 66.5225% | 56.6225% | 46.3892% | 40.2858% | 31.9650% | 22.9083% | 18.9350% |
| No Fan Rotom | 68.9617% | 27.3033% | 22.6175% | 7.4700% | 27.4775% | 8.9233% | 7.4233% |
| No Artazon | 23.3050% | 12.6108% | 10.5533% | 7.4658% | 5.2950% | 2.4458% | 2.0667% |
| No Fan Rotom or Artazon | 15.1658% | 3.7525% | 3.1900% | 0.5642% | 3.6325% | 0.6567% | 0.5642% |

Fan Rotom is especially important for establishing multiple Colorless evolution lines because Fan Call can cover Bunnelby, Pidgey, and Lillipup with one Ability.

Artazon is the larger enabler of the core because Guzma & Hala can search it and Artazon can then create the missing Basic channel. It is also the only modeled connector that can directly patch Oddish.

Jirachi contributes a smaller access increase. In this model, Stellar Wish raises Guzma & Hala access by about 2.6 percentage points.

## Finding 4: search-target depletion creates a zone inversion

Technical Machine: Evolution searches the deck for the evolution card. An evolution card drawn into the opening hand or first-turn draw cannot be used by that search effect unless another copy remains in the deck.

This makes some otherwise valuable cards liabilities for the exact first-turn ALS when they leave the deck too early.

Conditioning on an accepted opening and then exposing the six Prize cards plus the first-turn draw gives these exact availability ceilings for non-Basic search targets:

- a singleton non-Basic remains in the deck with probability 77.162486%;
- at least one copy of a two-copy non-Basic remains with probability 95.094061%;
- for a 2-copy Stage 1 plus a 2-copy Stage 2 chain, at least one of each remains with probability 90.371427%;
- for Herdier at two copies plus singleton Stoutland, at least one of each remains with probability 73.241397%.

The Stoutland line therefore has a materially lower search-target ceiling before Basic access, G&H access, or board routing is considered.

This is a useful ALS-specific extension of ordinary Prize-risk modeling. For deck-search evolution attacks, being drawn can remove a target from the searchable zone in the same way that being Prized does.

## Finding 5: the Supporter-lock endpoint needs an additional positioning step

Stoutland's Sentinel only applies while Stoutland is Active.

The Bunnelby ALS ends with Bunnelby Active because Jet Energy promoted it before the two Evolution attacks. Evolving Lillipup through Herdier into Stoutland on the Bench establishes the Stage 2 body but does not create Sentinel immediately.

This distinction matters for simulations that label every successful Stoutland evolution as an immediate lock state.

Vileplume behaves differently. Irritating Pollen applies while Vileplume is in play, so a Bench evolution can turn on Item lock immediately.

## Discard-cost interpretation

Guzma & Hala requires two other cards from hand for the Tool and Special Energy search.

Under the sequencing in this model, the player delays optional setup Benching and plays Guzma & Hala before spending other hand resources. The immediate line has enough hand volume to pay the two-card cost mechanically.

That does not make the discard strategically free. The model allows the player to burn cards whose later-game value could be high. A full DCI-aware policy should score the future loss of those resources.

## Validation and reproducibility

`tools/aichi_vileplume_als.py` contains the exact published deck counts, setup conditioning, first-turn state generation, card-access planner, greedy routing policy, endpoint-aware routing policy, and deterministic random seed.

The planner asserts state by state that the greedy connector policy never exceeds the endpoint-aware policy.

The mulligan portion has an exact combinatorial benchmark. Its simulated mean agrees with the exact expectation within ordinary Monte Carlo variation.

The card texts used for the interaction are available in the bundled database, so the result does not depend on a live website for the mechanics.

## Limitations

This is an ALS feasibility model rather than a full game simulator.

It does not value which Stage 2 pair is best in a matchup, model opponent disruption, decide whether revealing or discarding a resource is strategically acceptable, account for later recovery, optimize setup Active choice against every possible endpoint, or model natural-draw variants that skip Guzma & Hala.

The Artazon planner optimizes only the immediate named endpoint. A game-winning policy could prefer a lower immediate endpoint probability if it preserves stronger future resources or creates a better lock geometry.

The published list is one high-level tournament list. The result explains its internal access structure and should not be treated as a metagame-wide estimate.

## Next useful work

The strongest next extension is a small turn planner that treats ALS execution as a resource-allocation problem with explicit zones, connector capacity, Bench slots, Active positioning, and state-dependent discard value.

The Aichi list is a good test case because it contains a true multi-axis Supporter, a one-use Stadium connector, a three-target Ability connector, a two-attack Basic, several evolution endpoints, and both Active-dependent and passive locks.
