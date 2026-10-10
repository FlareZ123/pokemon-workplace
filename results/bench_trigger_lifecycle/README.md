# Bench-trigger lifecycle: built-in ways to repay Bench debt

## Question

Hand-to-Bench support Pokémon create value when they enter play, but after the trigger resolves the Pokémon usually remains in play and continues occupying a Bench slot. How often does such a Pokémon contain its own built-in way to leave play again?

This result scans the legal paper-Expanded card pool for Basic Pokémon with literal hand-to-Bench Ability triggers and then asks whether the same card has an attack that returns or shuffles **itself** to the player's hand or deck.

Implementation: `tools/bench_trigger_lifecycle.py`  
Reproducer: `results/bench_trigger_lifecycle/reproduce.py`

## Why this matters

A search graph can treat Tapu Lele-GX, Dedenne-GX, Crobat V, Lumineon V, or another Bench-entry support Pokémon as a temporary connector: play it, get value, and continue the line.

Board geometry is less forgiving. Unless another effect removes it, that Pokémon remains in play and consumes one of five Bench slots. The slot consumption is therefore a persistent state change rather than a zero-cost edge.

A built-in self-removal attack can repay that **Bench debt**, but attacking has its own resource and timing cost. The Advanced Player's Rulebook states that using an attack ends the player's turn, so attack-gated cleanup competes directly with the turn's main attack and also requires the support Pokémon to become Active and meet the attack cost.

## Card-pool result

The underlying literal hand-to-Bench trigger catalog contains:

- 123 legal prints;
- 48 unique card names;
- 51 conservative gameplay fingerprints.

Among those cards, the self-vacating scan finds:

- 22 prints;
- 6 unique card names;
- 7 conservative gameplay fingerprints;
- **0 self-vacating Abilities** matching the same immediate hand/deck cleanup pattern.

The six names are:

| Card | Self-vacating attack | Destination | Printed attack cost | Cleanup optional? | Special constraint |
| --- | --- | --- | --- | --- | --- |
| Dedenne-GX | Tingly Return-GX | Hand | Lightning + Colorless | No | GX attack |
| Eldegoss V | Float Up | Deck | Colorless + Colorless | Yes | none in attack text |
| Kartana-GX | Gale Blade | Deck | Metal + Colorless + Colorless | Yes | none in attack text |
| Liepard V | Shadow Ripper | Hand | Darkness + Colorless + Colorless | Yes | none in attack text |
| Lumineon V | Aqua Return | Deck | Water + Colorless + Colorless | No | none in attack text |
| Meowth ex | Tuck Tail | Hand | 3 Colorless | No | none in attack text |

Eldegoss V appears as two conservative gameplay fingerprints because the bundled print texts differ slightly in wording. This result does not claim those wordings are strategically distinct.

## Structural finding

Only 6 of the 48 literal trigger-Pokémon names have a built-in immediate route to remove themselves from play under this scan, and every one of those routes is an **attack**.

That matters for AMR. A model should not treat built-in cleanup as if it were a free post-trigger action. The cleanup line may require:

- promoting or switching the support Pokémon Active;
- satisfying its attack cost;
- spending the attack for the turn;
- accepting any once-per-game restriction such as a GX attack;
- surviving long enough to execute the cleanup.

The card can therefore be technically self-vacating while the cleanup line is strategically unrealistic in the state being modeled.

## Examples

### Lumineon V

Luminous Sign is a classic transactional Bench-entry Ability. Aqua Return can shuffle Lumineon V and attached cards back into the deck, which can restore the Bench slot and potentially make another Luminous Sign copy or the same copy relevant later.

That lifecycle is real, but Aqua Return is an attack costing Water plus two Colorless Energy. Using it ends the turn. A turn that needs a stronger attack elsewhere may rationally carry the Lumineon V Bench debt instead.

### Eldegoss V

Happy Match retrieves a Supporter from the discard pile when Eldegoss V is played from hand to the Bench. Float Up can optionally shuffle Eldegoss V and attached cards into the deck for two Colorless Energy.

Again, the cleanup is available on card text while remaining action- and attack-gated.

### Dedenne-GX

Dedechange creates the Bench debt immediately after its draw effect. Tingly Return-GX can put Dedenne-GX and attached cards back into hand, but that cleanup consumes the player's GX attack for the game and the attack for that turn. It is therefore a particularly clear example of why technical removability and realistic removability differ.

## Relation to the setup/Bench-trigger results

`results/setup_trigger_role_contention/` shows that a support Basic can be consumed by the mandatory starting Active role before its Bench-entry trigger is ever available.

`results/bench_trigger_access/` shows that a connector reaching the wrong zone can create fictitious trigger access.

This result covers the later lifecycle boundary: even after a correct hand-to-Bench trigger succeeds, the support Pokémon usually remains as persistent board occupancy.

The three stages are therefore distinct:

1. preserve or access a copy in hand;
2. have a Bench slot and perform the correct hand-to-Bench transition;
3. manage the occupied slot afterward.

## Method

The scanner reuses the repository's literal legal Expanded hand-to-Bench trigger catalog. It then examines attacks on those same legal prints for text matching an immediate move of "this Pokémon" into the player's hand or deck.

The result is intentionally conservative and text-structured. It does not attempt to infer multi-card cleanup lines, Knock Out, switching followed by another effect, devolution, or general-purpose pickup cards.

The reproducer asserts the current snapshot counts, the exact six names, representative destinations, the GX classification for Dedenne-GX, and the absence of a matching self-vacating Ability.

## Limits

The absence of a built-in self-vacating attack does not mean a Pokémon is impossible to remove. Expanded contains external pickup, shuffle, switch, Knock Out, and board-manipulation effects.

Likewise, the presence of a self-vacating attack does not mean using it is strategically desirable or even realistically reachable.

This scan does not evaluate:

- Energy acceleration into the cleanup attack;
- retreat or switching access needed to make the support Pokémon Active;
- attack lock;
- Prize tradeoffs;
- opponent gust pressure;
- external removal cards;
- whether replaying the trigger later is allowed or useful;
- whether the cleanup attack itself advances the win condition.

## Next useful work

Bench occupancy should be modeled as a persistent capacity resource with explicit release transitions. A practical state model can assign each support play one Bench slot, then permit release only through typed actions such as a self-vacating attack or an external pickup effect, each with its own timing and resource costs.

This would convert the current static Bench-capacity gate into a lifecycle model capable of reasoning about support chaining, core-board requirements, and the opportunity cost of freeing a slot.
