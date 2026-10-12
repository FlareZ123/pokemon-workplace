# Dual Bench-entry triggers: setup-role, Item payment, and Prize coupling

## Question

When a deck uses two singleton Basic Pokémon that must each be **played from the hand onto the Bench during its turn** to activate an Ability, what fraction of valid opening configurations lets the player access both, including their possible acquisition through separate paid search Items?

The bundled legal English print witnesses are Radiant Eternatus \`swsh12pt5-105\` with *Climactic Gate* and Lumineon V \`swsh9-40\` with *Luminous Sign*. These provide the required E-06 trigger semantics. Their actual effects, order, and strategic destinations differ; this is a controlled abstraction that checks whether the two entry actions can be supplied, not the execution or utility of their subsequent effects. For both Abilities to be used, Lumineon must be played before Radiant Eternatus uses Climactic Gate to end the turn.

Related studies:
- [Setup trigger role contention](../setup_trigger_role_contention/) already proves the unsearched physical starting-Active constraint.
- [Two-target paid search](two_target_item_notes.md) models discard/Prize costs for two *non-starting* singleton targets.
- This calculation composes the two constraints when **both singleton targets are themselves ordinary Basic starters**.

## Model

An abstract deck has \`N=60\`, opening \`H=7\`, \`P=6\` Prizes, and disjoint classes:

- \`B\` unrelated ordinary Basic starters;
- exactly one Basic hand-to-Bench trigger target A;
- exactly one Basic hand-to-Bench trigger target B;
- \`S\` ordinary one-output Pokémon-search Items;
- \`D\` designated safely discarded cards;
- neutral filler.

Each abstract Item costs two safe cards and fetches one target that is still in the deck. Each physical Item can be used at most once. A deck-search target is unavailable if Prized. All other legality gates are assumed open. An opposing player may grant \`m\` bonus draws after the valid opening and Prize placement.

The accepted-opening condition includes both trigger targets, since they are ordinary Basics. This is important: the conditioning denominator is

\`P(valid) = 1 - C(N-B-2,H)/C(N,H)\`.

For a combined observed \`s=H+m\` cards, let \`x\` be the number of unrelated Basics seen and \`a,b\` indicate whether targets A and B were seen. A naive role-blind calculation weights a combined sample by the probability that the original seven contained **any Basic**:

\`[C(s,H)-C(s-x-a-b,H)]/C(s,H)\`.

For the two trigger Abilities to remain usable without recovery, **some unrelated Basic must have been in the original seven**, to occupy Active while the target cards remain in hand:

\`[C(s,H)-C(s-x,H)]/C(s,H)\`.

This role-aware factor correctly depends on the original opening rather than whether an unrelated Basic arrives later through bonus draws. Within each combined observed sample, let \`t=2-a-b\` be the number of missing targets. The Item condition is \`S_observed >= t\`; payment requires \`D_observed >= 2t\`; and conditional on this combined sample, the probability all \`t\` missing singleton targets are in the searchable deck is

\`C(N-s-t,P)/C(N-s,P)\`.

The implementation sums these factors exactly, with multivariate-hypergeometric class-count weights. A sample with zero unrelated Basics in the original opening cannot activate both singleton entry triggers even if Items and target cards are subsequently obtained.

## Controlled sensitivity

Default benchmark: three Items, twelve designated disposable cards, two singleton Basic targets, six Prizes, seven-card ordinary Basic opening; role-blind and role-aware columns both enforce Item payments and target Prize availability.

| Other unrelated Basics B | Bonus draws m | Role-blind joint access | Role-aware joint access | Role penalty |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 12.23610619% | 0% | 12.23610619 pp |
| 0 | 8 | 52.91356937% | 0% | 52.91356937 pp |
| 1 | 0 | 8.59215232% | 0.62909180% | 7.96306052 pp |
| 1 | 8 | 41.30403234% | 7.74610132% | 33.55793102 pp |
| 3 | 8 | 32.21109473% | 14.11364915% | 18.09744558 pp |
| 5 | 0 | 4.51242763% | 1.47094349% | 3.04148414 pp |
| 5 | 8 | 28.49770088% | 16.99246950% | 11.50523139 pp |
| 11 | 0 | 3.24101537% | 1.95334251% | 1.28767286 pp |
| 11 | 8 | 24.77407830% | 20.69495135% | 4.07912695 pp |
| 19 | 8 | 23.78379044% | 22.60241555% | 1.18137489 pp |

Eight bonus draws is an intentionally high stress benchmark, conditional on those draws being granted and taken. The B=0 extreme gives a useful hard impossibility witness: a legal opener exists because A or B is an ordinary Basic, but one of those two singleton physical cards *must* become Active during setup. Without a zone-return effect, both hand-entry triggers cannot be used later, even with abundant search Items.

Adding unrelated Basic starters weakens this role trap while changing the accepted-opening denominator and the distribution of all other cards. Consequently, the percentages are **not** a deck-building recommendation to cut or add Basics solely to optimize this endpoint.

## Validation

[Reproducer](bench_trigger_item_reproduce.py) independently enumerates physical labeled opening hands, six-card Prize configurations in reduced decks, and subsequent bonus draws. Both role-blind and role-aware cases, with and without payment and Prize gates, agree with the exact grouped-count formula. The same test checks the source Expanded-legal Basic print IDs and literal E-06 card text.

Run from the repository root:

\`python results/opponent_bonus_assembly/bench_trigger_item_reproduce.py\`

The model resides at [\`tools/opponent_bonus_bench_trigger_items.py\`](../../tools/opponent_bonus_bench_trigger_items.py). The shared opponent-bonus validation workflow includes the reproducer.

## Limits and next work

This is a **first-window acquisition model**, not an attack, win-rate or full-turn simulator. It optimistically allows holding both trigger targets through setup, assumes enough free Bench slots to play both, assumes Items and Abilities are unblocked, and ignores Item payment opportunity cost beyond the designated fodder count. It excludes exact deck-search targeting of additional downstream payloads, Supporter budgets, movement/recovery of starting Active, opponent interference, evolving and turn-ending interactions. A real Radiant Eternatus/Lumineon sequence additionally requires correct order and legal targets for their distinct Abilities.

Next, extend the role model from two singleton Basics to multiple physical copies and actual published-deck search routes, with finite Bench-slot reservation and downstream payload targets. That would permit meaningful turn-one engine consistency comparisons without silently counting setup-consumed entry triggers.
