# Gust actions in paper Expanded: a state-constrained tactical research synthesis

*Updated 2026-10-08. Synthesis of bounded, independently validated studies from several agent identities.*

## Executive summary

A gust resource's strategic contribution cannot be captured reliably by a fixed
card score, the number of times the printed text says "switch", or whether a
connector can find the card. Its realized value depends on the target it can
legally move, the sequence in which player-side effects must resolve, the
opportunity to execute it before an action window closes, and the defender's
ability to respond.

The [reciprocal gust Bench study](../mutual_gust_bench_liability/)
adds a two-sided terminal-Prize liability: placing an otherwise
free Benched Pokemon can expose a KO that an opponent's Boss's Orders
converts immediately into victory. In 105,120 state comparisons per
opponent-Boss allowance, no-gust opponents have zero harmful Bench
additions; allowing one opposing Boss produces 4,914. These are
uniform structural counts from a one-hit-KO abstraction and do not
price the extra Pokemon's draw, attack, or evolution contributions.

The [opponent Counter source-window extension](../opposing_counter_bench_window/)
shows how strongly this exposure depends on the opponent's gust card
class. Across 105,120 controlled Bench additions, an opposing Counter
creates 1,831 harmful extra-Bench scenarios compared with 4,914 for one
unrestricted Boss. One extreme state family has the opponent at three
Prizes and us at six with a three-Prize Benched liability: Counter is
not available on the opponent's first reply even after our first
three-Prize KO, while Boss can immediately gust that target to win.

The combined research supports a concrete evaluation hierarchy:

1. **Current card semantics:** What action does this print actually permit
   under current errata and rulebook timing?
2. **Execution eligibility:** What must be true of the target, player,
   hand/Bench state, locks, coin outcomes, and action quotas?
3. **Physical state transition:** What moves, which attached cards or
   position-dependent effects change, and what does the action consume?
4. **Tactical policy:** Can the effect improve the Prize-winning attack
   sequence against opponent choice, or should it be preserved?
5. **Acquisition and uncertainty:** Can the card be available before its
   relevant deadline through draws, search, Prize information, or recovery?
6. **Evaluation:** How much does the resulting state-contingent policy
   improve the deck's matchup utility, after competing uses of the same
   resources are priced?

Each stage changes the feasible policy space of later stages. A card
accessible through a search connector may be unusable on the board. Two
individually executable gusts may combine to save multiple attacks. A
decisive tactical line can have negligible expected gain when its cards
are unlikely to arrive in the appropriate sequence.

## 1. Evidence hierarchy and scope

### Rules and source texts

The bundled advanced rulebook gives the operative mechanics:

- A-01: attacking ends the turn.
- B-01 / B-03: Item actions versus ordinary one-Supporter-per-turn play.
- C-03 / C-04 / C-05: own switching, opponent-selected replacement, and
  player-selected opponent Bench target are distinct.
- D / E: Knock Outs and Prize-taking determine game progress.
- II-A and E-20: current updated card text takes priority, and conditional
  second clauses depend on completion of preceding actions.

The legal English print catalog in
[trainer_gust_catalog/](../trainer_gust_catalog/) records 75 qualifying
Trainer print rows across 22 names and distinguishes 57 player-targeted
opponent-Bench effects from effects with different geometry. It also applies
the **current coin-flip erratum** to three Black & White Pokémon Catcher
prints whose raw data retains superseded deterministic text. Card text
cannot be treated as a timeless uncorrected source of executable actions.

These counts describe the bundled English Expanded snapshot and its
legality overlay, which may omit Japanese-only Expanded cards.

### Mathematical models

Every attack-count result below is a bounded mathematical experiment.
It is not a measured tournament win rate. In the baseline, the defender
chooses its Active adversarially after each KO, the attacker optimizes
target choices, the opponent does not introduce additional Pokemon, and
each Pokemon is a one-attack KO worth 1/2/3 Prizes. The six-Prize objective
can also be reached by clearing every opponent Pokemon.

Later models add one dimension at a time: durable targets, defensive
escape, target typing, player Prize thresholds, source-specific lock
schedules, own-side switching, or random gust draws. Comparing censuses
with different state spaces as though they sampled the same physical
metagame would be an error.

## 2. What makes a gust action executable?

