# Attack-copy semantics and nested selection in paper Expanded

## Question

How should an Expanded simulator or strategy model represent attacks whose text says to use another attack "as this attack", especially when one copied attack can itself select and execute another attack?

## Answer

The current Advanced Player's Rulebook gives a clean two-layer interpretation:

1. An attack that says to use another attack "as this attack" executes the chosen attack's effects and damage.
2. The outer attack keeps its own attack name while those copied effects are executed.

This means nested copy effects should be modeled as nested execution, not as a one-time replacement of the outer attack object. Selection restrictions belong to the copy edge that states them. If a selected attack contains its own copy instruction, that instruction creates a new selection edge with its own restrictions.

This result calls that property **edge-local copy restrictions**.

Implementation: `tools/attack_copy_catalog.py`

Regression: `results/attack_copy_semantics/reproduce.py`

Card-pool catalog: `results/attack_copy_semantics/catalog.json`

## Rules basis

The Advanced Player's Rulebook section C-18 defines "use it as this attack" as choosing another attack and doing all of its effects and damage. Unless the copying text says otherwise, the copying Pokémon does not need the Energy required by the chosen attack.

The same section gives a Foul Play example that is especially important for state representation. Zoroark can use the effects and damage of Mega Brave, but the attack name remains **Foul Play**. The copied Mega Brave effect that restricts Mega Brave next turn still applies, yet Zoroark may use Foul Play again because it did not rename the attack to Mega Brave.

Section D-06 separately distinguishes attacks written on a Pokémon's card from attacks that Pokémon can use through other effects. Together, these rules require a simulator to keep attack identity separate from the currently executing copied attack body.

## Computational card-pool inventory

The catalog scans the repository's current paper Expanded card pool and applies the same current-ban overlay used by `tools/build_expanded_legality_baseline.py`.

For the bundled snapshot it finds:

- **14,836** effectively legal print records scanned;
- **64** legal print records with attack text containing "as this attack";
- **30** distinct `(attack name, attack text)` copy-attack signatures;
- **30** distinct Pokémon names carrying those signatures;
- **3** signatures with an immediate non-GX selection restriction;
- **25** signatures whose source class can statically re-enter the same copy-attack family in some legal state.

The 25-count is a structural hazard flag. It does not mean those attacks force an infinite loop in actual play. State, source-zone membership, opponent choices, optional wording, and other restrictions can stop or avoid recursion.

The 30 signatures span several source geometries, including opponent Active attacks, opponent last attack, Pokémon in either player's in-play zones, the opponent's hand or deck, the user's Bench, previous Evolutions, a Dragon Pokémon in the user's discard pile, and a Fusion Strike Pokémon on the user's Bench.

## Edge-local copy restrictions

Consider three attacks in the current legal card pool:

- Mimikyu `smp-SM99`, **Copycat**: if the opponent's Pokémon used an attack that is not a GX attack during their last turn, use it as this attack.
- Regidrago VSTAR `swsh12-136`, **Apex Dragon**: choose an attack from a Dragon Pokémon in your discard pile and use it as this attack.
- Dialga-GX `sm5-100`, **Timeless-GX**: take another turn after this one, with the card's once-per-game GX restriction.

The direct Copycat selection checks the opponent's last attack. If that attack is Apex Dragon, the non-GX condition passes because Apex Dragon itself is not a GX attack. Once Copycat begins executing Apex Dragon's effects, Apex Dragon performs its own selection from a Dragon Pokémon in the Copycat user's discard pile. Apex Dragon does not contain a non-GX restriction, so its inner selection can choose Timeless-GX from Dialga-GX if Dialga-GX is an eligible Dragon Pokémon in that discard pile.

The outer non-GX filter therefore does not propagate into the inner Apex Dragon selection. It was already satisfied at the Copycat-to-Apex-Dragon edge.

This is a rules-derived inference from C-18's instruction to execute all effects of the selected attack and from the Foul Play example preserving the outer attack's identity. It is also consistent with the current card texts and with official Expanded guidance that explicitly presents Apex Dragon copying Dialga-GX's Timeless-GX as a legal use of Regidrago VSTAR.

