# Prize-rescue collapse after mulligan conditioning

## Question

Does the exact initial-Prize rescue model change once Pokémon TCG setup is modeled literally, including the requirement that the accepted opening hand contain a legal setup starter?

Yes. The effect is usually modest for ordinary medium-Basic decks, but it is systematic and can be large enough to matter in low-starter decks. More importantly, it reveals a foundational modeling point: **after conditioning on a valid opening hand, individual cards do not all have the same 10% Prize probability.** Setup-eligible cards are less likely to be Prized, while non-starters are slightly more likely to be Prized.

This result extends `results/prize_rescue_collapse/`, which models Gladion-style rescue capacity exactly for a uniformly random initial Prize set. It preserves that model's key collapse condition while conditioning the Prize distribution on a valid opening hand.

Implementation: `tools/prize_rescue_start_condition.py`  
Reproducer and exhaustive checks: `results/prize_rescue_start_condition/reproduce.py`

## Rules basis

The bundled advanced manual specifies the setup order:

1. draw 7 cards;
2. if the player cannot legally establish a starting Pokémon, reshuffle and repeat;
3. after a valid opening is established, set the top 6 cards of the remaining deck face down as Prize cards.

For an ordinary deck, a valid opening requires at least one Basic Pokémon in the opening hand. Repeated mulligans therefore make the final deck order equivalent to a random order **conditioned on the opening hand containing a starter**.

The broader term **setup-eligible starter** is used here because the Expanded card pool contains legal card-text exceptions. Examples in the bundled database include:

- `Talonflame` (`xy11-96`, Stage 2), whose Gale Wings Ability can put it face down as the Active Pokémon during setup;
- `Manectric` (`sm7-52`, `smp-SM130`, Stage 1), whose Electric Start Ability can do so when going second and can also place it on the Bench;
- `Luxray` (`swsh12pt5-44`, Stage 2) with Explosiveness;
- `Cinderace` (`me1-28`, Stage 2) with Explosiveness;
- `Snorlax Doll` (`sv4-175`, Item), which can be put face down in the Active Spot or on the Bench as if it were a Basic Pokémon during setup.

Conversely, `Shedinja` (`swsh4-66`) is a Basic whose Shell Survival text says it cannot be put face down during setup. For exact work, “number of Basic Pokémon” is therefore only a proxy. The correct state variable is the number of cards that can legally satisfy setup under the current going-first/going-second and card-text conditions.

## Extension of the existing rescue model

The existing Prize-rescue result partitions the deck into critical singleton cards, Gladion-like rescue copies, and filler. If `c` critical cards and `g` rescue copies are Prized, and the deck contains `G` rescue copies total, the pre-Prize rescue package collapses when

`c > G - g`.

That logic remains unchanged here.

The new part is the probability assigned to each Prize composition after setup conditioning.

## Exact conditioned state probability

Partition the deck into six categories:

- critical starters;
- critical non-starters;
- rescue starters;
- rescue non-starters;
- filler starters;
- filler non-starters.

For a particular Prize state with category sizes `n_i` and Prize counts `x_i`, the ordinary multivariate-hypergeometric mass is

`prod_i C(n_i, x_i) / C(N, P)`.

Let:

- `N` = deck size;
- `P` = Prize count;
- `H` = opening-hand size;
- `S` = total setup-eligible starter cards in the deck;
- `s_p` = setup-eligible starters contained in this complete Prize state.

The probability that an unconstrained opening hand is valid is

`A = 1 - C(N-S, H) / C(N, H)`.

Given the complete Prize state, the opening hand is drawn from the `N-P` non-Prize cards, containing `S-s_p` starters. Its acceptance probability is

`A_state = 1 - C((N-P) - (S-s_p), H) / C(N-P, H)`.

Bayes conditioning gives the exact accepted-start Prize-state mass:

`P(state | valid opening) = P(state) * A_state / A`.

Summing these conditioned state masses over `c > G-g` gives the exact rescue-collapse probability after mulligan conditioning.

## Finding 1: 10% is not the exact post-mulligan Prize prior

The following table asks a simpler question first: after a valid 7-card opening and before any deck search, what is the probability that one particular card is among the six Prize cards?

| Setup-eligible starters in 60-card deck | Specific starter is Prized | Specific non-starter is Prized |
| ---: | ---: | ---: |
| 4 | 8.014732% | 10.141805% |
| 6 | 8.881400% | 10.124289% |
| 8 | 9.299996% | 10.107693% |
| 10 | 9.539251% | 10.092150% |
| 12 | 9.688890% | 10.077777% |
| 16 | 9.854516% | 10.052903% |
| 20 | 9.933009% | 10.033496% |

The unconditional marginal is 10% for every labeled card. The accepted-opening condition breaks that symmetry.

When a specific starter is in the Prize cards, that starter is unavailable to satisfy the opening-hand requirement, making that Prize configuration less likely to survive setup. When a specific non-starter is Prized, starter density in the remaining cards rises slightly, making the configuration more likely to survive setup.

