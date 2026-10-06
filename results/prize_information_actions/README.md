# Exact Prize-information acquisition in paper Expanded

## Question

Is the first full deck search the only meaningful transition from uncertain Prize knowledge to exact Prize knowledge?

No. The bundled legal Expanded pool contains two mechanically distinct exact-information mechanisms:

1. inspecting the full remaining deck, then inferring the Prize cards by elimination;
2. directly inspecting or revealing all of the player's remaining Prize cards.

The second mechanism means the K0/K1 abstraction is stronger when K1 is defined by **exact Prize knowledge**, rather than specifically by having searched the deck.

Implementation: `tools/prize_information_actions.py`

Reproducer: `results/prize_information_actions/reproduce.py`

## Rules basis

The Advanced Player's Rulebook states that a player instructed to search their deck looks at its contents while choosing the requested cards. With accurate deck knowledge and visible-zone tracking, that full inspection reveals which cards are absent and therefore in the face-down Prize cards.

The same rulebook states that an attack ends the turn after it is used, Items can generally be played in any number during the player's turn, and only one Supporter may normally be played during the turn. Those action classes therefore place exact information at different points in the decision sequence.

The bundled card text supplies the card-specific effects analyzed below.

## Legality scope and method

The scanner uses the same legality policy as `results/expanded_legality_baseline/`:

- paper Expanded;
- Black & White onward;
- Expanded-legal sets from the bundled snapshot;
- card-level bans;
- the repository's official overlay for the seven 2025-2026 banned prints missing from the bundled database.

The resulting legal population contains 14,836 prints, matching the established legality baseline.

Effects are deduplicated by:

- information mechanism;
- action class;
- card name;
- attack or Ability name;
- normalized effect text.

Counts below are therefore **distinct text variants**, rather than raw print counts.

## Finding 1: 871 full-deck-inspection variants exist

The scanner treats two wordings as full remaining-deck inspection:

- `search your deck`;
- `look through your deck`.

Counts by action class:

| Action class | Distinct full-deck-inspection variants |
| --- | ---: |
| Attack | 568 |
| Ability | 122 |
| Supporter | 89 |
| Item | 87 |
| Pokémon Tool | 3 |
| Energy | 2 |
| **Total** | **871** |

Most are ordinary search effects.

The unusual exception is Porygon `xy7-64`, whose **Data Check** attack reads:

`Look through your deck. Shuffle your deck afterward.`

It retrieves no card. Its immediate material effect is deck inspection and shuffling.

This is a direct counterexample to defining exact Prize knowledge by whether a card was searched out of the deck.

Because Data Check is an attack, the information arrives after the player's main-phase decisions and the attack ends the turn. Its information can guide later turns, while it cannot retroactively improve earlier decisions that turn.

## Finding 2: nine card-text variants inspect all remaining Prizes directly

The scanner found nine distinct legal effects that either:

- say `Look at your face-down Prize cards`; or
- turn all of the player's Prize cards face up.

| Action class | Card | Effect |
| --- | --- | --- |
| Item | Town Map | Turn all of your Prize cards face up |
| Item | Beast Ball | Look at your face-down Prize cards |
| Item | Hisuian Heavy Ball | Look at your face-down Prize cards |
| Supporter | Gladion | Look at your face-down Prize cards |
| Supporter | Daisy's Help | Look at your face-down Prize cards |
| Supporter | Here Comes Team Rocket! | Each player turns all Prize cards face up |
| Attack | Poipole | Eye Opener: look at your face-down Prize cards |
| Attack | Celesteela-GX | Blaster-GX: turn all Prize cards face up |
| Attack | Naganadel & Guzzlord-GX | Chaotic Order-GX: turn all Prize cards face up |

These effects can reveal the exact remaining Prize composition without inspecting the deck at all.

If some Prize cards are already face up or otherwise known, looking at every remaining face-down Prize card still completes the information state.

## Finding 3: exact-information timing depends strongly on action class

The strongest state representation records **when** exact Prize information becomes available.

### Items

Town Map, Beast Ball, and Hisuian Heavy Ball can directly reveal the remaining Prize identities through Item actions.

Under ordinary rules, an Item does not consume the turn's Supporter play. Therefore an exact-information Item can reveal the Prize state before a later Supporter choice, provided the Item is legally playable in the current state.

The same timing advantage applies to ordinary Item deck searches such as Quick Ball and other searchable Items: the deck inspection occurs during the Item resolution, before later main-turn decisions.

### Supporters

Gladion, Daisy's Help, and Here Comes Team Rocket! reveal exact Prize information through a Supporter.

Under the ordinary one-Supporter-per-turn rule, the information arrives only after that turn's Supporter capacity has been consumed.

The information can still guide later Items, Abilities, Energy commitments, Bench decisions, attacks, and future turns.

It normally cannot be used to choose a different Supporter for that same turn.

### Attacks

