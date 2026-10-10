# Realistic access qualifier for a Gladion–Communication Grand Tree rescue

## Question

The physical Grand Tree Prize-repair witness is genuinely possible,
and when both Gladion and Pokémon Communication are **already in hand**
its conditional supply effect can be large. How rare is a much stricter
event that actually co-locates all of the necessary cards at the start
of a game, while respecting Basic-only accepted opening hands,
the six Prize cards, and the natural first two draws?

This analysis is an intentionally narrow **card-access certificate**.
It is not the probability of accomplishing the full archetype setup
or winning a game.

## Deck and certified line

Consider an illustrative 60-card deck containing four Gothita Basic,
one critical Gothorita, one critical Gothitelle, one Grand Tree
ACE SPEC, G Gladion copies, C Pokémon Communication copies, and
the remaining `53-G-C` slots as non-Basic filler. Let `G,C`
vary between 1 and 4.

The starting seven-card hand must contain:

* at least one Gothita, ensuring a valid Basic opening;
* the singleton Grand Tree, accessible to be played during turn one
  or turn two;
* at least one Gladion and one Pokémon Communication;
* neither the singleton Gothorita nor the singleton Gothitelle.

Then six Prize cards are set from the remaining 53 physical cards.
The critical Gothorita must be **Prized**, so Gladion can select it.
The critical Gothitelle must remain **unprized** in the deck.
After two ordinary beginning-of-turn draws, Gothitelle must remain
in deck, available to Grand Tree's second search.

The declared Gothita starts play in setup and is eligible for
Grand Tree evolution on the owner's second turn. On that turn,
subject to no Item/Supporter/Stadium lock and continued board
survival, the player may use Gladion to recover the Prized
Gothorita into hand, Pokémon Communication to return it into deck
while declining to take another Pokémon from the search,
and Grand Tree to evolve Gothita through Gothorita to Gothitelle.

## Exact combinatorial calculation

Sampling is without replacement. The opening hand is conditioned
on at least one of the four Basic Gothita because hands without
Basic Pokémon are mulligans. For the accepted opening, the
denominator is

`D = C(60,7) - C(56,7)`.

Let `F=53-G-C` be the filler count. The number of opening hands
holding Grand Tree, at least one Basic Gothita, Gladion and
Pokémon Communication, and no critical evolution cards, is

`H = sum_b=1..4 sum_g=1..G sum_c=1..C
 C(4,b) C(G,g) C(C,c) C(F,7-1-b-g-c)`

where invalid binomial arguments are zero.

Conditional on such a hand, the two named evolution cards are
both among the remaining 53 cards. Exactly the Stage 1 must enter
the six Prizes while Stage 2 remains outside:

`P(Prize Stage1, not Stage2) = C(51,5)/C(53,6)`.

Of the remaining 47 deck cards, the one critical Gothitelle
must avoid the next two natural draws:

`P(avoid next two draws) = 45/47`.

The final accepted-opening-conditioned exact event probability is

`P(E|valid Basic opening) =
(H/D) * [C(51,5)/C(53,6)] * (45/47)`.

These three factors are valid as a sequential chain of conditional
probabilities over physical cards. No false independent Stage1
and Stage2 Prize assumptions are used.

## Result

| Gladion copies | Communication copies | Exact access event among accepted openings |
|---:|---:|---:|
| 1 | 1 | 0.005788% |
| 2 | 2 | 0.021843% |
| 3 | 3 | 0.046335% |
| 4 | 4 | **0.077605%** |

The event is rare even when four copies of both connector cards
exist, because the starting hand must simultaneously contain a
Basic, the singleton Stadium, Gladion and Communication, while
a singleton Stage1 is in Prizes and Stage2 remains searchable
after the first two natural draws.

This sharply qualifies the earlier **85.43% conditional full-three
supply** example. That example starts *after* the bridge cards
are known available. Here, their joint access is explicitly
part of the event.

The two results have different populations and objectives; their
percentages must never be multiplied or compared as if the earlier
full-three conditional population represented all starting hands.

## Reproduction

`python results/grand_tree_opening_rescue_access/reproduce.py`

Implementation: `tools/grand_tree_opening_rescue_access.py`.
The independent oracle enumerates actual labeled opening-hand
subsets, subsequent six-Prize subsets, and subsequent natural-draw
subsets in ten smaller-card toy universes. Each exact rational result
must agree with the factored formula. The main program reports
results for every `G,C` combination in 1 through 4.

## Limitations

The event represents one exact, restrictive route. Opening draw,
Prize placement and two subsequent draws are jointly modeled.
Many real lines can establish necessary Pokémon and the Stadium
through searches, later draws, Pokémon Abilities or alternative
opening hands. The output is therefore neither a general setup
success estimate nor a bound on match win probability.

Deck legality is scoped to the modeled card names and copies.
The filler is stipulated to contain no other Basic Pokémon,
which determines the mulligan-conditioning event. Real deck
lists with additional Basics would have a different accepted-
opening law.

It also assumes Grand Tree can be placed at the required time,
the selected Basic survives to its second turn, the opponent
does not lock Item/Supporter use, and no competing Supporter
action prevents the Gladion rescue.

The one-turn **physical Prize-to-deck bridge** is independently
valid without the disputed same-physical-Stadium return rule.
This model counts a **single** Grand Tree Stage2 evolution,
so its probability statement does not rely on that dispute.

Related work:
[physical Gladion+Communication bridge](../grand_tree_prize_rescue_bridge/),
[accepted-opening conditioning](../setup_mulligan_policy/),
[Grand Tree evolution materialization](../grand_tree_materialized_chain/).
