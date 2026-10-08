# Gust option value in paper Expanded: a validated multiscale research map

**Research scope:** paper Pokémon TCG Expanded, Black & White onward.  
**Status:** a synthesis of thirteen exact, deliberately bounded models. Results are conditional on their own stated game-state abstractions. None of the structural board counts is a tournament-frequency estimate.

This document connects opponent-aware endgame analysis, card source restrictions, hand/deck availability, Prize information, retreat counterplay and Supporter contention into one coherent framework. Underlying evidence is kept in the named result folders and their executable regressions.

## 1. The central abstraction: actionable options over time

The tactical importance of a gust effect is determined by the set of *future attacks* it makes available before the game ends. A useful value representation is

`V(s) = min_{legal attacker action a} max_{legal defender reply d} E[1 + V(s') | s, a, d]`,

where a transition taking the final Prizes or removing the last opposing Pokémon has value one attack. This formalism permits uncertainty in card draws and adversarial promotion without asserting that every TCG mechanic is already represented.

For a usable gust action, four distinct questions must be answered:

1. **Semantic identity:** what does the card do under current errata, including its legal target family and attached conditions?
2. **Executability:** can its costs, timing, Supporter quota, Item-play permission, prerequisite switches and other resources be satisfied now?
3. **Availability deadline:** can the card enter hand or otherwise become usable before the attack turn where it matters?
4. **Terminal effect:** does using it now improve the Prize route after the opponent's best response, given alternatives and future opportunities?

The prior human concepts UDP, DCI, AMR, connector domination and ALS illuminate these differences. They are methodological hypotheses to test, not requirements to adopt a scalar score.

## 2. Exact tactical endgames and diminishing-return failure

[`gust_prize_minimax/`](../gust_prize_minimax/) establishes the simplest terminal payoff. The opponent has an Active and up to five Benched one-hit targets, worth one, two or three Prizes. The defender chooses the replacement Active after each KO. Over 146 geometrically distinct initial board classes where six total Prizes exist:

- A first guaranteed gust saves no attacks in 77 classes, one in 54, and two in 15.
- A second available gust's marginal value strictly exceeds that of the first in **41 classes**.
- Requiring the attacker to use an available gust on the opening attack instead of preserving the timing choice costs at least one attack in **55 classes**.

Witness: Active one Prize, Bench one/three/three Prizes. Optimal attacks with zero, one, two gusts: `(4,4,2)`. Two gusts are complementary; a one-dimensional additive per-gust score is structurally inadequate.

[`durable_gust_minimax/`](../durable_gust_minimax/) extends to one-/two-hit targets with damage retained after switching. **107 of 390** structural classes still show a strictly increasing second marginal. The complementarity is not an artifact of assuming all KOs are one attack.

## 3. Opponent choices and target escape

[`defender_escape_gust/`](../defender_escape_gust/) adds limited defender switches after a non-KO hit. Even a single executable switch can prevent the intended finishing attack. In 79/390 board classes, adding one defender escape reduces the total benefit of two available gusts. The number of classes with increasing second-gust marginal value actually rises from 107 to 157 because the first gust alone becomes less capable of securing a long two-hit Prize target.

[`typed_retreat_gust/`](../typed_retreat_gust/) makes that escape state-dependent: effective Retreat Cost, physical attached Energy cards, an explicit retreat prohibition, and a separately Item-lock-gated Switch alternative. On 390 normalized boards, giving one retreat-ready Energy to the high-value three-Prize targets reduces the gain from two gusts in **70 cases**. Providing the same Energy only to one-Prize targets reduces it in **6**. This is a counterplay *target-geometry* interaction that a single fixed 'opponent can retreat' flag misses.

**Interpretation:** gust is an attack sequence with an opponent between its steps. Surviving attackers can be moved away, so a theoretical two-hit Prize route cannot be scored as if the defender always leaves the damaged target Active.

## 4. Source-specific legality and target scope

[`trainer_gust_catalog/`](../trainer_gust_catalog/) audits current-semantic Trainer printed sources. Its conservative English Expanded lexical seed contains 75 source records across 22 names. Only 57 records / 16 names permit the effect user to select an *existing opposing Benched Pokémon*. The remainder involve opponent-selected promotion, moving a Pokémon from the opponent's hand, own-only switching, or non-Pokémon zones.

The catalog encodes restrictions such as:

