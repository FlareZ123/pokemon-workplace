# Optional setup cards make mulligan policy part of the Prize prior

## Question

When a deck contains cards such as Luxray with **Explosiveness**, Talonflame with **Gale Wings**, or Snorlax Doll, should an exact setup model treat them the same way as ordinary Basic Pokémon when conditioning the opening hand and initial Prize cards?

## Answer

Only if the player commits to keeping every otherwise-Basic-less hand that contains one of those optional setup cards.

The ordinary setup rule forces a player to keep a hand that contains a legally placeable Basic Pokémon. The relevant exception cards use **"you may"** wording. They can rescue an otherwise invalid opening, but they do not force the player to do so. The official Trainers Website Q&A for Luxray explicitly confirms that a player with no Basic Pokémon and an Explosiveness Luxray may decline to put Luxray Active and take a mulligan instead.

This means a setup model needs at least two card classes:

1. **forced starters**: legally placeable Basic Pokémon whose presence removes the mulligan option;
2. **optional setup starters**: cards that can be used to accept an otherwise Basic-less opening but may be declined.

A third class is ordinary non-starters. One Basic Pokémon in the current Expanded card pool, Shedinja with **Shell Survival**, is a negative exception and must not be counted as a forced starter.

Implementation:

- `tools/setup_eligibility.py` catalogs the setup exceptions from the bundled Expanded card pool;
- `tools/setup_mulligan_policy.py` computes exact opening acceptance, the geometric mulligan distribution, expected mulligans, and accepted-opening-conditioned Prize distributions under an optional-starter keep policy;
- `results/setup_mulligan_policy/reproduce.py` reproduces the findings and exhaustively validates small-deck cases.

## Rules and card-text basis

The bundled Advanced Player's Rulebook setup sequence says players draw 7 cards, determine whether they have a Basic Pokémon to start with, reshuffle and retry when they do not, and set the six Prize cards only after the opening setup is accepted. The same rulebook says effects using **"you may"** are optional. Card text takes priority when it contradicts a basic rule.

The official Luxray Q&A is especially important because it resolves the policy question directly:

- if a starting hand has no Basic Pokémon but does contain Explosiveness Luxray, the player may use Luxray as the Active Pokémon;
- the player may instead decline and mulligan.

Official ruling search:

- https://asia.pokemon-card.com/my/rules/search/?keyword=Luxray

The bundled card database supplies the exact Expanded card texts used by the catalog.

## Complete setup-exception catalog in the bundled snapshot

The legal Expanded snapshot contains **14,836** effectively legal prints. Of those, **7,259** are Basic Pokémon prints by subtype. Exactly one of those Basic prints is forbidden from normal setup, leaving **7,258** forced-Basic prints.

The setup-text scan found the following exceptions that directly alter whether a card can be placed during setup:

| Card | Print ID(s) | Setup status | Turn-order condition | May also be Benched during setup? |
| --- | --- | --- | --- | --- |
| Cinderace, Explosiveness | `me1-28` | optional Active | none | no |
| Luxray, Explosiveness | `swsh12pt5-44` | optional Active | none | no |
| Manectric, Electric Start | `sm7-52`, `smp-SM130` | optional Active | only if going second | yes |
| Snorlax Doll | `sv4-175` | optional Active | none | yes |
| Talonflame, Gale Wings | `xy11-96` | optional Active | none | no |
| Shedinja, Shell Survival | `swsh4-66` | forbidden Basic | none | no |

Three Salvatore prints also contain the phrase "setting up to play", but only because Salvatore can evolve a Pokémon that was put down during setup. They do not change opening eligibility. `setup_text_audit` retains these hits so the scanner's exclusions remain auditable.

This catalog is exhaustive for the bundled snapshot under a broad text scan for setup wording and face-down Active placement.

## Exact policy model

Let:

- `N` be deck size;
- `H` be opening-hand size;
- `F` be forced starters;
- `O` be optional setup starters;
- `q` be the probability of keeping a hand with no forced starter but at least one optional starter.

`q = 0` models always declining optional-only openings. `q = 1` models always accepting them. Intermediate values provide a reduced randomized-policy sensitivity model.

The probability that one opening attempt contains a forced starter is

`1 - C(N-F, H) / C(N, H)`.

The probability it has no forced starter but has at least one optional starter is

`[C(N-F, H) - C(N-F-O, H)] / C(N, H)`.

Therefore the per-attempt acceptance probability is

`A = P(forced present) + q * P(optional-only available)`.

Repeated mulligans are geometric, so the expected number of failed hands before acceptance is

`(1-A)/A`.

For a complete Prize state containing `f` forced starters and `o` optional starters, the ordinary multivariate-hypergeometric Prize mass is reweighted by the acceptance probability of the remaining `N-P` cards. This is the same Bayes-conditioning structure used by the earlier starter-conditioned Prize model, with the acceptance event now policy-aware.

## Finding 1: the previous single starter-count abstraction is a boundary policy

