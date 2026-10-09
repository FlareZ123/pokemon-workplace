# Printed Expanded card examples for output-capacity models

The bundled card database supplies concrete contrasts for the abstract
opponent hand-assembly research. This catalog uses named print IDs and
verifies the relevant English wording from the repository. It supplies
semantics examples rather than a legality ruling.

| Print | Textual resource shape | Strategic model qualification |
| --- | --- | --- |
| Computer Search (bw7-137) | Discard two hand cards; search for one card | A single-output flexible resource. Payment feasibility can prevent use |
| Ultra Ball (swsh9-150) | Discard two other hand cards; search for one Pokémon | One Pokémon output; cannot independently fetch two required Pokémon |
| Serena (swsh12-164) | Choose one of discard-and-draw or gust of Benched Pokémon V | Exclusive mode choice for a Supporter window |
| Guzma & Hala (sm12-193) | Fetch Stadium; optional discard two other hand cards to also fetch Tool and Special Energy | Conditional multi-category output in one Supporter use |
| Secret Box (sv6-163) | Discard three other hand cards; search one Item, Tool, Supporter and Stadium | Four category-restricted simultaneous outputs if payment and searches succeed |
| Tag Call (sm12-206) | Search for up to two TAG TEAM cards | Two possible outputs within a restricted card category |

A physically held card can connect to many potential goals in a graph, yet
have only one immediate output. Computer Search and Ultra Ball illustrate
why the one-use Hall matching model is appropriate for independent target
claims. Serena illustrates exclusive mode selection.

For Guzma & Hala and Secret Box, a capacity-one model can be too strict
because one actual play can output several separately selected cards.
A uniform high numeric capacity is also insufficient: each search has a
typed target category, payment constraints, and the actual deck may contain
fewer eligible targets. Tag Call can search up to two eligible TAG TEAM
cards, which introduces a category-specific quantity.

The generalized Hall framework can model an *abstract full sequence of
independent one-use connectors*. These printed examples motivate a richer
extension in which a resource's one-use action generates an output **bundle**
under game-state-dependent payments and target availability, with timing and
Supporter constraints. That would be required before asserting an executable
competitive Expanded line.

Run `python results/opponent_bonus_assembly/card_text_reproduce.py` from the
repository root to verify the exact bundled print IDs and wording fragments.
The reproducible catalog intentionally asserts fixed textual anchors rather
than claiming to parse the entire historical Expanded card pool or its errata.