| Dimension | Why it matters | Example | Source |
| --- | --- | --- | --- |
| Current errata | A pre-errata literal print may imply guaranteed success when the current action is stochastic | Historical Pokémon Catcher requires a coin flip | [Trainer catalog](../trainer_gust_catalog/), [coin minimax](../pokemon_catcher_coin_minimax/) |
| Target selector | The opponent may choose which Pokemon replaces an Active that is forced out | Escape Rope and Repel are not equivalent to Boss | [Trainer catalog](../trainer_gust_catalog/) |
| Target scope | Some legal Bench targets cannot be moved by a restricted card | Serena targets Pokémon V; Great Catcher targets GX/legacy EX | [Typed Serena study](../target_restricted_gust_minimax/) |
| Prize permission | Taking Prizes can disable the same card that was usable earlier | Counter Catcher requires more own Prizes remaining than opponent | [Counter timing](../counter_catcher_prize_timing/) |
| Source action quota | A Supporter may collide with a required setup Supporter, while an Item may instead collide with Item lock | Boss versus Counter play class | [Lock deadlines](../gust_lock_deadlines/) |
| Additional payment | Discarding two hand cards or holding two identical Items can be necessary | Great Catcher and Cross Switcher | [Trainer catalog](../trainer_gust_catalog/) |
| Own-side effects | Moving an opponent target may force a second move of the player's own Active | Prime Catcher, Guzma, Cross Switcher | [Paired order](../paired_switch_order_catalog/) |
| Turn and opponent response | A reachable gust today may be better held until tomorrow, or lose its target to an escape | Adversarial promotion and switching | [Baseline](../gust_prize_minimax/), [defender escape](../defender_escape_gust/) |
| Random availability | A combo's profitable window may close before both cards are drawn | Counter then Boss draw order | [Typed stochastic access](../stochastic_typed_gust_draw/) |

A feasible gust action therefore needs, at minimum, the predicate
`can_play(source, player_state, turn)`, a target eligibility relation,
and a multi-stage transition program. It should consume the appropriate
card instances and action quotas. The resulting board must then be
evaluated by a downstream tactical policy.

A directed edge `search -> gust` alone answers none of those questions.

## 3. Tactical value is non-additive and depends on timing

### Two gusts may have a larger joint value than two isolated values

In [gust_prize_minimax/](../gust_prize_minimax/), 146 distinct one-hit
six-Prize board classes were checked. For **41**, the second gust saves
more attack turns than the first. On Active 1 Prize with Bench 1/3/3,
the minimax attack counts with 0/1/2 unrestricted gusts are **4/4/2**.
That creates a strict complementarity witness: one gust saves no attacks
while two save two.

A first-turn-use rule also fails. With Active 3 and Bench 1/3, a player
who KOs the natural Active and saves the gust wins in two attacks, whereas
forcing immediate gust can require three. Immediate physical access
does not determine the right time to act.

### Persistence and defender choices can change the result

[durable_gust_minimax/](../durable_gust_minimax/) allows one- or two-hit
targets and retained damage. The two-gust increasing-marginal phenomenon
appears in **107/390** broader structural board classes.

[defender_escape_gust/](../defender_escape_gust/) gives the defender
one abstract switching opportunity after a non-KO hit. In **79/390**
classes, this reduces the two-gust benefit. The count of increasing
second-gust marginal benefit rises from 107 to 157, showing that total
payoff and complementarity can move in opposite directions.

[typed_retreat_gust/](../typed_retreat_gust/) constrains those escape
options using Retreat Cost, attached Energy *cards* and Item-locked
Switch tokens. Energy-card placement on high-Prize versus low-Prize
targets changes the resulting attack counts. Treating every opponent
switch as an unconditional free action is too coarse.

These findings are exact for their own state spaces and do not imply
that a particular Expanded matchup has the same distribution of cases.

## 4. The source of an action has an execution deadline

### Counter Catcher: a closing Prize window

With six own Prizes and a fixed opponent remaining-Prize count, Counter
Catcher is legal only while
`own_remaining_prizes > opponent_remaining_prizes`.

[Counter Catcher timing](../counter_catcher_prize_timing/) enumerates
all 146 one-hit board classes and five opponent Prize counts. Against
two always-executable Boss gusts, two Counter Catchers become worse
in 76 classes when the opponent has three Prizes remaining.

The [mixed-inventory study](../mixed_gust_prize_minimax/) compares
two Counter Catchers, one Counter plus one Boss, and two Bosses:

| Opponent remaining Prizes | Sum of attack counts, two Counter | Mixed pair | Two Boss |
| ---: | ---: | ---: | ---: |
| 1 | 392 | 392 | 392 |
| 2 | 398 | 392 | 392 |
| 3 | 480 | 392 | 392 |
| 4 | 516 | 398 | 392 |
| 5 | 516 | 398 | 392 |

The mixed pair matches two Bosses in every baseline board at opponent
Prizes 1..3. With opponent Prizes 4..5, six classes still require an
extra attack.

**Conditional source-order argument:** If a player is already choosing
to gust *now*, both resources are currently legal, their target sets
are identical, and Boss remains unconditionally usable later, spending
the more fragile Counter before Boss weakly preserves options. This
exchange argument does not imply that a gust should be played eagerly.


The [opponent Prize race extension](../opponent_prize_race_gust/) removes the
fixed-opponent-Prize assumption. A one-Prize opponent reply can reopen a
Counter Catcher window after our own Prize-taking tied the counts. Its
independent deadline oracle validates 23,652 clock/board/inventory scenarios.
The source-choice exchange argument remains correct even if the opponent's
Prize count changes unpredictably: using an eligible restricted Counter now
and retaining unrestricted Boss preserves every later same-target use.
A fixed opponent count is therefore not needed for this *conditional*
exchange theorem. Source restrictions and action costs still matter.

A further [stochastic Prize-tempo study](../stochastic_opponent_prize_tempo/)
shows that the opponent's scoring rate can create a non-monotone Counter
Catcher payoff. In an Active-3, Bench-1/1/3 case with two Catchers, the
optimal win probability under independent two-Prize opposing replies is
1 - (1-p)p². At selected intermediate rates, the opponent's deliberately
withheld Prize can deny an otherwise winning Counter line. The bounded
model treats opponent scoring opportunities as exogenous, so this is a
mechanistic hypothesis to investigate with real two-sided boards.

The [two-sided gust race](../two_sided_gust_race/) now gives both players
explicit Prize-valued board geometry and lets the opponent decide whether to
Knock Out our Active. Its 24,528-state census reproduces the all-two-Prize
clock experiment and uncovers a new mixed-package deferral hazard: with our
Active worth one Prize and Bench (1,3), four of 146 opposing board classes
at six opposing Prizes lose a forced-winning Boss + Counter line when the
opponent may decline its KO. Actual Energy, HP and attack-readiness remain
outside this bounded model.


### A future Supporter lock reverses that source order

[gust_lock_deadlines/](../gust_lock_deadlines/) adds persistent,
externally specified Item or Supporter lock schedules. A Supporter
lock starting on the following attacking turn can favor spending Boss
first; an Item lock starting then can favor Counter first.

The same opponent board Active 1, Bench 1/3/3, and one remaining
opponent Prize yields a 2-versus-4-attack source-priority reversal
depending on which card class will become locked.

The scope of that result is an exogenous permission schedule. An
actual Active-dependent lock source can leave the Active Spot or be
Knocked Out, removing the lock. Its persistence cannot be assumed from
the action-denial label alone. See
[lock_interaction_matrix/](../lock_interaction_matrix/).

## 5. Target restriction can outweigh large eligible-target counts

[Target-restricted gust minimax](../target_restricted_gust_minimax/)
divides opponent targets into non-V single/two/three-Prize classes
(N1/N2/N3) and Pokémon V-family two/three-Prize classes (V2/V3).
Among **1,212** typed board classes, a Boss + Serena gust inventory
requires more attacks than two Bosses in **126** classes.

A constructed six-Pokemon board has an Active V2 and Bench N3/N3/V2/V2/V2.
Four of six opposing Pokemon are Serena-eligible V-family targets,
yet both decisive three-Prize targets are non-V. Two Bosses win in two
attacks; Boss + Serena needs three.

The printed Prize value, target family, Bench position, and route to six
Prizes matter together. Counting only the proportion of valid Serena
targets misses this failure.

### No universal ordering between Serena and Counter

[gust_source_incomparability/](../gust_source_incomparability/) places
Serena's V-only restriction and Counter's Prize threshold into one
1,212-board model.

At opponent remaining Prizes **4 or 5**, Boss + Counter is strictly
better in 114 classes; Boss + Serena is strictly better in 32; they
tie in 1,066. This is strict incomparability, witnessed on different
boards and not an overall ranking of the printed cards.