When `q = 1`, forced and optional setup cards become symmetric for the accepted-opening event. The condition is simply "the hand contains at least one of the `F+O` cards". This is exactly the abstraction used by treating every setup-eligible card as a starter.

When `q = 0`, optional setup cards are symmetric with ordinary non-starters for opening acceptance. Only forced Basics condition the accepted hand.

For any `0 < q < 1`, there are three distinct Prize-prior classes: forced, optional, and other.

Therefore a model that accepts only one integer `starter_cards` silently fixes a mulligan policy whenever optional setup cards are present.

## Finding 2: policy can materially change K0 Prize priors

Consider a 60-card deck with four forced Basic starters and four optional setup cards.

| Optional-only keep probability `q` | Opening accepted per attempt | Expected failed mulligans | Specific forced card Prized | Specific optional card Prized | Specific other card Prized |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.00 | 39.949963% | 1.503131 | 8.014732% | 10.141805% | 10.141805% |
| 0.25 | 46.302311% | 1.159719 | 8.468295% | 9.844735% | 10.129767% |
| 0.50 | 52.654660% | 0.899167 | 8.812421% | 9.619343% | 10.120634% |
| 0.75 | 59.007008% | 0.694714 | 9.082453% | 9.442480% | 10.113467% |
| 1.00 | 65.359357% | 0.530003 | 9.299996% | 9.299996% | 10.107693% |

The optional card's Prize probability shifts by about **0.842 percentage points** between the two deterministic policies. The forced Basic moves in the opposite direction by about **1.285 percentage points**.

This is a policy effect, not a card-draw approximation. The numbers are exact under the stated composition model.

## Finding 3: the effect becomes extreme in low-Basic decks

A stress case with one forced Basic and four optional setup cards is strategically unusual but legal in principle when the Basic satisfies the deck-building requirement.

If the player always declines optional-only hands (`q=0`):

- opening acceptance per attempt is **11.666667%**;
- expected failed mulligans are **7.571429**;
- the sole forced Basic has **0%** probability of being Prized, because every accepted opening must contain it;
- a specific optional setup card has **10.169492%** Prize probability.

If the player always accepts optional-only hands (`q=1`):

- opening acceptance rises to **47.456217%**;
- expected failed mulligans fall to **1.107205**;
- forced and optional starter cards become symmetric at **8.537653%** Prize probability each.

This demonstrates that K0 Prize priors in optional-starter decks can depend strongly on a strategic setup decision. They are not determined by deck composition alone.

## Finding 4: turn order can change the prior for Manectric

Manectric's **Electric Start** only works if its player goes second.

For a deck with four ordinary forced Basics and four Manectric copies:

- going first, Manectric is not an available optional starter, so each Manectric behaves like an ordinary non-starter for opening conditioning and has **10.141805%** Prize probability;
- going second and always accepting Manectric-only hands makes the eight cards symmetric setup starters, reducing each Manectric's Prize probability to **9.299996%**.

If the player goes second but deliberately mulligans every Manectric-only hand, the prior stays at the going-first value.

Thus turn order and setup policy can both be K0 state variables before the first deck search.

## Finding 5: optional starters create a real mulligan-resource tradeoff

Accepting an optional-only hand does more than choose an Active Pokémon. It also ends the player's mulligan sequence.

In the four-forced, four-optional example, always declining optional-only hands produces **1.503** expected failed openings. Always accepting them produces **0.530**. Under the ordinary setup procedure, an opponent who did not mulligan can choose to draw up to the number of the player's mulligans after Prize cards are set.

A setup decision can therefore trade board quality against information and extra cards granted to the opponent. Any future policy optimizer should value the opening board and the mulligan externality together.

## Finding 6: the mulligan tail can be strategically large

Under a fixed policy, repeated opening attempts are independent after each reshuffle and the accepted-hand probability is `A`. The number `M` of failed openings before acceptance is geometric:

`P(M = k) = (1-A)^k A`,

so the exact tail is

`P(M >= k) = (1-A)^k`.

If the opponent did not mulligan and chooses the maximum permitted bonus draw, `P(M >= k)` is also the probability that the player gives the opponent the option to draw at least `k` extra cards.

| Forced Basics | Optional setup cards | Policy | At least 1 mulligan | At least 3 | At least 5 | At least 10 |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 4 | 4 | always decline optional-only | 60.050037% | 21.654085% | 7.808478% | 0.609723% |
| 4 | 4 | always accept optional-only | 34.640643% | 4.156788% | 0.498804% | 0.002488% |
| 1 | 4 | always decline optional-only | 88.333333% | 68.924537% | 53.780285% | 28.923190% |
| 1 | 4 | always accept optional-only | 52.543783% | 14.506546% | 4.005038% | 0.160403% |

The low-Basic stress case makes the externality unusually visible. A policy that chases the sole forced Basic gives the opponent a **53.78%** chance to have at least five optional bonus draws available. Accepting optional-only hands reduces that tail to **4.01%**.

This strengthens the case for treating the setup decision as a strategic action. The keep/mulligan policy affects the opening board, Prize priors, and the opponent's possible starting hand size simultaneously.