## Validation of the Mimikyu counter-line

The catalog performs the static card-text checks for the three-card chain and they all pass:

- Apex Dragon is a non-GX attack, satisfying Copycat's immediate filter;
- Dialga-GX is a Dragon Pokémon, satisfying Apex Dragon's source-type filter;
- Apex Dragon itself has no immediate non-GX filter on the attack it selects.

A game-state evaluator must still verify the dynamic conditions: the opponent actually used Apex Dragon during their last turn, Mimikyu can use Copycat, an eligible Dialga-GX is in the Mimikyu player's discard pile, and the once-per-game GX use is still available. Other board-state effects may also matter.

This validates the strategic mechanism described in the human-developed ALS notes while keeping the evidence types separate: card texts and rulebook semantics establish the mechanism, the catalog verifies the current card pool, and matchup value remains a strategic question.

## Why attack identity and attack body must be separate

A naive simulator might represent copying as:

`current_attack = selected_attack`

That loses information. It can incorrectly apply name-based restrictions, misclassify what the opponent used on the previous turn, or propagate source restrictions farther than the card text says.

A stronger representation keeps at least:

- **declared attack identity**: the attack actually announced by the attacking Pokémon;
- **executing attack body**: the damage and effects currently being resolved;
- **copy stack**: the ordered chain of copied attack bodies;
- **selection edge**: the source zone, eligibility predicate, and chooser for each copy instruction;
- **global use constraints**: once-per-game or other resources that remain relevant to the selected endpoint;
- **current actor state**: the attacking Pokémon and current player's zones used to interpret words such as "this Pokémon" and "your discard pile".

This separation also matches the rulebook's Foul Play example, where the copied body can create effects on the attacker while the attack name remains Foul Play.

## Structural re-entry hazards

The catalog marks a signature when its static source geometry can contain another legal instance of the same copy-attack family. Examples include:

- **Apex Dragon** selecting an attack from another Regidrago VSTAR in the user's discard pile, because Regidrago VSTAR is a Dragon Pokémon;
- **Cross Fusion Strike** selecting a Fusion Strike Pokémon on the Bench, a class that can include another Mew VMAX with Cross Fusion Strike;
- broad opponent-Active copy attacks selecting another copy attack in a mirror or compatible board state;
- opponent-last-attack copy effects reusing a previous copy attack.

These findings matter mainly for implementation safety. A recursive evaluator should carry a copy-resolution stack or another cycle-aware state representation. It should not blindly expand copy targets as an unrestricted graph traversal.

The current Advanced Player's Rulebook supplied with the repository does not establish a complete tournament procedure for every possible recursive copy cycle. This result therefore stops at identifying the structural hazards and the state representation needed to model them safely.

## Method

`attack_copy_catalog.py`:

1. loads the bundled English set and card JSON;
2. keeps sets marked Expanded-legal;
3. applies the repository's current print-level ban overlay;
4. scans legal attacks for the phrase "as this attack";
5. normalizes them into distinct attack-text signatures;
6. classifies the immediate attack source named by each text;
7. flags immediate non-GX filters and optional selections;
8. applies a conservative structural re-entry heuristic;
9. performs exact card-text checks for the Mimikyu -> Apex Dragon -> Timeless-GX chain.

The scan is deterministic for a fixed repository snapshot.

## Limitations

The catalog is a targeted text parser rather than a complete Pokémon TCG rules engine. Source classification is based on the wording present in the current snapshot and should be extended when new copy wording appears.

`structural_same_attack_reentry` answers only whether the source class can contain another attack from the same family under some state. It does not prove that the state is strategically realistic, that the choice is mandatory, or that a tournament loop occurs.

The scan also focuses on attack text containing the phrase "as this attack". Other mechanics that grant attacks, refer to previous Evolutions, or modify attacks without that phrase can interact with the same state model and may deserve separate treatment.

## Next useful work

A high-value extension is a general copy-resolution kernel. It should execute nested copy edges against a typed game state, preserve declared attack identity, apply endpoint-wide resources such as GX use, and terminate safely on repeated state-copy configurations. That kernel can then be integrated with the repository's existing typed access and lock-state work.
