# A two-horizon regional recovery package for Aichi Iron Thorns

## Question

After the named first-turn Volt Cyclone line fails, how often can the Japanese-only Palace Belt support the next turn while Palace Book or Player's Ceremony supplies an immediate end-turn draw continuation?

This result extends `iron_thorns_regional_failure_continuation/` by tracking Palace Belt and the two competing Active-dependent Tools in the published Kazuma and Kohei lists.

Implementation: `tools/iron_thorns_regional_recovery_package.py`  
Regression: `results/iron_thorns_regional_recovery_package/reproduce.py`

Ryoya's list is excluded from this endpoint because it contains no Palace Belt.

## Endpoint definitions

All probabilities use the same exact accepted-opening + six-Prize + first-normal-draw state space as `iron_thorns_named_line_probability/`.

A named-line failure has **Belt ready** when:

- Palace Belt is already in hand; or
- Guzma & Hala is accessible and at least one Belt remains in the deck.

The second route requires Guzma & Hala's optional two-card discard branch. The model establishes raw mechanical reachability and does not assign strategic DCI to the exact discarded cards.

A failure has **draw ready** when:

- Palace Book is in hand;
- Player's Ceremony is in hand; or
- Guzma & Hala is accessible and Player's Ceremony remains in the deck.

A failure is **dual-horizon ready** when Belt and one of those immediate draw continuations can be satisfied in the same state.

When Belt and Ceremony are both missing from hand, both remain in deck, and G&H is accessible, one G&H use can obtain the Stadium through its unconditional channel and the Tool through its optional discard channel. This is recorded separately as the **G&H fetch-both** witness.

## Exact results among named-line failures

| List | Belt ready | Immediate regional draw ready | Dual-horizon ready | G&H fetches Belt + Ceremony | Dual horizon + competing Tool already in hand |
| --- | ---: | ---: | ---: | ---: | ---: |
| Kazuma Kashi | **22.579832374%** | **32.848860519%** | **12.723906584%** | **7.808612206%** | **2.605033911%** |
| Kohei Hamamichi | **33.726034481%** | **22.579832374%** | **13.537034018%** | **7.629049728%** | **2.781642603%** |

As full accepted-opening state mass, the dual-horizon endpoint is 8.425579355% for Kazuma and 8.964020098% for Kohei.

The G&H fetch-both witness is 5.170745427% and 5.051841858% of the full state space respectively.

## Why the package is executable in one connector action

The local Guzma & Hala card text searches for a Stadium unconditionally. If two other hand cards are discarded, the same Supporter may also search for a Pokemon Tool and a Special Energy.

Therefore:

`Tag Call -> Guzma & Hala -> Player's Ceremony + Palace Belt (+ Special Energy)`

is a mechanically coherent multi-output recovery line when the named attack objective has already failed and both regional cards remain searchable.

The model does not require the Special Energy side payload because it is outside this endpoint. Its availability could increase the package's continuation value further.

## Tool contention

Kazuma and Kohei each contain one Handheld Fan and one Tool Jammer in addition to Palace Belt.

Both competing Tools depend on the holder being Active for their represented effect. A Pokemon can have only one Pokemon Tool attached. Choosing Belt for the Active Iron Thorns can therefore exclude immediate use of Fan or Jammer on that same Active Pokemon.

The model records a narrow visible-contention witness: the full dual-horizon package is ready while at least one Fan/Jammer copy is already in hand.

That occurs in only 2.605033911% of Kazuma named failures and 2.781642603% of Kohei named failures.

This is not the total strategic Tool opportunity cost. A competing Tool can still be in the deck, can be attached to another Pokemon for a later promotion plan, or can become more valuable in a matchup not represented here.

## Interpretation

This is a concrete multi-horizon connector line.

Player's Ceremony or Palace Book addresses the current failed turn by turning the remaining action window into cards.

Palace Belt addresses the following turn by increasing the normal beginning-of-turn draw while its holder remains Active.

Guzma & Hala can sometimes materialize both horizons in one Supporter action. The line therefore illustrates why a multi-output connector should be evaluated against several possible continuation objectives rather than only the failed immediate attack objective.

Kohei's second Belt meaningfully raises Belt readiness among failures, from 22.58% in Kazuma to 33.73%, but the dual-horizon rates stay close because both lists still contain only one Player's Ceremony and Kohei has no Palace Book.

## Cross-check

The reproducer independently calls `exact_named_line_probability()`.

For Kazuma and Kohei, the recovery model reproduces the exact original accepted-opening probability and named-line success probability before any recovery metric is considered.

## Limits

The calculation omits Trainers' Mail, Gladion, Speed Lightning Energy draw, VS Seeker, opponent mulligan bonus draws, other disruption Supporters, alternate attack lines, and opponent actions.

It does not decide whether the two G&H discards are strategically acceptable.

It does not value the Special Energy side payload that a paid G&H can also retrieve.

It records only Fan/Jammer already in hand as a visible Tool-contention witness. Full continuation planning would need board position, future switching, matchup-specific Tool value, Tool removal, and later draws.

Player's Ceremony remains symmetrical and ending the turn is a strategic choice.

## Next work

The next strongest extension is to include the Special Energy side payload and ask whether the same paid G&H recovery action can simultaneously improve the next turn's Energy state. A broader policy model could then compare the recovered line against using G&H or another Supporter for disruption instead.
