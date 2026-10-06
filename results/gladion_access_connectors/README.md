# Gladion access connectors: timing and trigger semantics

## Question

Which Expanded routes that appear to provide access to Gladion can actually produce a playable Gladion in the current Supporter window?

A raw graph edge such as "card X reaches a Supporter" is too coarse. The timing and zone semantics of the connector matter. This result builds a card-text census and a practical timing taxonomy around Gladion-style Prize rescue.

Implementation and text census: tools/supporter_access_catalog.py

## Rules and card-text basis

Gladion is a Supporter. Its bundled text looks at the face-down Prize cards, puts one into the hand, then shuffles the played Gladion into the remaining Prize cards. The effect also says that if the Gladion was not played from the hand, it does nothing.

The bundled advanced manual supplies two timing facts used here:

1. a player may use only one Supporter during their turn;
2. after a player uses an attack, their turn ends.

The manual also distinguishes playing a Basic Pokémon from the hand onto the Bench from effects that put a Basic Pokémon onto the Bench. This distinction matters for abilities such as Tapu Lele-GX's Wonder Tag, which explicitly requires the Pokémon to be played from the hand onto the Bench.

## Card-text census

The bundled snapshot contains **37 Expanded-legal card names across 62 prints** whose text literally contains a deck search for a Supporter card followed by putting the found card or cards into the hand.

By effect source, those names are:

| Source of effect | Unique card names |
| --- | ---: |
| Pokémon Ability | 10 |
| Pokémon attack | 20 |
| Item or ACE SPEC Item | 4 |
| Supporter | 3 |

This literal-text census is narrower than the true access graph. Computer Search can search for any card, so it can find Gladion without mentioning the word Supporter. Battle Compressor plus VS Seeker can create a two-card route through the discard pile. Pokégear 3.0, Random Receiver, and Trainers' Mail can probabilistically reveal or select Gladion without the same exact wording.

One of the four literal Item names, Team Rocket's Transceiver, only searches for a Supporter with "Team Rocket" in its name and therefore cannot find Gladion.

## Timing classes

### 1. Current-window direct Items

These can put Gladion into the hand before the Supporter play of the same turn, assuming their own conditions are satisfied.

| Card | Representative print | Relevant constraint |
| --- | --- | --- |
| Call Bell | sv8-165 | Only going second, only during the first turn |
| Secret Box | sv6-163 | ACE SPEC; discard 3 other cards; searches several Trainer categories simultaneously |
| Computer Search | bw7-137 | ACE SPEC; discard 2 cards; searches any card |
| Xtransceiver | bw3-96 | Coin flip; succeeds only on heads |

This class illustrates why access needs a cost model as well as a reachability edge. Secret Box and Computer Search are broad connectors, while their discard requirements can sharply reduce realistic availability.

### 2. Current-window Supporter-search Abilities

Ten Expanded-legal card names have an Ability that directly searches the deck for one or more Supporters and puts them into the hand. Important examples include:

- Jirachi-EX, Stellar Guidance
- Tapu Lele-GX, Wonder Tag
- Lumineon V, Luminous Sign
- Meowth ex, Last-Ditch Catch
- Gallade, Buddy Catch
- Dragonite, Fast Call
- Magneton, Call Signal
- Meowstic, Inviting Ears
- Pelipper, Hearsay
- Silvally, Call a Buddy

These are not equivalent outs. The Basic Rule Box Pokémon require a Bench slot and an Ability that remains usable. Jirachi-EX, Tapu Lele-GX, Lumineon V, and Meowth ex specifically trigger from being played from the hand onto the Bench. Gallade and Dragonite require established Stage 2 Pokémon. Magneton's search Knocks itself Out. Silvally requires an empty hand. Meowstic and Pelipper require an evolution played from the hand.

A simulator should therefore model these as typed, state-dependent connectors rather than ten interchangeable copies of a generic Supporter out.

### 3. Discard-pile Item chain

Battle Compressor Team Flare Gear can search the deck for cards and discard them. VS Seeker can then return a Supporter from the discard pile to the hand.

Therefore:

Battle Compressor -> Gladion in discard -> VS Seeker -> Gladion in hand

is a deterministic two-Item route if both Items are usable and present/reachable.

This route has different vulnerability from a direct deck search. Item lock can remove both edges. The route also consumes Battle Compressor and VS Seeker, each of which can have important competing uses.

### 4. Stochastic current-window Items

Pokégear 3.0, Random Receiver, and Trainers' Mail can expose Gladion during the current turn without consuming the Supporter play, while success depends on deck composition and order.

Their probability models differ:

- Pokégear 3.0 looks at the top seven and may take a Supporter.
- Random Receiver reveals until the next Supporter and takes it, making the identity distribution depend on the Supporter population.
- Trainers' Mail looks at the top four and may take a Trainer other than Trainers' Mail.

Counting each as one full deterministic "out" would overstate Gladion access.

### 5. Attack-based Supporter search

