# Talonflame setup policy case: turn order changes the value of optional-only hands

## Scope

This is a concrete case study of the hand-state setup framework using Hudson
Matheus's 18th-place Gardevoir/Talonflame list from LAIC 2018:

https://limitlesstcg.com/decks/list/915

That event list was played in Standard at the time. Here it is used only as a
fixed 60-card composition inside the paper Expanded research environment. The
reproduction script checks that every named card in the list has at least one
effectively legal Expanded printing in the bundled database. This is not a
claim that the 2018 list is competitively optimal in 2026.

The list contains:

- 4 Talonflame with **Gale Wings**;
- 9 ordinary Basic starters: 4 Ralts, 2 Tapu Lele-GX, 1 Alolan Vulpix,
  1 Mew-EX, and 1 Giratina;
- 4 Ultra Ball and 2 Brigette;
- 7 Fairy Energy and 4 Double Colorless Energy;
- 30 other cards.

The bundled card data confirms that `xy11-96` Talonflame is Expanded legal,
has Gale Wings, and has the one-Colorless **Aero Blitz** attack that searches
the deck for up to two cards. It also confirms the relevant Ultra Ball and
Brigette search text.

## Why Talonflame creates a genuine setup decision

Gale Wings says that if Talonflame is in the opening hand during setup, the
player may put it face down as the Active Pokémon.

A hand containing an ordinary Basic is already a forced keep under the normal
setup rule. The strategically interesting hands are therefore those with:

- zero ordinary Basics;
- at least one Talonflame.

In this list, such an optional-only opening occurs on **13.693074%** of shuffled
seven-card hands.

Those hands are heterogeneous. Some already contain a mechanical route to put
Ralts into play. Others can attack with Aero Blitz going second. Some do
neither.

## Exact optional-only hand composition

Classify the 60 cards into six disjoint groups:

| Group | Copies |
| --- | ---: |
| Forced Basics | 9 |
| Gale Wings Talonflame | 4 |
| Brigette | 2 |
| Ultra Ball | 4 |
| Energy: Fairy or Double Colorless | 11 |
| Other cards | 30 |

Conditioned on drawing an optional-only hand:

| Property | Probability |
| --- | ---: |
| Contains Brigette | 23.377071% |
| Contains Ultra Ball | 42.009651% |
| Brigette without Ultra Ball | 14.692088% |
| Ultra Ball without Brigette | 33.324667% |
| Contains both search channels | 8.684983% |
| Contains Brigette or Ultra Ball | 56.701738% |
| Contains any Energy | 80.531053% |
| Contains search or Energy | 93.677027% |
| Contains neither search nor Energy | 6.322973% |

This is an exact multivariate-hypergeometric calculation.

### Mechanical Ralts access

Brigette can search Basic Pokémon directly. Ultra Ball can search Ralts after
discarding two cards.

For this narrow mechanical-access test, every optional-only opener containing
Ultra Ball has enough cards remaining in hand to pay its two-card discard
cost after one Talonflame is placed Active. This says nothing about whether
those discards are strategically desirable. DCI and AMR can still make a
mechanically legal Ultra Ball route unattractive.

Because an optional-only hand contains no Ralts, all four Ralts remain in the
53-card deck before the six Prize cards are set. The exact chance that all four
Ralts then become Prized is only **0.005123%**. Thus the hand-level search
criterion is an extremely close approximation to actual Ralts availability,
while still having a precisely quantified Prize failure mode.

## Turn order creates a downstream policy split

The Advanced Player's Rulebook describes special attacks that can be used on
the first player's first turn as exceptions to situations where the rules
would normally prevent attacking. Talonflame's Aero Blitz has no such
exception.

Therefore the Energy-based Aero Blitz route is immediately available on the
first turn only when the Talonflame player goes second.

This creates two simple line-aware filters:

- **search filter:** keep a Talonflame-only opener if it contains Ultra Ball or
  Brigette;
- **search-or-Aero filter:** going second, keep if it contains one of those
  search cards or any Energy that can pay Aero Blitz.

These are line filters rather than claims of globally optimal play.

## Mulligan consequences

