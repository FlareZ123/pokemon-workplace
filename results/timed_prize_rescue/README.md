# Timed Prize rescue: exact access and Supporter-contention baseline

## Question

The existing Prize-rescue results answer whether enough Gladion-like rescuers exist outside the initial Prize cards. That is a topology ceiling. This result asks a stricter question: **by a stated deadline, after conditioning on a valid opening hand, are enough rescuers actually accessible and are there enough Supporter play opportunities to use them?**

Implementation: `tools/timed_prize_rescue.py`  
Reproducer and exhaustive checks: `results/timed_prize_rescue/reproduce.py`

## Why this matters

`results/prize_rescue_collapse/` showed that a rescue package can collapse when several critical cards and/or rescuers are Prized together. `results/prize_rescue_start_condition/` then showed that legal setup changes the Prize prior slightly. Both deliberately assumed that every rescue copy outside the Prize cards could eventually be reached and played.

That assumption is optimistic for an early deadline. A rescue line can exist in the deck while still having low Active Move Realism because the relevant Supporter has not been drawn, because only one Supporter can normally be played per turn, or because another Supporter is needed instead. The human-concepts document calls out both AMR and Supporter contention as failure modes for access-only reasoning.

The local advanced manual supplies the mechanical constraints used here: an accepted setup must establish a legal starting Pokémon before Prize cards are set, and a player may normally use only one Supporter during a turn.

## Exact model

The deck is partitioned into six categories:

1. critical setup-eligible starters;
2. critical non-starters;
3. rescue setup-eligible starters;
4. rescue non-starters;
5. filler setup-eligible starters;
6. filler non-starters.

The model proceeds in the real setup order.

1. Draw an opening hand and condition on it containing at least one setup-eligible starter.
2. Draw the initial Prize cards from the remaining deck.
3. Observe a specified number of later **random draws** from the post-Prize deck.
4. Count rescue cards in the accepted opening hand plus those later draws.
5. Compare that accessible-rescuer count and a separately specified number of Supporter opportunities with the number of critical cards in the initial Prize cards.

For opening category counts `h_i` and category sizes `n_i`, an accepted opening state has mass

`[prod_i C(n_i, h_i) / C(N,H)] / A`,

where

`A = 1 - C(N-S,H) / C(N,H)`

is the probability that a random opening hand contains at least one of the `S` setup-eligible starters.

Given that hand, a Prize state `p_i` has the ordinary multivariate-hypergeometric conditional mass

`prod_i C(n_i-h_i, p_i) / C(N-H,P)`.

After the opening hand and Prize cards are fixed, the number of additional rescue cards found in `D` random draws is hypergeometric. If `r_hand` rescuers are already in the opening hand and `c_prized` critical cards are Prized, the draw layer fails whenever it finds fewer than

`c_prized - r_hand`

additional rescuers. Separately, if `c_prized` exceeds the number of Supporter play opportunities before the deadline, the line fails regardless of card access.

The reported failure event requires at least one modeled critical card to be Prized. Games with no critical Prize are therefore not counted as rescue failures.

## Finding 1: topology can dramatically overstate timely access

Use a 60-card deck with six Prize cards, a seven-card accepted opening, 12 setup-eligible starters, four modeled non-starter critical singletons, and two non-starter Gladion-like rescuers. Give the player two Supporter opportunities by the deadline.

| Additional random draws before deadline | Unconditional timed failure | Failure given any critical is Prized |
| ---: | ---: | ---: |
| 0 | 28.832691% | 81.487163% |
| 1 | 27.889794% | 78.822343% |
| 2 | 26.962200% | 76.200768% |
| 5 | 24.271226% | 68.595518% |
| 10 | 20.092303% | 56.785016% |
| 20 | 12.882083% | 36.407439% |
| 47, every post-Prize card | 1.057675% | 2.989209% |

The final row deliberately gives perfect eventual access to every non-Prized rescuer. It reproduces the valid-start topology result from `results/prize_rescue_start_condition/`: 2.989209% conditional collapse for four non-starter criticals and two non-starter rescuers.

