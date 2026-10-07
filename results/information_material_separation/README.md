# Exact information access and material line access are separate resources

## Question

Does acquiring exact Prize information imply that the card-access line which produced that information also succeeds?

No. A full deck inspection can establish exact Prize composition even when the intended material connector chain fails, arrives too late, or consumes the action window needed for the target.

This result connects the Prize-information work to the repository's typed access and supporter-temporality results.

Reproducer: `results/information_material_separation/reproduce.py`

## Case 1: Nest Ball -> Tapu Lele-GX acquires exact Prize information while Wonder Tag fails

Nest Ball searches the deck for a Basic Pokémon and puts that Pokémon directly onto the Bench.

The search itself exposes the remaining deck contents to the player, so it can establish exact Prize composition by elimination.

Tapu Lele-GX's Wonder Tag requires:

`When you play this Pokémon from your hand onto your Bench...`

A Tapu Lele-GX put directly onto the Bench from the deck by Nest Ball does not satisfy that play-from-hand trigger.

The repository's typed access result already treats the Nest Ball -> Tapu Lele-GX -> Wonder Tag material route as invalid.

The information route behaves differently:

`Nest Ball full deck inspection -> exact Prize composition`

succeeds before the attempted Wonder Tag step.

This is a clean counterexample to any model that attaches Prize information only to successful search chains.

## Case 2: Quick Ball -> Tapu Lele-GX makes Wonder Tag's Prize information redundant

Quick Ball searches the deck for a Basic Pokémon and puts it into the hand.

If Tapu Lele-GX is then played from the hand onto the Bench, Wonder Tag can trigger and search the deck for a Supporter.

The typed material route can therefore reach a Supporter such as Gladion, subject to the ordinary costs and board requirements.

For Prize composition, the first Quick Ball search already inspected the deck.

Wonder Tag's later search can have large material value while adding no new exact Prize-composition information if the deck and Prize zones have not changed in a knowledge-destroying way between those actions.

This creates **information redundancy along a connector path**.

An action can be essential materially while informationally redundant.

## Case 3: Skyla gives exact Prize information after spending the Supporter window

Skyla is a Supporter that searches the deck for a Trainer card.

Playing Skyla therefore provides full deck inspection and can establish exact Prize composition.

Skyla also consumes the ordinary one-Supporter-per-turn capacity.

If the newly learned Prize state implies that Gladion would have been the ideal Supporter for the same turn, that information arrived after the Supporter commitment deadline.

Exact information exists, while the corresponding current-turn rescue action is no longer available through the ordinary Supporter window.

The value of that information shifts to later decisions and later turns.

## Case 4: Jigglypuff's Lead gives exact information after the main phase

Jigglypuff's Lead attack searches the deck for a Supporter card.

The search gives full deck inspection.

Using an attack ends the turn.

Therefore Lead can establish exact Prize composition and put a Supporter into hand, while the searched Supporter cannot be played during that same turn.

This matches the repository's supporter-temporality distinction between current-window and future-window access.

## Four independent questions for a search action

A planner should ask separately:

1. **Information:** does this action reveal the full deck or full Prize set?
2. **Material output:** what card or board object does the action produce?
3. **Timing:** which decisions remain after the information arrives?
4. **Capacity cost:** which once-per-turn, Supporter, attack, Bench, discard, or other resource did the action consume?

One edge can score differently on all four dimensions.

## Connector domination gains an information dimension

The human-developed connector-domination concept warns that a search path can consume the connector required for a stronger line.

Information adds another comparison.

Suppose two paths use the same connector:

- one produces a strong material target and exact information;
- another produces weaker material access but the same exact information.

The second path should receive no extra reward for "also revealing the deck" if the first path already provides the same information before the same decision deadline.

Conversely, an early low-material search can still have value if it moves exact information before a critical commitment that the stronger material path reaches only afterward.

This suggests deduplicating information gain along paths by information state and deadline, rather than rewarding every search edge independently.

## State-transition representation

A useful transition can carry fields such as:

- material zone changes;
- exact or partial Prize belief update;
- information recipient;
- Supporter capacity consumed;
- attack window consumed;
- Bench capacity consumed;
- discard cost;
- turn-ending flag;
- trigger provenance such as play-from-hand.

Then a path planner can compare complete resulting states.

The Nest Ball example would produce:

- exact Prize information;
- Tapu Lele-GX on the Bench;
- no Wonder Tag trigger.

The Quick Ball route can produce:

- exact Prize information;
- Tapu Lele-GX in hand;
- later play-from-hand trigger;
- a discard cost already paid.

The states are strategically different despite both containing a full-deck search.

## Validation

The reproducer audits the legal card text and asserts:

- Nest Ball is an Item full-deck search that puts the Basic directly onto the Bench;
- Quick Ball is an Item full-deck search that puts the Basic into hand;
- Tapu Lele-GX Wonder Tag is a play-from-hand-to-Bench triggered Ability;
- Skyla is a Supporter full-deck search;
- Jigglypuff Lead is an attack full-deck search for a Supporter.

The material route conclusions are consistent with the already preserved typed-access and supporter-temporality research.

## Limitations

This result does not reimplement the full typed state engine.

It assumes the existing rules interpretation for play-from-hand triggers, Supporter capacity, and attack timing.

A full integration still has to model Item lock, Ability lock, discard realism, Bench space, and concrete card accessibility.

## Next useful work

The strongest integration is to annotate typed-access transitions with Prize-belief updates.

The search engine should retain one shared information state as it traverses a path.

Repeated full-deck searches with no intervening hidden-state mutation should then add zero new exact-composition information, while still producing their material outputs.

A hidden Prize mutation can make a later search informative again, as shown in the non-monotonic knowledge result.
