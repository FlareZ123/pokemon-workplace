# Prize information has publicity and visibility side effects

## Question

Can an exact Prize-information action be modeled only as a change in the player's knowledge?

No. Some effects make Prize identities public and persistent on the board. Turning Prizes face up can also alter later cards whose text specifically requires face-down Prize cards.

Implementation: `tools/prize_visibility_interactions.py`

Reproducer: `results/prize_visibility_interactions/reproduce.py`

## Direct exact-Prize effects split into public and private modes

The exact-information catalog contains nine distinct legal text variants that directly reveal the complete remaining Prize composition.

Four turn all Prize cards face up:

- Town Map;
- Celesteela-GX's Blaster-GX;
- Naganadel & Guzzlord-GX's Chaotic Order-GX;
- Here Comes Team Rocket!

Those identities remain visible on the board according to their card text.

Five let the player look at all face-down Prize cards without globally turning the set face up:

- Gladion;
- Beast Ball;
- Poipole's Eye Opener;
- Daisy's Help;
- Hisuian Heavy Ball.

The second group can reveal selected cards through later parts of their effects, but the complete Prize composition is not made persistently face up.

This creates an information-ownership distinction.

A private inspection improves the player's information set.

A face-up effect also improves the opponent's information set about those Prizes.

## Full deck inspection is another private-information route

The Advanced Player's Rulebook states that while searching the deck, its contents are visible to the searching player and not to the opponent.

A skilled player can infer the Prize composition from that private deck inspection.

The searched card itself may be revealed when the card text says to reveal it. The inferred full Prize composition does not automatically become public.

This makes ordinary deck search strategically different from Town Map even when both produce exact Prize knowledge for the player.

## Finding: 12 legal effect variants explicitly require the player's face-down Prizes

The legal card scan finds 12 distinct effect variants containing the phrase:

`your face-down Prize cards`

They are:

| Action class | Card / effect |
| --- | --- |
| Ability | Mr. Mime / Pantomime |
| Attack | Chinchou / Searching Light |
| Attack | Blacephalon / Blazer |
| Supporter | Gladion |
| Item | Beast Ball |
| Attack | Poipole / Eye Opener |
| Supporter | Daisy's Help |
| Attack | Cresselia / Crescent Purge |
| Item | Hisuian Heavy Ball |
| Item | Arc Phone |
| Attack | Patrat / Safety Check |
| Attack | Umbreon / Lunatic Sense |

Town Map's text turns **all** of the player's Prize cards face up for the rest of the game.

After that state change, these effects no longer have the same set of face-down Prize targets.

The exact consequence depends on the full card text.

Examples:

- Gladion's intended Prize retrieval requires choosing from the face-down Prize cards.
- Beast Ball and Hisuian Heavy Ball search among face-down Prize cards.
- Arc Phone switches with a face-down Prize card.
- Mr. Mime's Pantomime switches a face-down Prize with the top deck card.
- one-Prize inspection attacks lose their hidden Prize target when every Prize is already face up.
- attacks whose bonus requires turning one face-down Prize face up can lose that conditional action.

This is a structural interaction between information and future move availability.

## Information can remove graph edges

A naive information model might represent Town Map as:

`unknown Prizes -> exact Prizes`

The card text creates a richer transition:

`face-down unknown Prizes -> face-up exact Prizes`

The visibility state is mechanically relevant.

Cards that require a face-down Prize target can have their action edges removed or altered after Town Map.

Therefore, an optimizer should not assign information as a detached scalar bonus while leaving the rest of the action graph unchanged.

The information-producing action can mutate the same state variables that determine future legal or useful moves.

## Public information can help the opponent

Face-up Prize cards reveal information to both players.

That can affect opposing decisions such as:

- which line to pursue;
- which resources can safely be assumed unavailable;
- whether a specific singleton is trapped;
- how aggressively to commit to a lock or Prize race;
- whether a recovery route is likely to exist.

The current work does not assign a numeric cost to that leakage.

It establishes that the information recipient belongs in the state representation.

A future utility model can distinguish:

- private self-information;
- public information;
- opponent-only information.

## Dedicated information actions differ in opportunity cost

Several legal effects are close to information-dominant actions.

Town Map uses an Item card and a deck slot while preserving the ordinary Supporter and attack windows.

Porygon's Data Check privately inspects the deck through an attack, which ends the turn.

Poipole's Eye Opener privately inspects all face-down Prizes through an attack.

Here Comes Team Rocket! publicly reveals both players' Prize cards through a Supporter, consuming the ordinary Supporter play for the turn.

These actions can produce similar knowledge for the player while imposing very different costs and externalities.

## Connection to discrete strategic value

A material-access optimizer can undervalue an information action because it may:

- draw no cards;
- search out no card;
- do no damage;
- accelerate no Energy.

The earlier value-of-information results show that information can still change the optimal line.

The visibility result adds another requirement: cards producing information must be evaluated for both policy improvement and state mutation.

Town Map is a particularly useful test case for future optimizers because its visible immediate output is almost entirely informational while its face-up transformation changes later Prize interactions.

## Validation

The reproducer scans the effectively legal Expanded pool and asserts:

- exactly 12 deduplicated effect variants explicitly reference `your face-down Prize cards`;
- their card names match the audited set;
- the nine direct exact-Prize effects split into four face-up/public variants and five private-look variants.

The scanner uses the same print-level legality overlay as the other agent6 card-pool work.

## Limitations

Text occurrence does not by itself determine whether a card becomes completely unusable after all Prizes are face up.

Some effects have other independent instructions, damage, or modes that can still matter.

This result therefore identifies affected action edges and target conditions rather than assigning a universal binary "disabled" label.

The public/private classification is about the full Prize composition. A private-look effect can still reveal or move an individual selected card as part of its resolution.

## Next useful work

The typed state model should add a Prize-visibility field separate from composition knowledge.

A minimal representation would track:

- number and identities of face-up Prizes;
- posterior over face-down Prize composition;
- which player knows each hidden identity;
- whether physical Prize positions are mapped;
- card effects that require face-down targets.

That would allow information actions such as Town Map, Gladion, Arc Phone, and one-Prize inspection attacks to coexist correctly in the same transition system.
