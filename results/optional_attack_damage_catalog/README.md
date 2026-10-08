# Exact optional damage boosts in the legal English Expanded card corpus

## Question

How common is the specific card-text form that creates an optional higher-damage
branch, and how often does a "more damage" choice consume a separate resource?

The reusable inventory is `tools/optional_attack_damage_catalog.py`.
The regression is `results/optional_attack_damage_catalog/reproduce.py`.

## Scope and method

The parser scans sets whose metadata lists Expanded legality and cards with
effective legal status under the repository's ban overlay. It selects attacks
whose printed damage is `N+` and whose text matches the deliberately narrow
form:

`You may [resource action]. If you do, this attack does N more damage ...`

The phrase must begin the attack text. This excludes forced effects,
opponent-controlled bonuses such as Shiftry's Whisk Away, other conditional
damage modifiers, and historical prints in sets that are not marked Expanded
legal. It is a **conservative family catalog** rather than a complete catalog
of optional damage across all Pokémon cards.

## Result

The snapshot exposes **71 legal print-level attack entries** spanning
**39 distinct card/attack/text signatures** and **37 distinct Pokémon
names**.

Ten print entries representing three signatures have variable boosts that
depend on how many cards were discarded: Ice Rider Calyrex VMAX's
Max Lance, Rillaboom VMAX's Max Beating, and M Camerupt-EX's
Magma Eruption. A generic optimizer must not apply the printed increment once
to those branches.

Cetitan ex is the clean fixed-bonus, Stadium-discard witness. Its two eligible
English prints are `sv10-65` and `sv10-210`, both using a 140 base and
optional +140. Roaring Moon ex's Calamity Storm has six legal prints in this
snapshot, all with 100 base and optional +120 from a Stadium discard.

## Strategic implication

The optional branch changes both the damage outcome and resource state.
Resource actions include discarding attached Energy, discarding a Tool,
discarding from hand, discarding Stadiums, returning Energy to hand,
turning a Prize face up, and discarding the top of a deck.

For a defender with Strong Bash-like damage reflection, additional damage may
directly lower the attacking Pokémon's chance of surviving even when both
choices already Knock Out the defender. The exact realized example is recorded
in [optional_overkill_reflection/](../optional_overkill_reflection/).

## Limitations

The corpus is the bundled English data snapshot, with region-specific
legality limitations recorded in `resources/INDEX.md`. Printed cost
descriptions are classified into coarse families. No claim is made that the
resource action is realistically payable in any given board state, that the
defending Pokémon's reaction is enabled, or that a target is within KO range.
Live simulations must incorporate those details.
