# Aichi Regidrago: Super Rod can reverse the preferred Trifrost Energy payment

**Result type:** source-card and rules-backed, matched initial game-state constructive witness. It demonstrates one legal next-turn route conditional on availability and absence of opponent interference. It does **not** assign a frequency or predict wins.

## A fully physical matched starting state

The published [2026 Aichi tenth-place Regidrago 60](https://limitlesstcg.com/decks/list/26816) contains four Double Dragon Energy, four Basic Grass, two Basic Fire, one Kyurem, one Super Rod, and one Crispin.

Consider a single exact Regidrago VSTAR state:

| Zone | Relevant cards |
| --- | --- |
| Active Regidrago VSTAR | One Double Dragon Energy already attached |
| Hand | Another DDE, one Basic Grass, **both Basic Fire**, Super Rod, Crispin |
| Searchable deck | Two DDE, three Basic Grass, **zero Basic Fire**, plus other cards |
| Discard | Kyurem for Apex Dragon to copy; no Basic Fire initially |
| Future resource availability | Manual attachment unused in the attacking turn; following turn's Super Rod, Supporter Crispin and manual attachment available |

The relevant Energy allocation conserves exactly four DDE, four Basic Grass and two Basic Fire across physical zones. Regidrago can attack with Apex Dragon once the player manually attaches **either held Basic** to the active DDE. Its Apex Dragon copies Kyurem's Trifrost, discarding all attached Energy. The opponent's intervening turn is assumed to leave Regidrago, the hand and the Trainer options intact.

## Paired action outcomes

| Step | Attach Grass before Trifrost | Attach Fire before Trifrost |
| --- | --- | --- |
| After copied Trifrost | Discard contains DDE + Grass | Discard contains DDE + **Fire** |
| Next turn: Super Rod | Can return Grass; deck still has **no Fire** | Returns discarded Fire; deck has Grass + Fire |
| Next turn: Crispin | Cannot attach a Basic via the two-type search, because the deck lacks Fire | Finds both types, attaches **Grass** to Regidrago, puts Fire in hand |
| Next turn: normal attachment | Attaches held second DDE; has two Energy units | Attaches held second DDE; has **DDE + Grass**, satisfying Apex's Grass/Grass/Fire cost |
| Immediate next-Apex Energy ready | **No** | **Yes** |

The mechanics follow printed text: Super Rod (`sv2-188`) shuffles up to three Pokémon/Basic Energy cards from discard into deck; Crispin (`sv7-133`) searches up to two *different-type* Basic Energy cards, puts one into hand and attaches the other. The Regidrago VSTAR (`swsh12-136`) Apex Dragon copies Kyurem (`sv6pt5-47`) Trifrost, which discards all attached Energy. DDE (`xy6-97`) supplies two flexible Energy units to Dragon Pokémon.

### Where the advantage vanishes

In the same restricted sequence, the Grass-discard branch can also recharge if a **Basic Fire was already in the discard pile** and is recoverable by Super Rod. Another playable Item that discards Fire from hand before Super Rod (for example, Quick Ball with a payable target/card action) also restores that branch. The included controls conserve all physical Energy copies in the initial-discard variant; the extra-Item case assumes that extra Item is available and payable. These are alternative action channels, not claims the opponent always permits them.

This is a concrete **same-state causal reversal** to simplistic advice that scarce Fire should always be kept in hand. The [paired causal stock study](../aichi_regidrago_crispin_paired_causal/) establishes that the deck itself initially remains unchanged by attaching either held Basic. The difference here arises later because Super Rod can selectively move a newly discarded Fire **back into the deck**, enabling Crispin.

## Reproduction and boundaries

- [Source-backed sequential model](../../../tools/aichi_regidrago_super_rod_bridge.py) validates exact physical card-print text, real list inclusion, Energy conservation, Item-to-Supporter sequencing, and the once-per-turn manual attachment.
- [Independent reproducer](reproduce.py) exhausts legal Super Rod subsets, both possible Crispin attachment roles, and manual attachment candidates over **six controlled post-attack cases**.
- Run from repository root: `python -m results.tests.aichi_regidrago_super_rod_bridge.reproduce`.

This checks Energy readiness of the **surviving active Regidrago** only. Earlier turns needed to establish that board, correct Kyurem discard, three opposing Trifrost targets, unspent Supporter and manual resources, opponent actions, hand acquisition, Stadium effects, Ability locks, Prize status and the probability of accessing the full line are outside the model. No 60-card swap or match-level claim follows.
