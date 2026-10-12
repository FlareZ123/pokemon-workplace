# Pokémon V-UNION is Pokémon V only when assembled in play

## Verified rules correction

The Pokémon Trading Card Game Rules, **Appendix 7: Pokémon V-UNION**,
explicitly state that a complete, assembled Pokémon V-UNION in play
counts as both **Pokémon V** and **a Pokémon with a Rule Box**. It has
its own Stage, V-UNION. It is neither Basic nor an Evolution card.
Individual out-of-play V-UNION pieces do not carry the same Rule Box
characteristic.

Sources:

- Official full rules PDF, Appendix 7, printed p. 26:
  https://assets.pokemon.com/assets/cms2-sv-se/pdf/trading-card-game/rulebook/par_rulebook_en.pdf
- Official V-UNION introduction:
  https://www.pokemon.com/us/news/pokemon-v-union-arrive-in-the-pokemon-tcg

The prior shared Retreat class classifier
`tools/retreat_dynamic_energy_units.py` contained Basic V, VMAX
and VSTAR tags but omitted V-UNION tags. It could therefore misidentify
an assembled V-UNION in other represented mechanics as neither a
Pokémon V nor a Pokémon with a Rule Box.

The exact correction adds all three modeled tags, `V-UNION`,
`Pokemon V-UNION`, and `Pokémon V-UNION`, to the **in-play**
`_POKEMON_V_TAGS` category. The existing derived
`_RULE_BOX_TAGS` includes these automatically. The same code
continues to treat V-UNION as neither Stage 1/Stage 2 nor Evolution.

## Two card-dependent consequences

1. **Wimpod, Punk Out (`pgo-25`).** Wimpod has no Retreat Cost if
   the opponent has a Pokémon V in play. An assembled opposing Mewtwo
   V-UNION therefore turns the Ability on. In the representative
   Galar Mine environment (+2 Retreat), the no-cost effect wins by
   the rulebook's D-13 priority. Before the correction, this
   V-UNION-only opposing state was incorrectly invisible.
2. **Twin Energy (`swsh2-174`).** This Special Energy provides two
   Colorless Energy to most holders but only one to Pokémon V or
   Pokémon-GX. An assembled V-UNION must receive the restricted
   one-Energy mode. Before the correction, this model returned two.

These are deterministic mechanical source effects. The first is an
exact matchup-state Retreat cost; the second changes actual attached
Energy-provider count and therefore potential Retreat-payment
feasibility.

## Reproduction

The machine-readable English snapshot contains 24 V-UNION component
prints across five Pokémon names, with the `V-UNION` subtype.
`reproduce.py` audits the exact `swshp-SWSH159` Mewtwo V-UNION
component and total corpus, tests three accepted tag spellings,
verifies both the Pokémon V and Rule Box flags, confirms the
non-Evolution classification, and asserts the two source-specific
consequences against live board input. A generic Basic Pokémon and
GX-only opponent are negative controls.

The dedicated validation workflow reruns previous dynamic Special
Energy provider and conditional free-Retreat regressions.
[CI run 38280115891 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38280115891).

**Boundary:** the fixture represents a properly assembled
in-play V-UNION as one board object. It does not implement
the four-component assembly procedure or promote this in-play
classification to individual pieces in hand, deck, discard or Prizes.
Card effects referring specifically to one V-UNION piece outside
play require a separate zone-sensitive representation.

There is no direct inference about deck strength, game wins or whether
any V-UNION is worth including in a competitive 60-card list.
