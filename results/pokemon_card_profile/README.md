# Card-grounded Pokemon combat profiles

## Question

Can physical board objects derive printed HP, type, Weakness, Resistance, and base Prize value from their exact print identity instead of receiving parallel hand-authored maps?

Yes, for effectively legal paper-Expanded Pokemon in the bundled snapshot.

Implementation: `tools/pokemon_card_profile.py`  
Regression: `results/pokemon_card_profile/reproduce.py`

## Representation

`PokemonCardProfile` stores:

- exact print ID and name;
- printed HP;
- Pokemon types;
- typed Weakness modifiers;
- typed Resistance modifiers;
- printed base Prize value inferred from the card's rule text.

Weakness and Resistance use the modifier parser from `results/type_modifier_catalog/`, so legacy additive Weakness remains representable.

The profile compiler applies `combat_data_overrides` before parsing. This means the audited Murkrow `me55-93` Resistance correction is visible to downstream mechanics without changing the raw card database.

## Coverage

The current effectively legal English paper-Expanded snapshot yields 12,504 Pokemon card profiles with parseable HP.

Regression witnesses include:

- Dragapult ex `sv6-130`: 320 HP, Dragon, two Prizes;
- Dialga-GX `sm5-100`: 180 HP, Dragon, two Prizes, Fairy x2 Weakness;
- Flying Pikachu VMAX `cel25-7`: 310 HP, three Prizes, Fighting -30 Resistance;
- Uxie `me55c-43`: preserved Psychic +20 Weakness;
- Murkrow `me55-93`: audited Fighting -30 Resistance after the override layer.

## Board bridge

`hp_by_board_object(...)` maps each `BoardPokemon.object_id` to printed HP using `BoardPokemon.print_id`.

This removes one parallel source of truth from damage and KO evaluation. A board with exact print identity already contains enough information to recover printed HP.

The helper deliberately rejects objects lacking a print ID or profiles absent from the legal index. Silent name-based fallback would be unsafe because same-name prints can have different HP, types, attacks, Abilities, or Prize rules.

## Remaining state

A printed profile is a starting point rather than the whole live combat state.

Effects can modify HP, remove Weakness or Resistance, change type, change Prize awards, suppress Abilities, or alter damage. Those effects should be represented as explicit live-state layers above this immutable print profile.

The next useful integration is to derive the step-3 and step-4 damage modifiers from attacker type plus the target's current effective Weakness/Resistance state.