| Source | Distinguishing requirement |
| --- | --- |
| Boss's Orders and Lysandre | Supporter, any existing opposing Benched target |
| Serena | Supporter, opposing Pokémon V target, alternate discard-and-draw mode |
| Great Catcher | Opposing Pokémon-GX/EX target, discard two cards |
| Counter Catcher | Item, player's remaining Prizes must exceed opponent's |
| Pokémon Catcher | Item, coin flip required under current errata |
| Custom Catcher / Cross Switcher | Paired card usage to obtain targeted gust |
| Toy Catcher | Target has at most 50 HP remaining |
| Prime Catcher | ACE SPEC restriction, switches own Active too |

This is a guided input taxonomy, not a complete legality engine. Real legality also depends on the exact card print, ban/reprint state, locks and action payment.

**Historical-text correction:** three old Pokémon Catcher entries (`bw2-95`, `bw5-111`, `bw10-83`) in the bundled database still show deterministic switching. Official Pokémon TCG errata (https://assets.pokemon.com/assets/cms/pdf/tcg/tcg_errata.pdf) requires a coin flip. The catalog preserves raw source text and provides normalized current text, preventing an old printed effect from being misinterpreted as a guaranteed gust.

[`typed_gust_target_minimax/`](../typed_gust_target_minimax/) compares Boss's Orders with Serena's Pokémon V-only gust over 582 synthetic V/non-V board types. Two restricted Serena gusts require extra attacks against two unrestricted Boss gusts on **208 boards**. One Serena plus one Boss differs from two Boss on **55**. On a Pokémon V target eligible to both, using Serena first while retaining Boss weakly dominates spending the broad Boss for the same target; it is strictly better in 118 source/target comparisons within this model. Serena's draw mode is considered separately below.

## 5. Chance, conditional gates and race deadlines

[`pokemon_catcher_coin_minimax/`](../pokemon_catcher_coin_minimax/) treats Pokémon Catcher's fair coin exactly, allowing a second Item attempt on tails before the attack. Two coin-flip Catchers are better in expected attacks than one guaranteed Boss gust on 41/146 structural boards, equal on 48 and worse on 57. A single Catcher has exactly half the one-guaranteed-gust attack saving in this bounded geometry, but the two-copy effect is not generally additive.

[`counter_catcher_prize_timing/`](../counter_catcher_prize_timing/) applies Counter Catcher's literal 'more Prize cards remaining' condition at each future attack. A natural three-Prize KO can **close** the Counter Catcher action window by tying remaining Prizes, even when the physical card remains in hand. With the opponent at three Prizes, two Counter Catchers require more attacks than two unconditional Boss gusts in 76/146 structural positions.

[`counter_catcher_prize_race/`](../counter_catcher_prize_race/) allows an external opposing Prize clock. An opponent taking a Prize can reopen the Catcher gate after it was closed by a high-value KO. However, a fast opponent can end the race before that window becomes useful. This model is a controlled conditional clock, not a simulation of the opponent's ability to take those Prizes.

**Principle:** card playability is an event in the evolving turn state, not a fixed card name property. The same physical card can be legal on turn one, illegal on turn two, and legal again on turn three.

## 6. Draw access, Prize replenishment and knowledge

[`stochastic_gust_draw/`](../stochastic_gust_draw/) integrates a finite random deck with optional gust decisions. On the one/one,three,three witness, two hidden gust cards among N future draws yield

`E[attacks] = 4 - 4 / C(N,2)`.

One gust already in hand, the other hidden among N future draws, yields `4 - 5/N`. These exact formulas demonstrate that a high terminal payoff can translate to small expected benefit when the draw deadline is early.

[`prize_refill_gust/`](../prize_refill_gust/) adds the actual action of taking Prize cards into hand. On the same witness, with four Boss cards in a 60-card abstract deck, the probability of an immediate two-attack double-three-Prize gust finish increases from **10.3171%** if Prize-recovered Boss cards are suppressed to **16.1067%** when the first three-Prize KO may yield a follow-up Boss. The distinction is validated with independent sequential deal enumeration.

[`k0_prize_gust_information/`](../k0_prize_gust_information/) compares K0 unknown Prize composition to K1 precise Prize-card counts inferred after inspecting the deck. With normal Prize-card recovery, K1 changes the optimal expected attack count on only four of 146 boards for each tested Boss count 2, 3, 4. Its gain per affected board is exactly `4/885`, `128/8555`, and `5008/162545`, respectively. Without usable Prize-card refills, this particular model gives zero K1 gain across the full tested census.

**Principle:** Prize knowledge matters when it changes an upcoming decision, and the information can be more useful in combination with a way to recover the hidden resource.

## 7. Supporter contention, drawing and discardability

[`serena_draw_option/`](../serena_draw_option/) implements Serena's alternative mode from actual text: discard one to three cards, then draw until the hand contains five. As a Supporter, this mode prevents playing Boss on the same turn, even if Boss is drawn. It can still supply Boss for the *next* turn. On a toy Active-three-Prize-non-V / Bench-one-and-three-Prize-non-V board, a Serena already held with one Boss among 20 deck cards improves expected finish from **2.9** to **2.65** attacks by drawing after a genuine discard. In 105/582 target geometries for this one-Boss setup, enabling Serena's draw mode improves optimum.

[`serena_discard_capability/`](../serena_discard_capability/) explicitly tests DCI-like resource protection. Keeping all extra Serena and Boss cards indiscardable can prevent access to Serena's full draw-to-five volume. With three Serena held, two Boss hidden in a 20-card draw pile, an all-non-V opponent, the expected attack count is **97/38** if spare Serena is protected, against **229/95** when it can be discarded. Across 582 toy boards, with three held Serena and two hidden Boss, this difference appears in 128 board classes.

This is precisely the kind of *conditional* card discardability described in the human prior research: a spare Supporter can become a good discard once its role as a potential gust is redundant or inapplicable. Discarding an already-useful Boss indiscriminately remains dangerous.

## 8. Validation map

Each technical result above has a Python reproducer under its result directory and a successful corresponding GitHub Actions regression. They use exact finite game trees, exact rational arithmetic or analytic combinatorics. Key independent checks include:

| Study | Primary independently cross-checked scope |
| --- | --- |
| One-hit gust minimax | 438 board/gust deadline states |
| Persistent damage | 1,170 deadline states and 117 one-hit reductions |
| Defender escape | 3,510 deadline scenarios |
| Target-specific retreat | 4,680 independent tree states plus 3,510 cross-kernel cases |
| Counter Catcher threshold | 2,190 deadline states |
| Coin-flip Pokémon Catcher | 438 rational expected-value states |
| Boss/Serena target restrictions | 5,238 deadline states |
| Opposing Prize clock | 15,768 deadline states |
| Prize-card refill | 5,110 cross-kernel cases plus separate sequential deal proof |
| K0 vs K1 | 1,460 policy comparisons plus 54 independent small-state checks |
| Serena draw option | 1,164 board comparisons plus exact reveal formulas |
| Serena discard capability | 2,328 protected/unrestricted board comparisons |

The Trainer source taxonomy separately asserts its 75 source print records and 22 name reviews. Independent validations check the models against their exact abstractions, not against tournament win-rate data.

## 9. A reusable decision procedure for later researchers

For a candidate deck swap involving Boss's Orders, Serena, Counter Catcher, Pokémon Catcher or another gust source, first normalize the legal current card text and relevant target eligibility. Then characterize **which board geometries matter** and when the attacker has to act, checking one-Supporter-per-turn contention and hand discard availability. Next model opposing promotion, whether the target survives a hit and can retreat, and the effect of each KO on both Prize races. Finally, calculate realistic access probability, including cards taken as Prizes, initial unknown Prize composition and draw or search connector opportunity costs.

Conclusions should be presented as:

- exact game-rule or card-text facts;
- deterministic tactics conditional on a specified board;
- combinatorial probabilities conditional on a specified deck/hand/draw model;
- empirical or simulation estimates with uncertainty and matchup weighting.

The current results overwhelmingly belong to the middle two categories.

## 10. What remains unresolved

The largest gap is an end-to-end model combining realistic attacker setup and survivability, the full paper Expanded card pool and ban/errata provenance, Supporter search and recovery, multi-hit damage ranges, evolving targets, Item/Ability/Supporter locks, actual opponent attacks, and a distribution of reachable board states. Different abstractions have different structural universes (146, 390 and 582 boards), so cross-study percentages must not be combined as if sampled from one population.

A practically valuable next experiment would start with a concrete tournament Expanded list and a narrow matchup, compile exact attack/retreat/draw/gust transitions from audited card IDs, and verify the first few turns with independent turn-level regression. That would create the missing bridge from informative tactical structure to credible deck construction recommendations.