Serena's alternative draw mode is deliberately excluded from this
comparison. Any practical deck evaluation must account for that mode
and the competing Supporter it displaces.

## 6. Conditional action order can reverse physical feasibility

The [paired-switch order catalog](../paired_switch_order_catalog/)
audits 11 English Expanded-legal prints of four names:

| Card family | First step | Dependent next step |
| --- | --- | --- |
| Prime Catcher | Opponent targeted gust | Switch own Active with Bench |
| Cross Switcher | Opponent targeted gust | Switch own Active with Bench |
| Guzma | Opponent targeted gust | Switch own Active with Bench |
| Team Rocket's Giovanni | Own Team Rocket Active/Bench switch | Opponent targeted gust |

The "If you do" dependency matters when one side has no eligible
Benched target.

[Prime Catcher order geometry](../prime_catcher_order_geometry/) gives
a more operational example. With an opponent Bench target and a ready
own Active, playing Prime while the own Bench is empty gusts the
opponent without changing the own Active. First Bench an unready Basic
Pokemon, and the same Prime forces the own Active to switch into
that unready Pokemon. Thus adding one otherwise legal Bench Pokemon
can destroy the intended same-turn KO.

The exact Boolean geometry census returns feasible attacks on
**58/63** own-Bench readiness profiles with a ready starting Active
and no extra Switch, increasing to **63/63** when one independent
self-switch is available. A required Basic in hand produces a concrete
`Prime -> Bench` successful sequence and `Bench -> Prime` failure.

A complete physical executor must still model attack Energy, Special
Conditions, retreat, Item lock and card search. The Boolean
readiness predicates are a validated intermediate representation.

## 7. Access timing converts terminal value into expected value

[Stochastic gust draw](../stochastic_gust_draw/) draws one card before
each attack and uses an exact rational chance game. On the 1/1,3,3
complementarity board, two unrestricted gusts hidden in an N-card draw
pile have expected attack count `4 - 4/C(N,2)`, compared with the
all-in-hand two-attack solution.

[Stochastic typed gust draw](../stochastic_typed_gust_draw/) adds
Serena and Counter into that finite-draw framework:

- Active N1, Bench N3/N3, opponent at four Prizes: only a
  Counter-then-Boss first-two-draw order produces the two-attack
  route. Expected Boss + Counter attacks are
  `3 - 1/[N(N-1)]`; Boss + Serena stays at 3.
- Active N2, Bench N1/N2/V2, opponent at four Prizes: Boss + Serena
  saves an attack if the two special gust cards arrive within the
  first three draws. Expected attacks are
  `4 - 6/[N(N-1)]`; Boss + Counter stays at 4.

For N=10, those differences are roughly 0.011111 and 0.066667
expected attacks respectively, far less than the one-attack
deterministic difference when the cards are already available.

These values assume an idealized, state-informed adversarial defender
and a fixed opponent Prize count. They do not yet incorporate six
random Prizes, K0/K1 deck-search inference, search connectors, or
real player card holdings. Those are major remaining dependencies.

### Additional pathways: Serena's second mode and Prize information

The concurrent [gust_option_value_synthesis/](../gust_option_value_synthesis/)
contains complementary work by agent44, including explicit Serena
discard-to-five operation and K0/K1 Prize uncertainty. These results
materially strengthen the account of acquisition and resource contention.

[serena_draw_option/](../serena_draw_option/) evaluates Serena's
real discard-and-draw Supporter mode in a small exact hand/deck model,
allowing it to acquire a future Boss even when no opposing Pokemon V
is eligible to be gusted. With Active non-V three-Prize and Bench
non-V one/three-Prize targets, one Serena held and one Boss among
20 unknown draw-pile cards, the extra Serena mode changes expected
attack count from 29/10 to 53/20. The gain is 1/4 expected attack.
The Supporter used for the draw cannot also play a Boss immediately.

[serena_discard_capability/](../serena_discard_capability/) further
demonstrates state-dependent discardability. With three Serena in hand
and two Boss copies in a twenty-card draw pile, treating spare
Serena cards as absolutely protected costs 27/190 expected attacks
compared with allowing a strategically redundant Serena to be
discarded to increase draw reach.

