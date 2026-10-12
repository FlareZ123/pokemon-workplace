# Aichi champion: Latias ex Skyliner as a second pivot to Max Geist

## Deck-specific strategic question

The [2026 Aichi champion's 60 cards](../../decks/shadow-rider-calyrex/) include one Latias ex (sv8-76), one Float Stone, one Dimension Valley, one Radiant Eternatus, four Shadow Rider VMAX, eleven Basic Psychic Energy, four Mysterious Treasure and one Quick Ball. Earlier [Energy-paid search](../shadow_rider_paid_ball_attack/) research represented Float Stone as the sole way to retreat the initial Active Basic into a charged VMAX. The printed Latias ex ability, **Skyliner**, states that your Basic Pokémon in play have no Retreat Cost.

A starting Active Basic can therefore retreat for free while Latias ex's Ability is active, whether Latias is itself the Active, is already Benched, or is naturally drawn and then Benched during the charging turn. Latias is one of the champion's 13 non-Radiant Basic Pokémon, and physically having it available changes the attack continuation even without locating Float Stone.

## Exact policy and board capacity

Retain the [conservative search-payment route](../shadow_rider_paid_ball_attack/) as defined: a Basic-valid seven-card opening with a non-Radiant starting Basic, six Prize cards, first natural draw, direct Radiant in hand or one Mysterious Treasure/Quick Ball used to fetch it by **discarding one Psychic Energy**, two VMAX placed from deck by Climactic Gate, and the turn ending. After an uninterrupted opposing turn, the player draws once, uses two payable Underworld Door draw/attachment windows on a Benched VMAX, and makes one manual attachment. Three attached Energy support normal Max Geist. Two support it if the singleton Dimension Valley is physically accessible and legally playable that turn.

The initial Active is Basic by construction. A held Latias can be played onto the Bench as required, or can be the initial Active; a Latias drawn by Underworld Door can be put onto Bench after drawing and before retreating. Float Stone remains an alternative pivot. With one Radiant and two VMAX on the Bench, adding Latias brings occupancy to four, below the ordinary cap of five. The model assumes the player leaves sufficient Bench slack, Latias's Ability is active, Float Stone is playable when used, and a charged VMAX can be promoted after the Energy attachments. Extra starting Basics can be retained in hand rather than Bench-bloating the board.

The **pivot endpoint** requires Float Stone available to attach to the Active Basic **or** Latias ex already in play or available from these natural/Ability draws to enter. The attack endpoint requires that pivot plus one of the two Energy/Stadium modes.

## Exact results per accepted opening of the published 60

| Milestone | Direct Radiant | Psychic-paid Ball | Combined |
| --- | ---: | ---: | ---: |
| First-turn Radiant double-VMAX launch | 12.017840120% | 29.446836494% | **41.464676614%** |
| Three-Energy Max Geist + Float **or Latias** retreat | 1.544094123% | 1.728146658% | **3.272240780%** |
| Two-Energy Max Geist + accessible Valley + either pivot | 0.438239334% | 0.565100250% | **1.003339585%** |
| **At least one complete charge + pivot route** | **1.736097829%** | **2.039929998%** | **3.776027827%** |

The final row is the union of normal and Valley-assisted modes, with their overlap subtracted. Counting only Float Stone yielded **1.863998282%** for this same direct-or-Energy-paid search policy. Counting natural Latias access as an additional legal retreat channel raises the restricted next-turn attack route to **3.776027827%**, a gain of **1.912029545 percentage points**.

This comparison illustrates why treating a single Tool as the sole possible pivot can systematically undervalue a deck's existing Basic support. It does not claim that all 3.776% of these sampled openings would result in a damaging attack against a capable opponent; the intervening opponent is assumed not to disrupt the board, and no actual matchup outcome is modeled.

## Physical probability model and validation

The new [five-category Underworld Door module](../../../tools/shadow_rider_latias_pivot.py) tracks Psychic Energy, Float Stone, Latias ex, Dimension Valley and filler in the two conditional two-card draws. It computes the exact joint event requiring an Energy threshold and at least one of the possible pivots.

To avoid expanding every opening/Prize state into a full extra category, the enumerator uses exact singleton exchangeability. There is precisely one Latias among 13 non-Radiant Basics. Given the other-Basic population's current hand and deck counts, the Latias identity lies in each zone with probability proportional to the number of cards of that class there. Likewise, Dimension Valley is one of 25 otherwise neutral cards in the search-aware full-60 model. The two independent card-identity splittings are integrated with the physically conditioned Psychic, Float, and Ball-source resources. Latias probabilities are **mass-weighted over the detailed full-deck categories** when multiple opening/Prize histories collapse into the same observable resource state; averaging those posterior counts is exact for this singleton requirement.

The [reproducer](reproduce.py) checks source print sv8-76 and the champion's listed one-copy Latias, tests the exact published-60 fractions, and compares the complete model to **four independent exhaustive small-deck oracles**. These physically label Latias, Float and Valley separately, simulate opening, Prizes, paid search and Psychic discard, both natural draws and full shuffled deck permutations, and only then apply Underworld Door and pivot rules. The small-deck oracle and analytical Fraction model agree. Offline tests passed 12 October 2026; full-game Twinleaf or match-result verification is not claimed.

## Boundaries and next use

The actual champion has additional ways to obtain Latias ex, including a separate Quick Ball or Mysterious Treasure search, which this model deliberately excludes. It also has Guzma, other movement options, first-turn setup and draw effects, and matchup-relevant Supporters. Bench-position crowding, Ability lock from an opponent, Pokémon Tool locking, opponent knockouts before the charging turn, damage and Prize trades remain out of scope.

The next research priorities are to evaluate paid Ball role contention when the same source could get Radiant or Latias, examine when spending Psychic Energy for search suppresses future Underworld Door activations, and measure attack-and-KO readiness against actual Aichi tournament opposition. None of these narrow access probabilities is a match-win percentage.
