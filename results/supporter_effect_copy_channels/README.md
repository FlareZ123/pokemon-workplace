# Supporter-effect copying: card identity and execution class diverge

## Question

If an attack says to use the effect of a Supporter card as the effect of that attack, should a simulator treat the resulting body as an ordinary Supporter play?

No. The physical card can be a Supporter while the current execution source is an attack.

Implementation: `tools/supporter_effect_copy_channels.py`  
Regression: `results/supporter_effect_copy_channels/reproduce.py`

## Corpus result

A conservative scan of the bundled effectively legal paper Expanded pool finds **11 print-level effects across 8 card names** matching the direct Supporter-effect-copy grammar.

Seven names are Pokémon whose **attacks** execute the copied effect:

- Liepard;
- Mimikyu;
- Mr. Mime;
- Ninetales;
- Oranguru;
- Smeargle;
- Sylveon.

The eighth name, Sabrina's Suggestion, is itself a Supporter. Its copied body still originates from a Supporter play because Sabrina's Suggestion must first be played as the Supporter action.

This makes the action class a property of the current execution edge, rather than a property inferred from the card whose text supplied the delegated body.

## Concrete Mimikyu witness

Mimikyu `sm12-96` / Impersonation says:

`Discard a Supporter card from your hand. If you do, use the effect of that card as the effect of this attack.`

The selected Supporter therefore moves from hand to discard as part of the attack. Its effect body is delegated to the attack, and the attack ends the turn through the ordinary attack boundary.

The minimal executor preserves the current Supporter-play usage count while consuming the attack action. This allows a state where an ordinary Supporter was already played earlier in the turn to still resolve Impersonation as the later attack, subject to the attack's own legality and cost.

That distinction is a rule/card-text derivation. The card-specific official Q&A cited below independently confirms that Supporter effect semantics are evaluated through this copied attack channel.

## Official Q&A: hand-scoped Supporter modification stops applying

The Japanese official Q&A contains an exact interaction between Mimikyu's Impersonation and Shiftry's Shifty Substitution.

Shifty Substitution says that, while Shiftry is Active, each Supporter card in the opponent's hand has `Draw 3 cards.` instead of its usual effect.

The Q&A asks what happens when the opposing Mimikyu uses Impersonation, discards a Supporter from hand, and then copies it. The ruling says the original Supporter effect can resolve because Shifty Substitution applies to Supporters **in the opponent's hand**. Once the Supporter has been discarded for Impersonation, that hand-scoped replacement no longer determines the copied body.

Official Q&A search:
https://www.pokemon-card.com/rules/faq/search.php?sc_group_id=713

The same official Mimikyu Q&A family also confirms detailed Supporter-body execution through Impersonation, including Guzma & Hala's optional additional discard branch:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%81%AA%E3%82%8A%E3%81%99%E3%81%BE%E3%81%99&regulation_header_search_item1=all

## Mechanical representation

The regression keeps three facts separate:

1. **physical source card**: the discarded card is a Supporter;
2. **execution class**: the copied body is currently an `attack_effect`;
3. **turn budget history**: any Supporter plays already consumed earlier in the turn remain historical facts, while the attack closes the turn.

This avoids two opposite modeling errors.

A simulator that labels the copied body simply `Supporter` can incorrectly try to consume another Supporter quota when Impersonation resolves.

A simulator that forgets the physical card's Supporter identity can fail to enforce Impersonation's selection requirement, fail to move the selected copy from hand to discard, or lose zone-sensitive effects such as the Shiftry interaction.

## Lock implication

Hand-scoped Supporter prohibitions and modifications should test the actual action and zone they name.

For example, an effect that says a player cannot **play Supporter cards from their hand** denies the ordinary play edge. Impersonation instead discards a Supporter and delegates its body to an attack. A planner should therefore avoid applying a play-from-hand gate merely because the delegated text originated on a Supporter card.

This is a card-text and rules-grammar consequence. The official Shiftry Q&A provides a concrete zone-sensitive analogue, while this result does not claim a separate located Q&A for every Supporter-lock card.

## Relation to the action-budget work

The repository already separates:

- effect-based Energy attachment from the ordinary manual attachment;
- Teleport Room Stadium placement from the ordinary Stadium play;
- switching from Retreat;
- direct-to-Bench placement from ordinary hand entry/evolution paths.

Supporter-effect copying shows the same principle in delegated text execution: **effect provenance and action provenance are separate state variables**.

## Limits

The executor deliberately does not implement arbitrary Supporter bodies. It records the exact copied text and provenance so a higher-level effect engine can dispatch the body under the attack execution context.

The corpus grammar is conservative. It captures direct English wording of the form `use the effect of ... Supporter card ... as the effect of this attack/card`. Other cards may interact with Supporters through search, recovery, forced play, text replacement, or more indirect semantics without belonging to this copy family.

The result also does not decide every interaction between copied Supporter bodies and effects that refer to having `played a Supporter card`. Those predicates should remain literal and provenance-aware rather than inferred from the copied body.