This matters most for low-starter decks. With only four setup-eligible starters, a particular starter has only an 8.015% post-mulligan Prize probability, while a particular non-starter is at 10.142%.

### Implication for K0

Before the first deck search, K0 uncertainty should not generally assign every card an independent or even identical 10% Prize prior if the simulator is already conditioning on a valid setup. Card class relative to the setup rule changes the prior.

The effect is combinatorial rather than strategic. Whether the difference matters depends on the question being studied.

## Finding 2: non-starter rescue packages are slightly riskier after valid-start conditioning

Gladion is a non-starter. Many important singleton resources it might protect, such as Trainer cards or ACE SPECs, are also non-starters. Conditioning on a valid opening makes Prize configurations rich in those non-starters slightly more likely.

For a 60-card deck, six Prize cards, 12 setup-eligible starters, two non-starter rescue copies, and all modeled critical singletons also non-starters:

| Critical singletons | Uniform collapse | Valid-start collapse | Uniform collapse given any critical Prized | Valid-start collapse given any critical Prized |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0.058445% | 0.059818% | 0.584454% | 0.593561% |
| 2 | 0.224553% | 0.229753% | 1.172446% | 1.190747% |
| 3 | 0.538972% | 0.551273% | 1.958752% | 1.989357% |
| 4 | 1.034419% | 1.057675% | 2.943208% | 2.989209% |
| 5 | 1.736302% | 1.774733% | 4.124762% | 4.189200% |

The correction is not huge at 12 starters, but it consistently increases the risk for an all-non-starter package. With four critical singletons and two Gladion-like rescuers, the conditional collapse rate moves from 2.9432% to 2.9892%.

The larger lesson is methodological: a simulator that already models mulligans should not then draw Prize cards from an unconditional 60-card hypergeometric distribution as a separate independent step.

## Finding 3: critical card type changes package risk

Hold the deck at 12 setup-eligible starters, four critical singletons total, and two non-starter rescue copies. Move the four critical cards one at a time from the non-starter category into the starter category:

| Critical singletons that are starters | Valid-start collapse | Collapse given at least one critical is Prized |
| ---: | ---: | ---: |
| 0 | 1.057675% | 2.989209% |
| 1 | 1.038777% | 2.960701% |
| 2 | 1.018850% | 2.928397% |
| 3 | 0.997870% | 2.892152% |
| 4 | 0.975817% | 2.851819% |

Package reliability therefore depends on whether the protected resources themselves help satisfy setup. Treating all “critical singleton” cards as exchangeable is slightly wrong even before strategic differences are considered.

## Relation to the existing Prize-rescue result

`results/prize_rescue_collapse/` remains the cleaner unconditional topology baseline and captures an important effect that a simpler “target plus every Gladion are all Prized” formula misses: several critical Prizes can consume several rescue copies, because each played Gladion itself becomes a Prize.

This result does not replace that model. It adds a setup-conditioning layer. The same capacity condition `c > G-g` is evaluated over a Prize-state distribution conditioned on legal setup.

## Validation

The implementation uses no Monte Carlo sampling for the reported values.

`results/prize_rescue_start_condition/reproduce.py` validates the model in three ways:

1. for several small decks with mixtures of starter/non-starter critical and rescue cards, it exhaustively enumerates every accepted opening-hand subset and every disjoint Prize subset, then compares collapse and critical-Prize probabilities to the exact formula;
2. it verifies that the complete conditioned Prize-state probability mass sums to one;
3. it independently recomputes the previous uniform Prize-rescue baseline and prints the conditioned result beside it.

The exact and exhaustive results match to floating-point precision in the preserved regression cases.

## Limitations

The model still addresses only initial Prize topology and opening validity. It does not model draw/search access to Gladion, one-Supporter-per-turn contention, Supporter lock, ordinary Prize-taking, Peonia or other alternative recovery, matchup-dependent criticality, turn timing, or whether a nominal setup starter is desirable to start with.

The `starter_cards` count must reflect the actual setup condition. For an ordinary deck it is the number of Basic Pokémon that may legally be placed during setup. Card-text exceptions should be included or excluded as appropriate. Conditional starters such as Manectric with Electric Start mean the count can depend on who goes first.

The categories assume cards within each of the six classes are exchangeable for this setup question. A richer simulator can preserve exact card identities while using the same conditional probability logic.

## Practical modeling recommendation

For exact setup simulation, sample or enumerate the opening hand and Prize cards from one shared deck order, applying the legal setup condition before accepting the state. If using closed-form abstractions instead, condition Prize-state probabilities on the opening acceptance event rather than multiplying an opening model by an independent uniform Prize model.

This is especially worth doing for low-starter control or combo decks, where the post-mulligan Prize prior differs most from 10%.

## Next useful work

The strongest continuation is to combine this valid-start-conditioned Prize topology with timed access to rescue cards. That model should track whether Gladion is searchable/drawable by the turn a critical Prize is needed, Supporter contention, lock effects, and ordinary Prize-taking. A second useful extension is to model going-first/going-second-dependent setup exceptions directly rather than requiring the caller to provide the appropriate starter count.
