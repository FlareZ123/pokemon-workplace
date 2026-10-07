# Prize-destination replacement applicability across Knock Out

## Question

When Lost Block and Billowing Smoke can redirect an opponent's taken Prize cards, which replacement effects are still applicable at the Prize-taking boundary?

They have different lifetimes. Lost Block is a continuous Ability and requires a surviving, enabled Barbaracle after Knock Out disposal. Billowing Smoke is captured from the Knocked Out holder when its Tool effect was live and the Knock Out came from opponent attack damage.

Implementation: `tools/prize_destination_applicability.py`  
Regression: `results/prize_destination_applicability/reproduce.py`

## Official boundary

The Japanese Pokémon Card Trainers Website answers the exact Lost Block self-KO case: if the Barbaracle with Lost Block is itself Knocked Out by the opponent's attack, Lost Block cannot redirect the opponent's Prize because Barbaracle leaves play before the opponent takes it.

Source:

- https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%AF%E3%82%B6%E3%81%AE%E5%8A%B9%E6%9E%9C&page=52&regulation=all&regulation_header_search_item1=all

The same source gives the exact Lost Block plus Billowing Smoke ordering interaction when a separate Lost Block source survives.

## Derived state rule

For an opponent's Prize award from a Knock Out:

- inspect the defender's board **after** KO disposal for live Lost Block sources;
- inspect the removed Pokémon's captured Tool state for Billowing Smoke;
- require Billowing Smoke's Tool effect to have been live at the KO trigger;
- require the KO to have been caused by damage from an opponent's attack.

This separates a continuous source that must survive from an event-triggered replacement whose source can leave play before the later Prize movement.

## Regression

The regression proves four boundaries:

1. surviving Barbaracle plus live Billowing Smoke produces both replacement candidates;
2. Barbaracle itself Knocked Out with Billowing Smoke produces only the Smoke replacement;
3. suppressed Lost Block produces only Smoke;
4. blanked Smoke or a non-attack-damage KO does not produce the Smoke replacement.

The derived candidates feed directly into `prize_destination_overrides.py`, where the official chooser rule can resolve any remaining multi-zone choice.

## Architectural implication

Effect applicability cannot be inferred only from the board snapshot at one arbitrary time. Continuous effects and triggered effects can cross the same event boundary differently.

A simulator should preserve the post-disposal board for continuous effects and the relevant pre-disposal trigger snapshot for effects such as Billowing Smoke. This temporal split is required before replacement ordering is even considered.
