# Bellelba-only Tag Call: exact first-search fallback ceiling

## Research question

The Aichi Vileplume first-turn study in
[results/aichi_tagcall_information_preview](../aichi_tagcall_information_preview/)
models a supplemental Tag Call before playing an already-held Guzma & Hala
(G&H), but restricts that extra Item search to obtaining additional G&H
copies.

The published 2026 Aichi runner-up Vileplume list has four G&H, four
Tag Call and **one Bellelba & Brycen-Man**. Both Supporters are TAG TEAM
cards, so Tag Call may retrieve either. A player may search for **one**
eligible TAG TEAM card, because the card says "up to 2." A prior Tag Call
that finds Bellelba and reveals the remaining deck supplies the same K1
Prize-location observation before paying G&H.

How often can Bellelba be the **only searchable TAG TEAM Supporter**
when G&H is already available and an early Jirachi setup is relevant?

## Literal card and rule basis

The bundled English card snapshot at resources/cards/en/sm12.json
contains the following specific print records:

- sm12-206 Tag Call, Item: search for up to two TAG TEAM cards, reveal
  them, put them into hand, shuffle.
- sm12-193 Guzma & Hala, Supporter and TAG TEAM.
- sm12-186 Bellelba & Brycen-Man, Supporter and TAG TEAM.

The provided Advanced Player's Rulebook, H. Deck and D-05 "Up to,"
permits taking fewer than the named quantity in a limited-category
deck search. The player can therefore search for just one Bellelba even
if G&H is already in hand. Tag Call is an Item, leaving the ordinary
Supporter play available.

The published Aichi runner-up Vileplume deck counts were transcribed
into tools/aichi_setup_inference.py: 46 non-Basic cards, 14 Basic cards,
G&H4, Tag Call4, Bellelba1. Its specific use in this event model
should not be generalized to every regional Expanded card pool.

## Event and exact calculation

This calculation deliberately isolates a **necessary visible/hidden
card configuration**, not the downstream game-winning line.

For a random shuffled 60-card deck:

1. The seven-card opener must contain the deck's unique Jirachi
   (one of 14 eligible Basic starters), so the hand is accepted.
2. After the single natural turn draw, among seven non-Jirachi
   visible cards the player must hold at least one G&H and at least
   one Tag Call.
3. Every G&H not among those seven visible cards must be within six
   hidden Prize cards. Thus another G&H is absent from the
   searchable deck.
4. The singleton Bellelba must be absent from the visible cards
   and the Prizes, hence searchable.

Any extra Tag Call can now retrieve Bellelba alone, revealing the deck
before the held G&H's optional two-card discard.
The first decision to play Tag Call uses only prior visible information;
the later payment can respond to the search information.

We count the natural draw before Prizes conditionally. Uniform
exchangeability of the unrevealed deck positions makes this equivalent
to physical Prize placement before the draw.

Let k be the number of G&H among the seven visible non-Jirachi
cards and t the number of Tag Call among them.
The deck has 50 other non-Jirachi cards beyond G&H4, Tag Call4,
Bellelba1. There are 52 unseen positions after the seven non-Jirachi
cards and the known Jirachi.

The exact unconditional event probability is

\[
\Pr(E)=\frac{7}{60}
\sum_{k=1}^{4}\sum_{t=1}^{4}
\frac{\binom{4}{k}\binom{4}{t}\binom{50}{7-k-t}}
{\binom{59}{7}}
\frac{\binom{52-(4-k)-1}{6-(4-k)}}
{\binom{52}{6}}.
\]

Terms outside combinatorial bounds are zero.
The conditioning event is a Basic-valid opening,
with probability

\[
\Pr(\mathrm{accept})=1-
\frac{\binom{46}{7}}{\binom{60}{7}}
=\frac{252032}{292581}.
\]

Therefore

\[
\Pr(E\mid\mathrm{accept})=
\frac{74221}{1341841280}
=\boxed{0.005531280123\%}.
\]

Equivalently, about one such event in **18,079 accepted starts**.

Breakdown by number k of G&H already visible:

| Visible G&H | Fraction of all accepted openings |
| ---: | ---: |
| 1 | 0.001340552804% |
| 2 | 0.002587473167% |
| 3 | 0.001420492814% |
| 4 | 0.000182761338% |
| **Total** | **0.005531280123%** |

The event is sufficiently rare that **any improvement restricted
solely to this Bellelba-only fallback is bounded above by
0.005531280123 percentage points** of accepted openings for a binary
first-turn success metric. That is an opportunity upper bound, even
when granting certain success for every event counted. A realistic
actual improvement could be zero.

This upper bound says nothing about more frequent Tag Call searches
for Bellelba when another G&H is still searchable. Those possibilities
require a different event definition and comparison policy.

## Verification

- Exact rational arithmetic via Python Fraction, integer combinatorics.
- An independent physical-card-labeled oracle enumerates all
  accepted openers, next-draw cards and disjoint Prize subsets in an
  11-card toy deck with Jirachi1, other Basics2, G&H2, Tag Call2,
  Bellelba1, other filler3. Both evaluators return **62/1365**.
- Full 60-card result is asserted as the exact fraction
  **74221/1341841280**.
- The probability across k=1..4 partitions is checked to sum exactly
  to the same fraction.

Source: tools/aichi_tagcall_bellelba_ceiling.py.
Regression: results/aichi_tagcall_bellelba_ceiling/reproduce.py.
[Passing GitHub Actions run 38061180727](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38061180727).

## Limits and possible extensions

The event only represents naturally held cards plus one natural draw;
it assumes no earlier deck inspection, mulligan extra draws, search
connectors, discard, opponent lock or other first-turn action.
It counts a legal opportunity to search for Bellelba; it makes no
claim that the optional Tag Call improves the Aichi two-Stage-2
evolution endpoint, which also requires discards and other card access.

The Aichi information-preview model's G&H-only action set may omit
other useful Tag Call choices even when G&H remains searchable.
The next informative experiment is an exact or state-preserving
paired action-set comparison that permits TAG TEAM targets from the
real list and scores the downstream Jirachi/G&H endpoint. It must
preserve information timing, search target movement and the
Supporter quota before attributing any gain to information.
