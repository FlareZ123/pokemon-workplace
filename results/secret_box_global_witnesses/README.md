# All four Secret Box search categories are needed for universal modeled first-turn coverage

## Claim, scope, and relation to the sample

The Aichi Vileplume 2026 ACE SPEC swap planner considers whether a going-second setup can produce **Bunnelby in play + Technical Machine: Evolution and Jet Energy held**. Full-output Secret Box generates 20,785 extra successes against Grand Tree in 500,000 accepted-opening samples. Within those samples, either **Item + Supporter** or **Tool + Supporter** alone preserves every incremental success.

That empirical complete-coverage statement is sharply limited: the [constructive state test](../secret_box_coalition_synergy/constructive_global_witnesses.py) gives three physically valid, fully ordered 60-card starting configurations from the published Aichi list. They all fail with the Grand Tree baseline and succeed with full-output Secret Box. Taken together, they prove that **each of Item, Tool, Supporter, and Stadium outputs is necessary to preserve all possible modeled incremental successes**, even though no proper subset is necessary on the observed 500k states.

This result applies to the *existing compressed first-turn-core planner and named 60-card deck*. It does not claim that all four searches are compulsory to resolve a literal Secret Box under printed rules or that the alternate ACE SPEC has zero value in other game states.

## Exact physically valid fixtures

The reproducer pins all seven opening cards, all six Prize cards, and the first-turn draw. It constructs a **unique-index permutation of all 60 physical cards** and feeds identical card positions into Grand Tree and Secret Box variants.

### 1. Supporter output is necessary

- **Opening seven:** Oddish; Grand Tree/Secret Box; Guzma; Cassius; Karen; Faba; Lusamine.
- **Six Prize cards:** Tag Call ×4, Pidgeotto, Gloom.
- **First-turn draw:** Plumeria.
- **All winning output masks:** `4,5,6,7,12,13,14,15` (every one includes Supporter).

The Item search for Tag Call is useless because all four copies are Prized. The required Jet Energy is missing from hand. The Supporter output can reach Guzma & Hala directly, then its paid mode obtains TM: Evolution and Jet Energy while its Stadium search obtains Artazon to Bench Bunnelby.

### 2. Tool and Stadium outputs are both necessary

- **Opening seven:** Oddish; Grand Tree/Secret Box; Jet Energy; Guzma; Cassius; Karen; Faba.
- **Six Prize cards:** Guzma & Hala ×4, Pidgeotto, Gloom.
- **First-turn draw:** Lusamine.
- **All winning output masks:** `10,11,14,15` (every one includes Tool and Stadium).

Jet Energy is held, but TM: Evolution and Bunnelby are missing. All Guzma & Hala copies are Prized, so Tag Call and direct Supporter output cannot supply the missing components. Tool obtains TM: Evolution, and Stadium obtains Artazon, which supplies Bunnelby.

### 3. Item output is necessary

- **Opening seven:** Oddish; Grand Tree/Secret Box; Bunnelby; TM: Evolution ×2; Guzma; Cassius.
- **Six Prize cards:** Stealthy Hood ×3, Counter Gain, Artazon ×2.
- **First-turn draw:** Karen.
- **All winning output masks:** `1,3,5,7,9,11,13,15` (every one includes Item).

The Prize cards exhaust *every other Tool* and both Artazon, while both TM: Evolution copies are already held. No Tool or Stadium output can add a disposable card. The opening hand contains Bunnelby and at least one protected TM, but no Jet.

An Item search obtains Tag Call, which in turn obtains Guzma & Hala and Bellelba & Brycen-Man. After Secret Box's three-card cost, the extra TAG TEAM and duplicate TM can pay Guzma & Hala's two-card optional discard, unlocking Jet. With Item removed, direct Supporter alone cannot pay its two-card cost without surrendering an essential held piece.

## Proof of universal necessity

Any fixed subset of output categories that preserves **all** complete-Secret-Box-only successes for the modeled deck must succeed in each constructed state.

- Fixture 1 forces Supporter (bit 4).
- Fixture 2 forces Tool (bit 2) and Stadium (bit 8).
- Fixture 3 forces Item (bit 1).

Therefore, its mask must contain `4|2|8|1=15`. Full-output mask 15 succeeds in each case. Since each fixture has a valid 60-card permutation and passes the exact planner, this is a constructive counterexample to every proper output subset being universally sufficient. The model's full-output function is the reference endpoint, so the all-four mask is trivially sufficient over all possible states by definition.

## Why Monte Carlo missed the Item-only exception

The six Prize cards in fixture 3 comprise exactly the three Stealthy Hood, one Counter Gain and two Artazon cards. Under an unconditioned uniformly shuffled 60-card deck, the chance that this *exact six-card set* occupies the Prize positions is

`1 / C(60,6) = 1/50,063,860`.

Even ignoring the additional opening-hand requirements, 500,000 samples would be expected to show fewer than 0.01 such Prize layouts. This is why the first-turn-core sample can show apparent universal two-category coverage even though an exact reachable state disproves it.

The condition that an opening hand contain a Basic Pokémon introduces a small selection effect; the simple probability above is for an unconditioned shuffled deck, and is used only to illustrate rarity. A stronger enumeration could count entire winning starting-state families, rather than relying on a specific constructed permutation.

## Reproduction and limitations

Run `python results/secret_box_coalition_synergy/constructive_global_witnesses.py` from repository root. It verifies card multiplicities, 60 unique physical positions, accepted basic opener, Grand Tree baseline failure, full Secret Box success, and each subset-mask outcome. [Passing CI run 38050810040](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38050810040).

The solver compresses several card identities, does not price future discard utility, and only models a constrained first-turn setup endpoint. These counterexamples are **proofs about that exact computational model**. They identify states a finite random sample can miss, and they motivate exact support-cover verification and more faithful state-level simulator coverage.