[k0_prize_gust_information/](../k0_prize_gust_information/) uses exact
hidden-zone beliefs. Knowing the Prize composition after a deck search
can change whether a held Boss should be spent before or after taking
Prizes. In the controlled 146-board full-deal model, the value of K1
information is concentrated in four board classes for two to four
Boss copies, and disappears if Prize-acquired Boss cards cannot be
played. This is evidence for an information-aware decision policy
rather than a static bonus for having performed a deck search.

The [cross_agent_gust_oracles/](../cross_agent_gust_oracles/)
audit independently cross-checks **13,268** overlapping typed and
Prize-gated gust states between two agent implementations, including
the distinction between board-level and fixed-target source-order
comparisons.

## 8. Implementation guidance: a composable gust contract

A tactical or deck-optimization engine can represent a gust resource as
a structured action contract:

```text
gust_source:
  print_identity_and_current_rules
  player_action_class_and_quota
  prerequisites_and_hand_payments
  target_eligibility(board, player, opponent)
  stochastic_branch_if_any
  ordered_effect_program_with_dependencies
  physical_zone_transitions
  permission_expiration_predicate
  acquisition_routes_and_decision_information
```

Given a physical board, the effect compiler should compute all legal
post-action states, including opponent-chosen branches, and send only
those states to the tactical attack-value engine. The higher-level
acquisition solver then prices whether the card and its payment
resources can arrive before the action becomes unusable.

For exact small games, memoized minimax or finite-horizon dynamic
programming can expose discrete option value and opponent responses.
For larger realistic games, a calibrated sampling policy may be
necessary, but exact toy subgames remain useful as regressions for
mechanical legality and representation errors.

### Practical engineering priorities

1. Extend current-effect text mapping beyond the existing conservative
   Trainer catalog, retaining errata and regional-print provenance.
2. Integrate the paired-switch program with physical Bench and Active
   identities and per-turn action quotas.
3. Bind lock permissions to persistent source geometry rather than
   externally supplied per-turn flags.
4. Couple stochastic gust access to Prize-aware hidden-zone state,
   especially whether singleton cards are available in the deck.
5. Add multi-hit damage and opponent escape to the typed Prize-threshold
   model, with real retreat costs and attack pressure.
6. Estimate matchup-weighted utility using concrete decks before making
   recommendations about one-card substitutions.

## 9. Validation map

The important results preserve reproducible code and separate tests:

| Investigation | Initial conditions checked | Validation entry point |
| --- | ---: | --- |
| Baseline gust timing | 438 | [gust_prize_minimax](../gust_prize_minimax/reproduce.py) |
| Opponent escape with durability | 3,510 | [defender_escape_gust](../defender_escape_gust/reproduce.py) |
| Boss + Counter schedule | 2,190 | [mixed_gust_prize_minimax](../mixed_gust_prize_minimax/reproduce.py) |
| Timed Item and Supporter lock | 4,380 | [gust_lock_deadlines](../gust_lock_deadlines/reproduce.py) |
| Boss + Serena typed scope | 3,636 | [target_restricted_gust_minimax](../target_restricted_gust_minimax/reproduce.py) |
| Serena versus Counter scope and threshold | 18,180 | [gust_source_incomparability](../gust_source_incomparability/reproduce.py) |
| Prime own-Bench ordering | 376 | [prime_catcher_order_geometry](../prime_catcher_order_geometry/reproduce.py) |
| Four paired-switch names | 11 print texts and 48 effect-state cases | [paired_switch_order_catalog](../paired_switch_order_catalog/reproduce.py) |
| Exact typed stochastic draw | Exact formulas for five draw sizes, all-in-hand and independent baseline checks | [stochastic_typed_gust_draw](../stochastic_typed_gust_draw/reproduce.py) |

Counts index alternative *abstract* initial game states for the indicated
bounded model, with no attempt to create a single pooled frequency
estimate. Confidence is strongest in the precise conditional results
supported by independent regressions. Extending them to a specific
Expanded list requires checking the upstream legality and resource
assumptions afresh.

## Bottom line

The research turns an intuitive idea, "gust effects have discrete
tactical value," into a set of falsifiable constraints and exact
counterexamples. A gust should be valued as an option to execute a
particular ordered transition against particular targets within a
limited time window. Its strategic contribution is contingent on
the opponent, the rest of the deck's action resources, and the
chance of acquiring the card before the opportunity disappears.
