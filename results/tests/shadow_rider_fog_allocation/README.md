# Shared Fog Crystal allocation: Marshadow and Forest Seal Stone's Pokémon V

## Why this extension matters

The [Fog Crystal-to-Marshadow result](../shadow_rider_fog_marshadow/) introduced the champion's four Fog Crystal as a search route for **Marshadow**, allowing its Bench-only Resetting Hole to discard Path to the Peak. Fog Crystal may also search **Shadow Rider Calyrex V** (`swsh6-74`), a Basic Psychic Pokémon. When Forest Seal Stone is held, finding that V can enable the Tool's Star Alchemy to supply one missing launch piece.

One Fog Crystal only searches **one** Basic Pokémon. The branch choices therefore compete directly. Modeling them as two independent accessible paths would double-count a physical connector. The exact evaluator explicitly allocates `fog_for_marshadow + fog_for_v <= Fog Crystal copies held`.

## Exact method

Use the same 60-card capacities, accepted opening seven, first natural going-second draw, and six hidden Prize cards as the earlier studies. The counterfactual opposing board contains active Iron Thorns ex and Path to the Peak. A successful restricted Radiant Eternatus launch has two Shadow Rider VMAX left in deck, a usable Path counter, and either opening-Active Flutter or Canceling Cologne to neutralize the active Iron Thorns. Forest Seal Stone can access only one outstanding role after it is attached to a Pokémon V. Radiant's Climactic Gate ends the turn when used.

The model considers each allocation of the actually held Fog Crystal copies: zero or one retrieving Marshadow, plus zero or one retrieving Shadow Rider V, subject to the common hand budget, remaining deck identities, Bench-only Marshadow constraint, and Forest Seal Stone in hand. It integrates the conditional Prize survival of five identity categories (Radiant, Cologne, Marshadow, other Path answers, Shadow Rider V) and separately enforces survival of two VMAX. A five-bit exhaustion mask is derived by exact multivariate hypergeometric counting, using integer combination weights and `Fraction`.

The same **Energy-only Mysterious Treasure discard** constraint is maintained. Other Fog uses, Treasure paths, Quick Ball, draw supporters, opponent reactions, sequencing costs outside the enumerated actions, and actual match outcomes remain excluded. The added allocation is an optional action, so its exact endpoint cannot be worse than the narrower model.

## Results

Exact conditional first-turn access, by added Canceling Cologne / Flutter tech count:

| Cologne / Flutter | Fog to Marshadow only | Fog to Marshadow or V | Extra gain (pp) |
| --- | ---: | ---: | ---: |
| 0 / 0 | 0.000000% | 0.000000% | 0.000000 |
| 1 / 0 | 2.967210% | 3.321259% | 0.354049 |
| 0 / 1 | 2.873716% | 3.004208% | 0.130491 |
| 2 / 0 | 4.655582% | 5.037875% | 0.382293 |
| **1 / 1** | **5.039163%** | **5.426284%** | **0.387121** |
| 0 / 2 | 4.914216% | 5.127519% | 0.213303 |
| 3 / 0 | 5.650345% | 6.000842% | 0.350496 |
| 2 / 1 | 6.036099% | 6.408975% | 0.372876 |
| 1 / 2 | 6.310937% | 6.686917% | 0.375979 |
| 0 / 3 | 6.183379% | 6.432309% | 0.248930 |
| 4 / 0 | 7.083748% | 7.475526% | 0.391779 |
| 3 / 1 | 7.456445% | 7.871802% | 0.415357 |
| 2 / 2 | 7.762095% | 8.196133% | 0.434038 |
| 1 / 3 | 7.974356% | 8.409501% | 0.435145 |
| 0 / 4 | 7.821905% | 8.136873% | 0.314967 |

In the one-Cologne/one-Flutter case, the second Fog use increases the already-corrected access estimate by **0.387121 percentage points** (approximately **7.68% relative**). Against the original no-Fog Marshadow baseline of 2.811878%, the combined correction reaches **5.426284%**. The restricted access-maximizing mixture at each tech count remains (0,0), (1,0), (1,1), (1,2), and (1,3).

These comparisons do not price the lost Stadium or Trainer slots in experimental tech packages. They are conditional opening-line probabilities, **not match win rates** or rankings of competitively optimal decklists.

**Information-state caveat:** These exact card-access figures permit the feasibility evaluator to choose a path using the realized hidden Prize configuration, before any required deck inspection. Treat them as information-privileged feasibility bounds for the initial K0 state. A nonanticipatory opening policy must first choose an action using only observable cards and can condition later search decisions on K1 knowledge actually acquired. [The subsequent paid-search study](../shadow_rider_paid_search_allocation/) documents the distinction and additional connector competition.

## Reproducibility and scope

[Reproduce](reproduce.py) enumerates all 15 exact full-deck cases and checks the one-Cologne/one-Flutter overlap against the previous independent four-bit Prize model. It also validates the Fog Crystal, Shadow Rider Calyrex V, and Forest Seal Stone printing data. A **247,590-world independent labeled toy model** reproduces both no-V-search and V-search endpoints exactly. A manual-only Windows GitHub Actions workflow runs the regression without spending CI resources on every unrelated commit.

Further work should add paid Mysterious Treasure retrieval of either target and search for Psychic Energy via Fog, while tracking search-card and Energy discard consumption jointly. Full-game testing against capable opposing decks remains necessary to establish competitive value.