## Finding 7: optional-starter identity can split the Prize prior again

The scalar `q` model treats all optional setup cards as one class. A player may prefer some optional starters over others. `tools/setup_multiclass_policy.py` generalizes the exact conditioning calculation to any number of optional groups and accepts a policy over the count of each group in a Basic-less hand.

Consider a 60-card deck with four forced Basics, two Manectric, and two Snorlax Doll while going second. Compare three deterministic policies:

| Policy | Opening accepted | Expected failed mulligans | Forced Basic Prized | Manectric Prized | Snorlax Doll Prized | Other card Prized |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| decline every optional-only hand | 39.949963% | 1.503131 | 8.014732% | 10.141805% | 10.141805% | 10.141805% |
| keep optional-only iff Snorlax Doll is present | 54.143608% | 0.846940 | 8.881400% | 10.124289% | 8.881400% | 10.124289% |
| keep every optional-only hand | 65.359357% | 0.530003 | 9.299996% | 9.299996% | 9.299996% | 10.107693% |

Under the selective policy, Snorlax Doll has the same accepted-opening Prize prior as a forced Basic, **8.881400%**, because either one can terminate the mulligan sequence. Manectric remains aligned with ordinary cards at **10.124289%** because Manectric-only hands are still rejected.

The model also supports nonlinear policies. If the player accepts an optional-only hand only when at least two optional cards are present, the same 4+2+2 deck accepts **44.273748%** of attempts. Each optional card is Prized with probability **9.685492%**, between the forced-Basic prior of **8.337599%** and ordinary-card prior of **10.152070%**.

This shows that `q` is a useful sensitivity parameter and still loses information when the setup choice depends on card identity or hand composition. Exact K0 priors can require the actual keep rule.

`results/setup_mulligan_policy/reproduce_multiclass.py` checks the generalized formula against exhaustive labeled-hand and Prize enumeration for deterministic, nonlinear, and fractional policies.

## Finding 8: under a stationary keep policy, the realized mulligan count does not further change the final Prize prior

The policy changes the accepted-opening Prize distribution, and the number of failed attempts can be large. Once the policy is fixed across attempts, the realized count of earlier mulligans supplies no additional information about the final accepted deck order.

Let each full shuffle produce an independent random deck order `X_i`, and let `A(X_i)` be the event that the policy accepts that opening. If exactly `m` attempts fail before acceptance, the final state comes from `X_{m+1}` conditioned on `A(X_{m+1})`. The preceding rejected orders are independent of `X_{m+1}`. For any final Prize state `S`:

`P(S=s | M=m) = P(S=s | A)`.

This means a player who knows they mulliganed five times should use the same final Prize prior as a player who mulliganed zero times, provided both use the same stationary keep rule and the deck is fully randomized after each rejection.

Two important qualifications remain. The revealed contents of mulligan hands can disclose archetype information to the opponent even though those prior hands do not alter the final Prize distribution. A player who changes their keep rule after repeated mulligans also breaks the stationary-policy assumption, in which case the realized mulligan count can become informative about the final accepted state.

## Validation

The reported probabilities require no Monte Carlo sampling.

`reproduce.py` validates the exact conditioned Prize distribution against exhaustive enumeration of every labeled opening-hand subset and every disjoint Prize subset in several small decks. It includes both deterministic boundary policies and fractional `q` sensitivity cases. Exact and exhaustive state masses match to floating-point precision.

A second invariant checks that when `q=1`, a forced card and an optional card have identical Prize probability because the acceptance condition depends only on their combined count.

## Correction to earlier repository guidance

`results/prize_rescue_start_condition/` correctly identified that mulligan conditioning changes Prize priors, and its mathematics is exact for the acceptance event it models. Its broad wording treated every "setup-eligible starter" as if its presence necessarily defined a valid accepted opening.

That interpretation is too strong for cards with optional setup text. The old model remains valid in either of these cases:

- all counted starter cards are forced starters under the ordinary Basic rule;
- optional setup cards are included only under a policy that always accepts an optional-only opening.

For decks containing optional setup cards under any other policy, use the policy-aware model here.

## Limitations

The scalar `q` model only conditions on whether an optional setup card exists in a Basic-less hand. A skilled player can condition the decision on the entire seven-card hand, matchup information revealed by an opponent's mulligan, turn order, the identity of the optional starter, and the cost of giving the opponent extra mulligan draws.

Different optional starters are also not interchangeable strategically. Starting Talonflame, Luxray, Cinderace, Manectric, or Snorlax Doll creates different boards and future lines.

The card-text scanner is tied to the bundled snapshot. Future releases can add new setup wording and should be audited. The `setup_text_audit` output is intended to make that maintenance easy.

## Next useful work

The strongest extension is a hand-state policy model. Instead of one scalar `q`, it should evaluate the exact optional-only opening hand and choose between keeping and mulliganing based on downstream board value, the opponent's mulligan bonus, matchup information, and the optional starter's ALS value. That would turn the policy sensitivity shown here into an actual setup decision rule.
