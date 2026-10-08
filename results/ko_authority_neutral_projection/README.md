# A Knock Out state can be invariant despite unresolved order authority

## Question

If selected official sources disagree on which player can order competing KO effects, can a game-state simulator ever advance confidently without choosing a winner in that rules-source dispute?

**Yes, within the fixed destination-only KO model, provided every permitted candidate order yields the identical complete conserved terminal state.** This result separates physical endpoint certainty from the legally authorized actor who selects an effect order.

Implementation: `tools/ko_authority_invariant_projection.py`.
Regression: `results/ko_authority_neutral_projection/reproduce.py`.

## Real card-text witness

Consider an opposing Tyranitar-GX with *Lost Out* Knocking Out your Active Basic Lapras while the *Lost City* Stadium is in play.

- [Lost Out](https://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/series/sm8/121) sends the Knocked Out opposing Pokémon and **all attached cards** to the Lost Zone.
- [Lost City](https://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/series/swsh11/161/) sends the Knocked Out Pokémon to the Lost Zone while **discarding attached cards**.
- The [official Japanese Q&A](https://www.pokemon-card.com/rules/faq/search.php?sc_group_id=606) says that for this exact pair, the opponent of Tyranitar-GX (the Knocked Out Pokémon's owner) may choose which effect goes first. Lost Out-first loses Pokémon and attachments; Lost City-first discards attachments while losing the Pokémon.
- [TPCi Professor guidance from February 2026](https://professorprogram.pokemon.com/news/11473085) instead says the current player orders multiple triggered KO effects during a turn.

The repository preserves these source claims independently. In the fixture, Tyranitar-GX's attacking player and Lapras's owner are different, so the combined-source chooser assessor reports `AUTHORITY_CONFLICT`. The existing `authorize_and_resolve_order` bridge appropriately refuses to accept a selected order as though the conflict were settled.

### Case A: no attached cards

Both printed effects send Lapras itself to the Lost Zone. Because it has **no attachments**, there is no card whose destination differs between the two effects. The two abstract orders collapse to one complete conserved terminal state, with Lapras in the Lost Zone and the surviving Benched Bidoof promoted.

The new projection returns that invariant terminal state together with the **unresolved authority conflict**. It does not claim the simulation chose an order or that either player was authorized to select one.

### Case B: one or more Basic Water Energy attached

If Lapras has any Basic Water Energy attached, Lost City-first places that Energy in discard, whereas Lost Out-first puts it in Lost Zone. The two complete terminal states differ.

The same source conflict now matters materially. The new adapter returns `ORDER_SENSITIVE`, the number of distinct possible outcomes, the unresolved chooser evidence, and **no terminal state**. It refuses to silently pick the attacker's or defender's preferred outcome.

The regression constructs five exact conserved boards with zero, one, two, three and four attached Basic Water Energy cards. It verifies the contrasting behaviors for every count and independently executes both physical branches through the original fixed-order disposal kernel, with promotion and card conservation.

## Algorithm and correctness boundary

The adapter:

1. Assesses the selected rule-source claims and concrete player roles without replacing or reconciling their differences.
2. Enumerates all candidate destination outcomes, including external precedence constraints only if explicitly supplied.
3. Groups exchangeable-equivalent outcomes using the independently validated terminal zone-signature quotient, then executes physical KO disposal once per distinct terminal state.
4. Returns the sole state if exactly one conserved terminal state exists; otherwise returns no state and reports that an actual authorized choice or stronger rule source is required.

For an order-invariant set, the same physical result follows from every candidate order. Even a completely unresolved chooser cannot affect that *specific* destination-only physical outcome. Invariance across a superset of actual legal orders is a sufficient condition for outcome certainty.

This establishes physical-state certainty under the supplied effects, and leaves legal-order authority unresolved. It is not a general rule that an unapproved player may choose actions. The guarantee excludes other side effects outside destination routing, dynamic trigger eligibility, unknown card text, and any historical/tournament variation in whether an effect activates.

## Additional checks

The test shows that a known chooser under just the Japan source still leaves the Energy-attached state order-dependent until an actual order is submitted. It also verifies that a source profile with no applicable authority claim can coexist with an invariant physical projection.

An externally imposed Lost City-before-Lost Out precedence is tested as a **synthetic constraint** that collapses the Energy-attached case to one result. The study makes no claim that the precedence is an official governing ruling.

## Strategic implication

Some unresolved rule-source disagreements can be safely deferred in a simulation when they cannot affect any conservatively modeled outcome. Others must remain explicit branches because they change recoverable resources. This distinction supports research that can continue producing correct conditional state transitions while maintaining strict uncertainty and provenance discipline.
