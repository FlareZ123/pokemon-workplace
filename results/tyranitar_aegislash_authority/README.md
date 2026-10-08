# Source-scoped Tyranitar-GX Lost Out / Aegislash Durable Blade resolution

## Card-specific official evidence

The Pokémon Card Game Japan Q&A currently serves an exact question about an Aegislash Knocked Out by attack damage from an opponent's Tyranitar-GX with **Lost Out**. It asks whether Aegislash's **Durable Blade** returns Aegislash to the hand before Lost Out sends it to the Lost Zone.

The official answer says the **owner of Aegislash may choose which effect goes first**. Durable Blade first returns it to hand; Lost Out first sends it to the Lost Zone. An adjacent official answer confirms that returning Aegislash with Durable Blade also returns its preceding Doublade and Honedge Evolution cards.

Official Japanese Q&A, query for ギルガルド, page 2:

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%AE%E3%83%AB%E3%82%AC%E3%83%AB%E3%83%89&page=2&regulation_faq_main=

The current-served page does not provide a usable original publication or supersession date for this particular answer. The conclusion here is deliberately **source-scoped**, not a declaration that this answer universally overrides the February 2026 TPCi current-turn-player trigger-order guidance.

## Implementation

`tools/ko_trigger_order_authority.py` adds:

- `JAPAN_LOST_OUT_AEGISLASH_QA`, a named evidence source;
- `LOST_OUT_AEGISLASH`, an exact interaction scope.

The Japan source produces one `KNOCKED_OUT_POKEMON_OWNER` authority claim only for that interaction. All other interaction IDs remain unaffected.

`results/tyranitar_aegislash_authority/reproduce.py` reuses the existing conserved three-card Honedge -> Doublade -> Aegislash Knock Out board and its attachments. It obtains genuine classified destination-program signatures for **Durable Blade** (`SELF_TO_HAND`) and **Lost Out** (`ALL_TO_LOST`) from `knockout_redirection_routes.py`, then composes source claims, concrete player authorization, chosen order, and physical conservation.

Under the selected Japan source, the Aegislash owner may choose either:

| Chosen first effect | Aegislash, Doublade, Honedge | Two Water, DCE, Muscle Band |
| --- | --- | --- |
| Durable Blade | Hand | Discard |
| Lost Out | Lost Zone | Lost Zone |

The independent conserved physical executor validates both endpoints and promotes the surviving Bidoof in the fixture.

## What happens if official source scopes disagree?

The repository already records TPCi Professor guidance from February 2026 stating that the current turn player chooses the order of multiple during-turn Knock Out triggers:

https://professorprogram.pokemon.com/news/11473085

The Japan Aegislash Q&A assigns the choice to the Knocked Out Pokémon's owner. These name different players when an attacking player Knocks Out an opposing Aegislash. Accordingly, passing **both** sources into the authority resolver returns `AUTHORITY_CONFLICT`; it refuses physical execution as though the dispute were resolved.

If both descriptions point to the same concrete player, authorization can proceed without resolving the abstract policy disagreement. The bundled Advanced Player's Rulebook 3.4 independently describes the *current-turn player* as ordering triggered effects when **several Pokémon are Knocked Out simultaneously**, which is narrower than this single-Aegislash case.

This does not prove that two differing real players both have a right to choose the ordering under one tournament rule system. Rather, it explicitly preserves source provenance and reveals where a governing rules-policy decision is needed.

## Validation

Run `python results/tyranitar_aegislash_authority/reproduce.py`. This checks both source-authorized Japan orders, all three evolution cards, explicit attachment routes, unchanged physical card totals, source-conflict refusal, agreement when roles coincide, v3.4's narrow multiple-KO scope, and isolation from unrelated interactions.

CI workflow: `.github/workflows/validate-tyranitar-aegislash-authority.yml`.

## Strategic relevance

The example establishes an independently sourced, card-specific ordering authority where an executable destination choice directly determines future availability of an Evolution stack and attachments. It provides a rules-evidence fixture for integrating source-aware order choice with a game-state planner, while making regional/version interpretation an explicit input instead of hiding it in an optimizer.
