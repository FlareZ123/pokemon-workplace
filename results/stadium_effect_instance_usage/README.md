# Stadium effect usage is per in-play instance

## Question

If a player uses a Stadium effect that says “once during each player's turn,” then removes that Stadium and plays another copy with the same name, is the second copy's effect already spent?

No. An official Brooklet Hill ruling explicitly permits the second copy's effect.

Implementation: `tools/stadium_effect_instance_usage.py`  
Regression: `results/stadium_effect_instance_usage/reproduce.py`

## Concrete legal Expanded witness

Brooklet Hill `sm2-120` is legal in the bundled Expanded pool. Its effect begins:

`Once during each player's turn, that player may...`

The official Japanese Q&A asks about this sequence:

1. use the Brooklet Hill already in play;
2. use Field Blower to discard it;
3. play Brooklet Hill from hand;
4. use Brooklet Hill's effect again that same turn.

The ruling says **yes**.

Official Q&A:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%81%9B%E3%81%9B%E3%82%89%E3%81%8E%E3%81%AE%E4%B8%98&regulation_faq_main_item1=all

Older official Speed Stadium and Pokémon Pal City rulings give the same shape: after the used Stadium leaves play and another copy is played, the new in-play Stadium can use its effect.

## State model

The model distinguishes:

- physical Stadium card identity;
- current in-play Stadium instance identity;
- ordinary Stadium-play quota;
- per-instance voluntary effect-use history.

`use_current_stadium_effect()` marks the current `instance_id`, rather than the Stadium name.

`discard_current_stadium()` can remove that used instance without affecting the ordinary Stadium-play quota.

`play_stadium_from_hand()` consumes the ordinary Stadium-play action and creates a new in-play instance for the selected physical card.

The regression executes the official shape with two physical Brooklet Hill copies:

`Brooklet A effect -> Field Blower removal -> play Brooklet B -> Brooklet B effect`

The first effect use does not globally mark the name “Brooklet Hill” as spent.

## Why name-level usage is wrong

A state such as:

`used_stadium_effect_names = {"Brooklet Hill"}`

would reject the official line after the second Brooklet Hill enters play.

A state tied only to physical card identity is also more specific than the evidence supports. The ruling proves fresh use for a new copy. Other game mechanics can move the same physical card out of play and later return it, which raises a separate incarnation question.

For this reason the model explicitly stores an **in-play instance ID** in addition to the physical copy ID.

## Interaction with Stadium entry channels

This result is orthogonal to `stadium_entry_channels/`.

That result answers how a Stadium enters play and whether `TurnAction.STADIUM_PLAY` is consumed. This result answers whether the current in-play Stadium instance's voluntary effect has already been used.

A composed planner therefore needs both axes.

Teleport Room can create additional Stadium instances through effect placement without consuming the ordinary Stadium-play quota. Whether an entering Stadium's voluntary effect is fresh should be determined by the in-play-instance lifecycle rather than by Stadium name alone.

## Limits

The official Brooklet Hill ruling uses a **different physical copy** of the same Stadium name. This result does not claim that the same physical Stadium card, after leaving play and later returning in the same turn, necessarily receives a fresh instance-use allowance without a card-specific or general object-identity ruling.

The `instance_id` is caller-supplied for that reason. A higher-level zone/object lifecycle should decide when a new in-play instance is created.

The model covers voluntary Stadium effects with once-per-turn-style use history. Continuous Stadium effects have no analogous activation-use counter.