Twenty Expanded-legal card names in the literal census search for a Supporter through an attack. Examples include Clefairy, Eevee, Fennekin, Piplup, Xerneas, and several Stage 1 attackers.

These cannot produce a Gladion play in the same turn. Using the attack ends the turn. They are setup routes for a later Supporter window.

This is a general temporal-graph rule: an edge may reach the required card while crossing the action boundary that made the card useful.

### 6. Supporter-based search

The literal census includes Misty's Favor, Steven, and Larry's Skill, each of which can search another Supporter. Many broader Supporters can also reach Gladion because they search for a Trainer or any card, including Skyla, Green's Exploration, Red's Challenge, Teammates, and Team Rocket's Petrel.

They cannot lead to a Gladion play in the same turn under the normal one-Supporter rule. Their useful edge is:

current Supporter window -> Gladion in hand -> later Supporter window

This matters in a timed Prize-rescue model. A search graph that collapses that path to immediate access can be off by an entire turn.

## Zone semantics: the Tapu Lele-GX counterexample

Tapu Lele-GX's Wonder Tag is a useful test for connector correctness.

Quick Ball and modern Ultra Ball search a Pokémon into the hand. If they obtain Tapu Lele-GX, the player can then manually play Tapu Lele-GX from the hand onto an open Bench, satisfying Wonder Tag's trigger and searching Gladion.

Nest Ball instead searches for a Basic Pokémon and **puts it directly onto the Bench**. That does not perform the action "play this Pokémon from your hand onto your Bench." Therefore:

Quick Ball -> Tapu Lele-GX in hand -> manually Bench -> Wonder Tag -> Gladion

is a valid same-window access line if all costs and board constraints are satisfied, while:

Nest Ball -> Tapu Lele-GX directly onto Bench -> Wonder Tag

does not activate Wonder Tag.

The same distinction applies to Jirachi-EX, Lumineon V, and Meowth ex because their Supporter-search Abilities use the same hand-to-Bench trigger structure.

This is a concrete example of a false graph edge created by ignoring zones and trigger verbs.

## Connector contention

Even a valid path can be strategically dominated.

Ultra Ball -> Tapu Lele-GX -> Gladion consumes Ultra Ball, its two-card discard cost, and a Bench slot before Gladion is played. In a deck where Ultra Ball is needed to establish an attacker, the route can exist while being strategically inferior or impossible after realistic resource preservation is applied.

Secret Box can search Gladion directly, while its other searched categories and three-card discard cost may make a different use of Secret Box much stronger.

Battle Compressor plus VS Seeker has similar contention. Battle Compressor may have deck-specific payloads that are more important than putting Gladion into the discard pile.

The connector therefore needs at least these annotations:

- zone entered by the target;
- whether a trigger requires play from hand;
- action type consumed by the connector;
- whether the turn ends;
- discard or hand costs;
- Bench or evolution requirements;
- Ability/Item/Supporter lock sensitivity;
- stochastic success probability;
- connector opportunity cost.

## Implication for the timed Prize-rescue model

The earlier timed-access baseline treats cards_seen_by_window as unbiased random exposure. This result shows how the next access-network layer should alter that baseline.

A direct Item or usable Ability can add same-window targeted access. A Supporter search for Gladion should add access only to a later Supporter window. An attack-based search should also advance the turn boundary. A deck-to-Bench search must preserve the destination zone so that hand-play triggers are not incorrectly fired.

This means targeted access should be represented as typed state transitions rather than by increasing the effective number of random cards seen.

## Validation

tools/supporter_access_catalog.py scans every bundled English card record whose database legality says Expanded legal. It reports the literal direct-supporter-search census and prints the exact text of representative connectors.

It also has regression assertions for the zone distinction:

- Nest Ball contains the direct-to-Bench wording;
- Quick Ball contains the into-hand wording;
- Tapu Lele-GX requires play from the hand onto the Bench;
- VS Seeker returns a Supporter from discard to hand;
- Battle Compressor sends searched cards to the discard pile.

The representative cards in this result are not among the seven stale-ban prints repaired by the repository's Expanded legality overlay.

## Limitations

The 37-name census is a text-pattern census, not an exhaustive enumeration of every multi-card route to Gladion. Generic any-card search, draw engines, top-deck manipulation, recovery loops, Pokémon search chains, bounce/replay effects, and other indirect routes can create additional paths.

Some routes have matchup- or state-specific legality. Ability lock, Item lock, Supporter lock, Bench saturation, evolution timing, and hand costs can remove edges during a real game.

The classification focuses on whether a connector can make Gladion playable within the current Supporter window. A deck-specific optimizer still needs to decide whether using that connector for Gladion is strategically correct.

## Next useful work

The next high-value extension is a small typed access-network engine. It should represent card zones and action windows explicitly, then encode representative paths such as Quick Ball -> Tapu Lele-GX -> Gladion, Nest Ball -> Tapu Lele-GX, Battle Compressor -> VS Seeker -> Gladion, and Skyla -> Gladion.

A good first test is whether the engine automatically derives the correct temporal outcome for those four lines before it is expanded toward full deck simulation.
