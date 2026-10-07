# Optional selection in attack-copy effects

## Question

What happens when a copy attack says the player **may** choose or discard a source before using one of its attacks?

Declining the optional branch is a valid resolution of the declared attack. Any mandatory outer continuation still occurs, and no selected body or source mutation is fabricated.

Implementation: `tools/attack_copy_kernel.py`  
Regression: `results/attack_copy_optional_selection/reproduce.py`

## Current legal witnesses

The catalog contains two optional copy signatures:

- **Haughty Order**: reveal the top 10 cards of the opponent's deck, optionally choose an attack from a Pokémon found there and use it, then shuffle the revealed cards back.
- **Hypnotic Reign**: reveal the opponent's hand, optionally discard a Pokémon found there and use one of that Pokémon's non-GX attacks.

These attacks cannot be represented as "a copy target must exist and must be chosen."

## Kernel change

`CopySelector.optional_selection` now distinguishes optional copy branches.

A choice policy may return `None`. For an optional selector this records a trace step with no selected attack and `selected_body_executed=False`.

If an optional selector has no legal candidates at all, resolution likewise continues without raising target illegality.

Mandatory outer text still resolves.

## Regressions

For Haughty Order:

- with an eligible revealed Pokémon, the player may decline;
- with no eligible target, the attack still completes;
- in both cases the reveal event is followed by the mandatory shuffle cleanup.

For Hypnotic Reign:

- the player may decline even when an eligible hand Pokémon exists;
- the source Pokémon remains in hand because the optional discard-and-copy branch was not taken.

## Architectural implication

Copy target existence, branch choice, and body execution are separate decisions.

This distinction matters for simulation because an optional copy branch can be strategically dominated, harmful, or irrelevant. A policy should be allowed to decline it without treating the whole attack as illegal.

It also matters for cleanup: outer mandatory text can survive a skipped inner branch.

## Limitations

The current trace uses `selected_body_executed=False` for both a declined optional branch and a selected body suppressed by an Energy gate. The selected attack ID distinguishes the latter today. A future richer trace may encode explicit branch outcomes.