The earlier rows expose a different failure mode. If the only access is the opening hand plus random draws, most rescue-required states do not have enough rescuers available quickly. With no later draw, the conditional failure is 81.49%; even after ten random draws it is 56.79%.

This is **not** an estimate of a real Gladion deck's failure rate. Real decks may have targeted search, draw Supporters, Abilities, Prize-taking, or alternative recovery. The result is a baseline showing how much information is lost when a model treats “rescue copy exists outside the Prizes” as equivalent to “rescue copy is usable by the deadline.”

## Finding 2: Supporter contention is independently binding

Now use four non-starter rescuers and assume every non-Prized rescuer is eventually seen. This removes ordinary card-access scarcity and isolates the one-Supporter-per-turn channel.

| Supporter opportunities before deadline | Unconditional failure | Failure given any critical is Prized |
| ---: | ---: | ---: |
| 1 | 4.695508% | 13.270479% |
| 2 | 0.232787% | 0.657904% |
| 3 | 0.008830% | 0.024955% |
| 4 | 0.006101% | 0.017244% |

Even with four rescuers and guaranteed eventual access to every non-Prized copy, a one-opportunity deadline fails in 13.27% of the states where at least one critical card is Prized. Those are mostly states requiring more than one rescue before the deadline.

The remaining 0.017244% conditional failure with four opportunities is the pure initial topology floor under this setup-conditioned model: too many required resources and rescuers are trapped in the Prize cards together.

## Interpretation

### Computational result

The exact calculations establish three distinct layers of rescue reliability:

- **Prize topology:** enough rescue copies exist outside the Prize cards.
- **Timed card access:** enough of those copies have actually reached the hand by the deadline.
- **Action bandwidth:** enough Supporter opportunities exist to play them by the deadline.

A graph or deck model that collapses these layers into one “Gladion can access a Prize card” edge can be highly optimistic.

### Strategic judgment

The gap between the topology floor and the no-search timed baseline suggests that future deck-level models should value search engines according to when they make rescue cards available, rather than simply whether they connect to them. This connects Prize modeling directly to AMR and connector domination: a search route to Gladion consumes whatever connector found it, and that connector may have a stronger competing use on the same turn.

## Validation

The implementation is exact; no Monte Carlo sampling is used for the reported values.

`results/timed_prize_rescue/reproduce.py` performs two checks:

1. a small `N=10` case is exhaustively enumerated over every accepted opening-hand subset, disjoint Prize subset, and disjoint future-draw subset; exact failure and any-critical-Prized probabilities match to floating-point precision;
2. giving the 60-card baseline all 47 post-Prize cards as draws and effectively unlimited Supporter opportunities reproduces the existing setup-conditioned topology failure probability `0.010576751696984328`.

The exact state mass is also asserted to sum to one.

## Limitations

This model intentionally does not include targeted search, non-random draw effects, ordinary Prize-taking, alternative Prize recovery, rescue cards becoming accessible after being shuffled into the Prize cards, Supporter lock, Item lock, connector costs, discard gates, matchup-specific criticality, or competing uses of the Supporter for the turn.

`extra_random_draws` means literal sampling without replacement from the post-Prize deck. It should not be used as a proxy for targeted search. A future search model should represent the relevant connector explicitly.

`supporter_opportunities` is passed directly instead of inferring it from a turn number. This keeps the tool valid across going-first/going-second timing, skipped or blocked Supporter turns, and arbitrary research horizons.

The model also treats every modeled critical card as requiring rescue before ordinary Prize-taking can solve the problem. That is appropriate for setup-critical stress tests and can be pessimistic for late-game tactical cards.

## Next useful work

The next high-value extension is a deck-level connector model for rescue access. It should add explicit searchable paths to Gladion-like cards, track the opportunity cost of the connector, and model Supporter contention with the deck's ordinary setup Supporters. A useful first target is an exact or small-state turn model where a connector can either find the rescue Supporter or spend the same search resource on an attacker, Energy engine, or lock piece.
