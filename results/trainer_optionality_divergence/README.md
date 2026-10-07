# Historical Trainer optionality divergences

## Question

Can a historical mandatory choice and a current optional choice produce different reachable game states even when the surrounding search effect looks nearly identical?

## Result

Yes. Three same-name Trainer families produce a direct material-transition divergence across six historical prints:

| Name | Historical prints | Historical wording | Current wording |
| --- | ---: | --- | --- |
| PokéNav | 3 | choose an eligible Pokémon or Energy | you may reveal an eligible Pokémon or Energy |
| Pokégear 3.0 | 1 | choose a Supporter | you may reveal a Supporter |
| Dusk Ball | 2 | choose 1 Pokémon | you may reveal a Pokémon |

Under the current Advanced Player's Rulebook, a specified `choose` count is mandatory when eligible objects exist. `You may` makes the described action optional.

A state with an eligible card in the inspected window therefore distinguishes each pair. The current card can decline to move the eligible card into hand. The historical wording requires a choice.

All six historical source prints are promoted to the resolver's `known_non_equivalent` evidence set.

## Concrete witnesses

### PokéNav

Put an eligible Pokémon or Energy among the top three cards. Current PokéNav can decline to take a card and return the inspected cards in an allowed order. Historical PokéNav requires choosing an eligible card and moving it to hand.

### Pokégear 3.0

Put a Supporter among the top seven cards. Current Pokégear 3.0 can decline to take it and shuffle the inspected cards back. Historical Pokégear 3.0 requires choosing a Supporter when one is available.

### Dusk Ball

Put a Pokémon among the bottom seven cards. Current Dusk Ball can decline to take it. Historical Dusk Ball requires choosing one when available.

## Rules basis

The repository Advanced Player's Rulebook defines `Choose` as selecting the specified number. When a number is specified, the player may not voluntarily choose fewer available objects. The same rulebook defines `You may` effects as optional.

The proof depends on those current rules semantics rather than on punctuation or edit distance.

## Tooling

`tools/trainer_optionality_divergence.py` stores the three audited cases and validates:

1. source and target print identity;
2. direct target legality in Expanded;
3. the historical mandatory-choice text fragment;
4. the current optional-choice text fragment.

The collector returns the six source IDs as explicit negative evidence.

## Evidence classes

**Current rule fact.** Mandatory `choose` and optional `you may` have different action semantics.

**Card-text fact.** The bundled historical and current print records preserve the relevant wording difference for all six source prints.

**State-model proof.** An eligible card in the inspected window creates a reachable state where the current effect can leave hand size unchanged and the historical effect cannot.

## Reproduction

Run `python -m results.trainer_optionality_divergence.reproduce`.

The regression validates all three families and cross-checks the six source IDs against the reprint resolver.

## Limitations

This result covers only the exact mandatory-versus-optional wording family represented by these three Trainers. It does not infer optionality from looser natural-language similarity.

## Next work

Several remaining historical Trainer pairs appear plausibly equivalent after current rules normalization, including VS Seeker, Lure Ball, Moomoo Milk, Maintenance, and Pokémon Communication. Those should be tested with positive semantic proofs rather than assumed equivalent from surface similarity.
