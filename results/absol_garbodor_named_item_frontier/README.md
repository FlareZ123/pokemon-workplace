# Mega Absol ex: first-turn physical named-Item access

## Research question

How much does a **third Mega Absol ex** improve immediate first-turn access in the [2026 Aichi eighth-place Mega Absol/Garbodor list](../competitive_deck_baselines/), once the actual Quick Ball, Ultra Ball, Battle VIP Pass, Pokémon Communication and Hisuian Heavy Ball cards are included with their constraints?

This study compares the **unchanged published 60** (two Mega Absol), a complete three-copy version replacing one of two Temple of Sinnoh, and a complete three-copy version replacing the sole Crobat V. All three are conservatively `eligible_snapshot` at October 12, 2026 and preserve a single Secret Box and all other counts. The original [source manifest](../competitive_deck_baselines/absol_garbodor_kobayashi_2026.json) remains unmodified.

## Exact conditional access

Randomly draw a seven-card opening, accept only hands containing a Basic Pokémon, select the starting Active, place six hidden Prize cards from the remaining physical deck, then reveal the player's first natural draw. The model evaluates whether **one immediately playable named Item** can obtain a Mega Absol, or a Mega is already in hand. No Item chains or other draw effects are credited.

| Route policy | Published two Mega | +1 Mega / −1 Temple | +1 Mega / −1 Crobat V |
| --- | ---: | ---: | ---: |
| Mega already directly in hand | 32.519203% | 43.929817% | 45.798873% |
| Direct, Battle VIP Pass, or Hisuian Heavy Ball | 50.220804% | 59.554440% | 60.821351% |
| **Paid search**, including conditional Pokémon Communication | **68.319327%** | **74.931248%** | **75.410322%** |
| Unpaid search graph upper envelope | 82.542202% | 86.498911% | 86.823945% |

All percentages are **conditional on a Basic-valid opening** and include a six-card Prize packet. The three configurations respectively have 10, 11, and 10 Basic Pokémon, so the conditioning denominator changes when Temple of Sinnoh is replaced.

Relative to the published deck, the third Mega gives **+6.611921 percentage points** in the paid one-step Item access event when Temple is cut and **+7.090995 points** when Crobat is cut. This is substantially smaller than the gains in direct-hand access because the published list already has many searchable routes.

## Strict route contract

The `energy_paid` policy accepts the first successful physical route among:

- A Mega Absol directly held in hand (or chosen as starting Active).
- Battle VIP Pass in the hand during the player's first turn, with at least one Mega available outside Prizes and hand, and an intentionally reserved Bench slot.
- Quick Ball in hand with at least one *other held Energy card* available to discard, and a Mega still in deck.
- Ultra Ball in hand with at least two *other held Energy cards* available to discard, and a Mega still in deck.
- Pokémon Communication in hand with at least one spare, genuinely held Pokémon **after one starting Active has been removed from the opening hand**, and a Mega in deck.
- Hisuian Heavy Ball in hand with at least one Mega in the six Prize cards.

The Energy-only discard restriction is an **explicit hypothetical hand-preservation policy**. Actual Quick Ball and Ultra Ball allow other cards to be discarded; an Energy may itself be vital to attacking and therefore inappropriate to discard. The paid rate is neither a strict rules ceiling nor a human optimal play prediction. The `unpaid_upper` mode ignores costs on Quick Ball, Ultra Ball and Pokémon Communication and so is a theoretical named-search ceiling under the specified one-step action restriction. The `vip_or_heavy` mode provides an independent non-discard search boundary.

The source deck has four Quick Ball, two Ultra Ball, two Battle VIP Pass, one Pokémon Communication, one Hisuian Heavy Ball and seven Energy. Its ten published Basics include two Mega Absol. Separate source-card text checks enforce the five Item mechanics. One Basic card from the initial seven must be placed Active, preventing Pokémon Communication from reusing that same physical card as an exchange payment.

## Computation and crosschecking

`tools/mega_absol_named_item_access.py` enumerates exactly every feasible *multivariate seven-card opening-count state* and the type of its first drawn card. A labeled hand with count vector `h` has integer weight `product(C(capacity[i], h[i]))`; the first draw of type `j` multiplies this by `capacity[j] − h[j]`. Target Prize multiplicities are integrated using the hypergeometric factor `C(remaining_mega,k) C(remaining_other,6−k)` with the conditional remaining deck size, and all masses are accumulated as exact integer numerators and `Fraction` ratios.

The separate `physical_oracle` enumerates **every individually labeled hand, Prize selection and first draw** on three twelve-card toy decks, without using the category-weight or hypergeometric solver. All five probability outputs agree exactly on all three toys.

Reproduce:

`python -m results.absol_garbodor_named_item_frontier.reproduce`

[Manual Windows CI run 38249747598](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38249747598) passed the tournament baseline, the earlier opening-copy frontier, and this new paid named-Item frontier.

## Strategic interpretation

The third Mega reduces the chance of a target-access gap, but replaces a distinct competitive resource. A Temple of Sinnoh cut forfeits Special Energy disruption. A Crobat V cut removes the singleton Dark Asset draw engine and a Basic starter. The conditional direct/Item-search metrics intentionally do not assign utility to either displaced card.

Other omitted lines include Forest Seal Stone Star Alchemy, Adventure Bag into a Tool connector, Bench draw Abilities, Supporter draws, multiple Items in sequence, opponent locks, going-first/second differences beyond the named first draw, first-turn attachments, damage-counter setup, Garbotoxin activation, and prize-recovery sequencing. The reported percentages are **exact probabilities for the declared initial physical-card decision problem**, with no claim of estimated matchup win rates or of any third-copy variant being competitively superior.

**Source evidence:** May 10, 2026 CL Aichi [published top-eight decklists](https://limitlesstcg.com/tournaments/566/decklists) and exact English card-print snapshot under `resources/cards/en/`. All probabilistic and deck-adjudication claims are reproduced by the checked-in code above.
