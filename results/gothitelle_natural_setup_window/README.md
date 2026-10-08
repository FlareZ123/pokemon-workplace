# Turn-two Gothitelle through Rare Candy: exact natural-draw readiness

## Objective and evidence

The preceding [Teleport Room access studies](../teleport_same_pool_policy/)
assume an established Gothitelle. This analysis calculates the chance of
naturally seeing the correct setup components by the player's second turn,
subject to the timing of Rare Candy and a legal opening hand.

- Implementation: [`tools/gothitelle_natural_setup_window.py`](../../tools/gothitelle_natural_setup_window.py)
- Independent SFT: [`reproduce.py`](reproduce.py)
- [Passing GitHub Actions run 37773831995](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37773831995)

The bundled legally playable prints are Gothita `xy3-39` (Basic),
Gothitelle `xy3-41` (Stage 2, Teleport Room), and Rare Candy `sv1-191`.
Rare Candy evolves an established Basic directly into its Stage 2 but cannot
be used during the player's first turn or on a Basic just put into play.

## Exact model

1. Sample seven opening cards from a 60-card deck. The opening attempt is
   legal if at least one Gothita or other Basic Pokémon appears.
2. Set six random Prize cards from the remainder.
3. Draw one card on turn one. Gothita must be available in the opening or
   this first draw so it can enter play before the second turn.
4. Draw one more card on turn two. A Gothitelle and Rare Candy must both
   occur among the opening seven plus these two draws.

The physical availability of all three pieces at the correct time is
measured. The model assumes that Gothita remains in play and that no
Item/Ability locks or opponent interference prevent evolution. It includes
no extra draw, search, opponent-mulligan bonus cards, or Supporter effects.
A Bench Gothitelle can use Teleport Room because the Ability has no
Active-only condition.

For exact probability, the opening category counts are evaluated by
multivariate hypergeometric sampling; the subsequent two ordered draws
are evaluated from the remaining category counts. All arithmetic uses
integer combinations and reduced fractions.

### Results

| Counts: Gothita / Gothitelle / Candy / other Basics | Success per seven-card attempt | Success given legal opener |
| --- | ---: | ---: |
| 2 / 2 / 2 / 8 | 1.417374% | 1.911828% |
| **3 / 2 / 4 / 8** | **3.650225%** | **4.694346%** |
| 4 / 3 / 4 / 8 | 6.602236% | 8.157422% |
| 4 / 4 / 4 / 8 | 8.329321% | 10.291329% |
| 3 / 2 / 4 / 0 | 3.395959% | 10.766141% |

The highlighted illustrative list has 43 other cards beyond its three
Gothita, two Gothitelle, four Candy, and eight other Basics. In the same
configuration, the probability that a random opening is legal is
77.757886%. Its natural-turn-two readiness probability among accepted
seven-card openers is 4.694346%.

With zero other Basics, only 31.542957% of random opening attempts are
legal; conditional on an accepted opener, almost any accepted hand
already contains Gothita, explaining the much larger 10.766141% rate.
This illustrates how mulligan conditioning alters apparent consistency.

### Random Prize marginalization

Because Prize cards are drawn randomly and no deck search or Prize
inspection intervenes, the *unconditional* two subsequent natural draws
have the same distribution as drawing two uniformly from the N-7 cards
after the opener, regardless of whether six Prizes were set aside.

The model's marginal success therefore remains identical for zero and six
random Prizes whenever the same natural draws are feasible. Individual
K1-known Prize configurations still matter, and search actions break the
simple exchangeability assumption.

## Validation

The SFT separately enumerates every opening-card subset, Prize subset,
first natural draw, and second natural draw in a labeled nine-card toy
deck. The exact combinatorial model agrees with this independent
enumeration, including an alternative experiment with zero random Prize
cards. It also verifies the exact available card prints and text-derived
evolution timing. CI run `37773831995` passed.

## Limitations and interpretation

These rates represent **unassisted card-and-timing readiness** in a
simplified game. Actual Expanded decks can significantly increase
access through search and draw engines. Opponent Knock Outs, Item lock,
Bench pressure, and other effects can prevent a theoretically available
evolution from resolving.

In particular, none of these probabilities should be multiplied by the
earlier conditional Teleport Room accessibility percentages to claim an
overall win or setup rate. The two experiments use different hypothetical
card partitions and are not one joint game-state distribution.

The next useful investigation is a single concrete 60-card model
including Gothitelle setup, Trainer access, the full Bench, and
discard-fed Stadium restoration in a shared timeline.
