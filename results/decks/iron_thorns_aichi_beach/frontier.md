# Matched-cost Iron Thorns: second DCE versus second Tropical Beach

## Why this comparison exists

Kazuma Kashi's sixth-place 2026 Aichi Iron Thorns control list used the Japanese-only Player's Ceremony Stadium to end a turn with two cards drawn. The first English-print adaptation replaced that Stadium with a second Double Colorless Energy (DCE), emphasizing its named first-turn Volt Cyclone resource package. The second English-print candidate instead adds a second Tropical Beach promo, preserving a turn-ending draw plan at the cost of that DCE.

Both [speed deck](../iron_thorns_aichi_english/) and [draw-recovery deck](README.md) are complete, distinct, 60-card, English-print decks. They differ by exactly one card: one DCE for one Tropical Beach. Both retained the other two English substitutions (one Trainers' Mail for Palace Book, one Handheld Fan for Palace Belt). All published tournament source positions are attributed in their manifests. The alternatives are experimental, and neither has a measured win rate.

## Source card effect

The bundled English Tropical Beach promo, BW28, says each player may once during their turn draw up to seven cards in hand, ending that player's turn if used. It can be played as the one Stadium for the turn if allowed, and G&H can search it through its unconditional Stadium channel.

The same effect is available to the opponent on their turn. This is an important strategic cost missing from the calculation.

Printed Guzma & Hala (Cosmic Eclipse 193) can search one Stadium without paying a discard. Its optional side search for a Pokémon Tool and Special Energy requires discarding two other cards. Consequently, a failed DCE attack branch can pivot to a Tropical Beach search without its optional discard if the card is in the deck.

## Physical model and event definitions

Exact sample space: seven-card opening conditioned on at least one of four Iron Thorns ex Basic starters, six hidden Prize cards from the remaining deck, and one first going-second natural draw. A single Iron Thorns becomes Active. Opponent mulligan bonus cards are excluded.

Fixed structural counts: four Iron Thorns, two Tag Call, two G&H, one Thunder Mountain Prism Star, 12 other *hypothetically acceptable* two-card-discard targets, and remaining protected cards. Speed variant has DCE 2 / Beach 1; recovery variant has DCE 1 / Beach 2.

**Attack event:** Thunder Mountain and DCE are in hand or obtainable using one G&H action, while any required G&H two-card discard can be paid using two held cards from the designated 12-card safe subset. Tag Call can find a G&H if it is still in the deck. An already held DCE needs no optional G&H discard to find Thunder Mountain.

**Fallback event:** the attack event is absent, and Tropical Beach is held or can be found by the same G&H/Tag Call connector route from the remaining deck. This represents immediate access to a Stadium activation that can draw cards and ends the turn. Attack availability takes priority, making attack and fallback buckets disjoint. Two policy choices are compared in an additional sensitivity: strict discards versus allowing expendable spare Tag Call/G&H copies.

The 12-card safe subset may be instantiated *hypothetically* as four Crushing Hammer, four Trainers' Mail, two Enhanced Hammer and two Camping Gear in both decklists. In actual games these cards have varying tactical value and can be needed for other actions. This assumption deliberately does not optimize DCI or future turns.

## Exact matched-size results

| Deck choice | Attack package available | Attack failure with Beach fallback | Neither endpoint |
|---|---:|---:|---:|
| Speed: 2 DCE / 1 Beach | **20.953811%** | 27.046351% | 51.999839% |
| Recovery: 1 DCE / 2 Beach | 16.293836% | **39.657754%** | 44.048410% |

The second DCE adds 4.659975 percentage points of immediate strict-paid attack access. The second Beach adds 12.611403 points of fallback access conditional on the attack not being available.

If one arbitrarily scores an attack-ready event at utility 1 and a Beach fallback at utility v, the equal-score point is the exact ratio **41265224571587 / 111677083922987 = 0.369504854**. The draw-recovery variant wins that toy score only when fallback value exceeds about 36.95% of attack access value. Actual game utility depends on which cards the Beach draw produces, the opponents' use of Beach, and how much an early Volt Cyclone matters.

### Hypothetical discard-pool sensitivity

| Safe cards | Speed attack | Speed Beach fallback | Recovery attack | Recovery Beach fallback |
|---:|---:|---:|---:|---:|
| 0 | 9.234391% | 37.504419% | 4.841275% | 50.993581% |
| 6 | 12.954847% | 34.187282% | 8.452492% | 47.419695% |
| 12 | 20.953811% | 27.046351% | 16.293836% | 39.657754% |
| 19 | 29.529449% | 19.374890% | 24.836675% | 31.198559% |
| 30 | 36.568688% | 13.052225% | 32.080710% | 24.020768% |

Increasing the designated safe pool raises immediate attack availability for both lists, which reduces the mass left for the fallback event. More Beach copies preserve greater fallback access in the measured range. This is a structural event-coverage result, not an inference that more Tropical Beach is universally stronger.

## Reproduction

- Exact grouped multivariate hypergeometric solver: [tools/iron_thorns_beach_frontier.py](../../../tools/iron_thorns_beach_frontier.py).
- Deck print, source-count and legality proof: [reproduce.py](reproduce.py).
- Independent labeled physical oracle: [frontier_reproduce.py](frontier_reproduce.py).
- Windows regression workflow: [validate-iron-thorns-beach-frontier.yml](../../../.github/workflows/validate-iron-thorns-beach-frontier.yml).

The solver uses an equivalent randomization order of next draw before allocating hidden Prize cards. The oracle instead explicitly deals opening, six Prizes and then the draw. Three toy decks exhaustively enumerate 13,608, 25,200 and 47,880 labeled worlds; all event buckets agree exactly. The attack component is independently checked against [G&H discard payability](../iron_thorns_aichi_english/discard_payability.md), making the added measurement the joint failed-attack and Beach-access event.

## What is still unknown

The model intentionally does not follow the extra Beach draw into next turn. It omits Trainers' Mail searches, Speed Lightning Energy drawing, hand-playing potentially expendable Item cards before G&H, opposing mulligans, Stadium counterplay, both-player Beach reuse, Tool displacement and lock rules, action sequencing after other Supporters, opponent board state, and match timing. It also ignores the utility of a failed attack line's remaining cards.

Both candidates should remain labeled exploratory. A next-step two-turn decision solver could quantify actual drawn-card rescue, opponent reuse and the option to hold G&H before committing the attack or Beach line. Full competitive ranking ultimately requires real opponent-play evidence.