Poipole's Eye Opener, Celesteela-GX's Blaster-GX, Naganadel & Guzzlord-GX's Chaotic Order-GX, and Porygon's Data Check reveal exact information through attacks.

An attack ends the turn.

These are therefore **late-window information actions**. They can prepare future turns, while current-turn main-phase commitments have already happened.

### Abilities

The 122 full-deck-inspection Ability variants are heterogeneous.

A text-level timing audit classifies them approximately as:

- 104 announced during-turn search Abilities;
- 5 play-from-hand-triggered search Abilities;
- 10 other conditional or triggered search Abilities;
- 3 residual wording cases.

Examples include:

- Tapu Lele-GX's Wonder Tag, a play-from-hand-to-Bench trigger;
- Arceus VSTAR's Starbirth, a during-turn VSTAR Power;
- older once-during-your-turn search Abilities.

Action class alone is insufficient to place every Ability on a timeline. Trigger conditions, Ability lock, Bench requirements, once-per-turn restrictions, and other costs remain part of the state.

### Energy and Pokémon Tools

The two Energy variants and three Pokémon Tool variants acquire information through attached-card effects rather than ordinary Trainer play timing.

Examples include Capture Energy, which searches after being attached from the hand, and Reversal Trigger, which searches when the attached Team Plasma Pokémon is Knocked Out by damage from an opponent's attack.

These effects reinforce that exact Prize information is an event in the game-state timeline rather than a single fixed phase transition.

## Finding 4: partial inspection should remain a separate belief state

The same scan identified 158 distinct partial-information variants under conservative text patterns:

| Mechanism | Action class | Variants |
| --- | --- | ---: |
| Partial deck inspection | Attack | 59 |
| Partial deck inspection | Ability | 37 |
| Partial deck inspection | Item | 33 |
| Partial deck inspection | Supporter | 22 |
| Partial deck inspection | Stadium | 1 |
| Partial Prize inspection | Attack | 5 |
| Partial Prize inspection | Item | 1 |

Examples include effects that look at only the top or bottom portion of the deck, or only one face-down Prize card.

These actions update the player's belief about the Prize state. They do not generally collapse the uncertainty to exact knowledge.

This fits the posterior model in `results/prize_belief_states/`: information is better represented as a spectrum.

## Stronger knowledge-state abstraction

The original human-developed K0/K1 terminology captures an important phenomenon. The card-pool audit suggests a stronger representation.

A game state can track:

- **partial Prize belief**: a posterior over possible Prize compositions given all observations;
- **exact Prize knowledge**: whether the remaining Prize identities are fully known;
- **information acquisition event**: the action and timing that produced the new observation.

Full deck inspection is one route to exact knowledge.

Direct all-Prize inspection is another.

Partial deck or Prize inspection updates the posterior without necessarily making it exact.

This representation preserves the useful strategic distinction while avoiding a dependency on one particular card-action wording.

## Search timing and irreversible commitments

The value-of-information result in `results/prize_information_value/` showed that exact Prize knowledge can change which line should be selected.

The action catalog now provides the timing layer.

For a commitment `C`, ask:

1. Does exact Prize information arrive before `C`?
2. What resource did the information action consume?
3. Does the information action remove or alter any candidate lines?
4. If exact information is unavailable, what posterior should govern `C`?

Examples of commitments include:

- the turn's Supporter choice;
- a unique search connector;
- a Bench slot;
- a discard payload;
- Energy allocation;
- an attack-line choice.

The same information effect can therefore have different strategic value depending on when the decision deadline occurs.

## Validation

The reproducer asserts:

- the legal print count matches the established 14,836-print baseline;
- the 880 exact-information text variants break down into 871 full-deck-inspection and 9 direct-Prize-inspection variants;
- Porygon `xy7-64` Data Check is detected as a full-deck inspection despite containing no `search your deck` wording;
- the nine direct exact-Prize card names match the card-pool audit;
- Tapu Lele-GX Wonder Tag is identified as a play-from-hand-triggered Ability;
- the conservative partial-information counts match the scanner output.

## Limitations

Text-pattern scanning is an auditable cataloging method rather than a complete rules interpreter.

Effects can reveal additional information through unusual wording, opponent actions, deck manipulation, or interactions not captured by the conservative patterns.

Some search effects cannot be legally initiated in every state. The catalog says that resolving the effect provides full-deck inspection. It does not claim that the card can be played solely for information in an arbitrary state.

The scanner also does not assign strategic utilities to information actions. Porygon's Data Check, Town Map, and a productive search Item all have very different opportunity costs even when each can produce exact Prize knowledge.

## Next useful work

The next model should treat exact-information acquisition as a timestamped state transition inside the typed access network.

Each transition should record:

- information gained;
- action class;
- Supporter capacity consumed;
- Bench or Active requirements;
- discard or attachment costs;
- whether the action ends the turn;
- one-per-game powers such as GX attacks or VSTAR Powers;
- which strategic choices remain available after the transition.

That would allow a planner to compare the value of acquiring information now against delaying it or committing to a line under uncertainty.