| Optional-only policy | Acceptance per shuffle | Expected failed mulligans |
| --- | ---: | ---: |
| Decline every Talonflame-only hand | 70.022521% | 0.428112 |
| Keep only immediate-search hands | 77.786732% | 0.285566 |
| Keep search-or-Aero hands | 82.849786% | 0.207004 |
| Keep every Talonflame-only hand | 83.715595% | 0.194521 |

The going-second search-or-Aero filter captures most of the mulligan reduction
available from unconditional Talonflame acceptance. Relative to accepting every
Talonflame-only hand, it gives up only **0.865809 percentage points** of
per-attempt acceptance while rejecting the 6.323% of optional-only hands that
lack both modeled lines.

The going-first search filter is much more selective because the attack route
is unavailable during that first turn.

## K0 Prize priors also change

The policy conditions which opening hands terminate the redraw sequence, so it
also changes the initial Prize prior.

Specific-card Prize probabilities are:

| Policy | Forced Basic | Talonflame | Brigette | Ultra Ball | Energy | Other |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Decline optional-only | 9.434569% | 10.099782% | 10.099782% | 10.099782% | 10.099782% | 10.099782% |
| Search filter | 9.622837% | 9.888846% | 9.975810% | 9.975810% | 10.097176% | 10.097176% |
| Search-or-Aero filter | 9.726599% | 9.765785% | 10.058002% | 10.058002% | 10.058002% | 10.080381% |
| Accept all optional-only | 9.743086% | 9.743086% | 10.071061% | 10.071061% | 10.071061% | 10.071061% |

Under the search filter, both search channels are slightly less likely to be
Prized than Energy or filler because optional-only hands containing either
channel are preferentially accepted.

Under the search-or-Aero filter, individual Brigette, Ultra Ball, and Energy
cards have the same Prize probability. The policy treats the presence of any
one of those cards as sufficient to keep, even though their class sizes and
execution costs differ.

## Strategic interpretation

This case gives a concrete example of why "optional starter present" is too
coarse a setup state.

Talonflame-only hands can differ in at least three strategically relevant ways:

1. whether a Ralts-search route is already executable;
2. whether Aero Blitz can be powered immediately;
3. whether turn order allows that attack to be used now.

The same Talonflame card therefore has different practical setup value across
hands and turn orders while its setup legality remains unchanged.

The result also illustrates the distinction between access and AMR. Among all
optional-only hands, **33.324667%** contain Ultra Ball without Brigette and
therefore expose the two-card discard payment if the player wants immediate
Ralts access. **14.692088%** contain Brigette without Ultra Ball and instead
expose the Supporter-for-turn cost. Another **8.684983%** contain both channels,
so the player can choose which resource to spend.

Those channel shares are mechanical facts about the opening distribution. A
richer Gardevoir-specific hand-value model would need DCI for Ultra Ball's two
discards, Supporter contention around Brigette, and the value of delaying board
development in exchange for Aero Blitz.

## Reproduction

Run:

`python results/talonflame_setup_policy_case/reproduce.py`

The script:

- validates the 60-card composition;
- verifies current Expanded-legal print availability for every named card
  against the bundled resources;
- verifies the relevant Talonflame, Brigette, and Ultra Ball text;
- computes the exact optional-only hand partition;
- reports acceptance and expected mulligans for all four policies;
- computes exact policy-conditioned Prize priors;
- computes the all-four-Ralts-Prized failure probability.

## Limits and next questions

The line filters deliberately omit draw Supporters, Tapu Lele-GX chains,
strategic discard costs, matchup pressure, Bench value, and the opponent's
first turn.

A stronger continuation model should evaluate the whole opening hand and
first-turn sequence. In particular:

- Ultra Ball should pay a DCI-aware two-card cost;
- Brigette should compete with Professor Sycamore, N, Cynthia, and other
  Supporters for the turn;
- going-second Aero Blitz should be valued by what its two searched cards make
  possible on the following turn;
- opponent first-turn lock or disruption can reduce the AMR of the Aero line.

Those additions would turn this exact line-coverage calculation into a
deck-specific setup policy model.
