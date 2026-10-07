# Shadow Rider Calyrex: the Regidrago counter-ALS is a zone-routing line

## Question

Yasunori Kato won the 2026 CL Aichi Open League with Shadow Rider Calyrex VMAX. In the official winner interview, Kato identified Mimikyu and Dialga-GX as deliberate deckbuilding choices and said Mimikyu's Copycat used the opponent Regidrago VSTAR's Apex Dragon to turn a game around.

The repository already proves the nested copy semantics:

\`Copycat -> Apex Dragon -> Timeless-GX\`

This result asks a different question. How realistic is the response turn once the physical payloads can begin in deck, hand, discard, or Prize cards?

Implementation: \`tools/shadow_rider_regidrago_counter_als.py\`  
Regression: \`results/shadow_rider_regidrago_counter_als/reproduce.py\`

## Empirical anchor

Primary event source:

- Pokémon Card Game official, CL2026 Aichi May winner interview:
  https://www.pokemon-card.com/info/005499.html
- The Open League winner section names Yasunori Kato, identifies Shadow Rider Calyrex VMAX as his deck, says Mimikyu and Dialga-GX were deliberate inclusions, and records that Mimikyu used Copycat after taking Apex Dragon from an opposing Regidrago VSTAR.

Published 60-card list cross-check:

- Limitless, Yasunori Kato, 1st Place CL Aichi Open League:
  https://limitlesstcg.com/decks/list/26807
- Relevant counts are 1 Mimikyu, 1 Dialga-GX, 4 Mysterious Treasure, 4 Fog Crystal, 1 Quick Ball, 1 Hisuian Heavy Ball, 1 Battle Compressor, 1 Night Stretcher, 1 Tulip, 1 Guzma, 1 Dimension Valley, 4 Shadow Rider Calyrex VMAX, and 11 Psychic Energy.

The external event evidence establishes that the counter was intentional and used in competition. The card database and rulebook establish the mechanics.

## Destination asymmetry

The two singleton payloads want opposite physical destinations.

- Mimikyu must become an attacker. The bounded routing endpoint is Mimikyu in hand, ready to enter the Bench before being powered and promoted.
- Dialga-GX must be in the Shadow Rider player's discard pile because the copied Apex Dragon resolves from the copying player's perspective and searches that player's discard pile for a Dragon Pokémon.

This creates a useful connector inversion. A discard cost can be productive.

If Mimikyu is in deck and Dialga-GX is in hand, one Mysterious Treasure performs both required movements:

\`discard Dialga-GX as cost -> search Mimikyu\`

The cost places Dialga exactly where Apex Dragon needs it while the output places Mimikyu in hand. Quick Ball can perform the same paired movement because Mimikyu is Basic.

This is a concrete case where treating "discard one card" as a scalar penalty misstates the line.

## Exact coarse zone matrix

The regression gives each payload one of four starting zones:

\`deck, hand, discard, prize\`

It then searches shortest routes using only the named Aichi routing package:

- Mysterious Treasure;
- Fog Crystal;
- Quick Ball;
- Battle Compressor;
- Hisuian Heavy Ball;
- Night Stretcher;
- Tulip.

With Item play available, one generic disposable hand card, and the listed connector counts, **15 of 16** ordered zone pairs can reach the bounded endpoint:

\`Mimikyu in hand + Dialga-GX in discard\`

The only unreachable pair is:

\`Mimikyu Prized + Dialga-GX Prized\`

The reason is physical rather than probabilistic. The list has one Hisuian Heavy Ball, and one use can exchange itself for only one Basic Pokémon from the Prize cards. Every other listed routing action operates on deck, hand, or discard.

This is a pre-Prize-taking statement. Taking Prize cards before the response can change the state.

## Representative routes

### Dialga in hand, Mimikyu in deck

One Mysterious Treasure is enough:

1. discard Dialga-GX;
2. search Mimikyu into hand.

No unrelated discard fodder is needed.

### Both payloads in deck

Battle Compressor plus Night Stretcher can deliberately send both cards through discard:

1. Battle Compressor discards Mimikyu and Dialga-GX;
2. Night Stretcher returns Mimikyu to hand;
3. Dialga-GX remains in discard.

The intermediate state looks worse under a zone-agnostic "discarded payload" heuristic while satisfying the line exactly after the recovery action.

### Dialga-GX Prized, Mimikyu in deck

Hisuian Heavy Ball plus Mysterious Treasure repairs the singleton:

1. Heavy Ball exchanges itself for Dialga-GX;
2. Mysterious Treasure discards Dialga-GX and searches Mimikyu.

### Mimikyu Prized, Dialga-GX in deck

Hisuian Heavy Ball plus Battle Compressor splits the destinations:

1. Heavy Ball recovers Mimikyu;
2. Battle Compressor discards Dialga-GX.

These two single-Prize cases have different continuations despite the same abstract fact "one critical singleton is Prized."

## Exact initial Prize collision

For two distinct one-of cards in a 60-card deck with six initial Prize cards:

- neither is Prized: **80.847458%**;
- exactly one is Prized: **18.305085%**;
- both are Prized: **0.847458%**.

The final number is the initial probability of the one coarse payload pair that the bounded one-Heavy-Ball routing model cannot repair before Prize taking.

It is not a match-loss probability. Natural Prize taking, alternative recovery, prior materialization, and opponent pressure are outside this calculation.

## Copycat Energy threshold

The relevant Mimikyu print has Copycat for:

\`Psychic + Colorless\`

Dimension Valley makes attacks used by Psychic Pokémon cost one Colorless less. Mimikyu is Psychic, so a live Dimension Valley reduces Copycat to:

\`Psychic\`

From zero attached Energy, the deterministic attachment threshold therefore changes:

- no Dimension Valley: 2 Psychic Energy cards are needed;
- Dimension Valley live: 1 Psychic Energy card is needed.

Shadow Rider Calyrex VMAX's Underworld Door can attach a Psychic Energy from hand to a **Benched** Psychic Pokémon. The ordinary manual attachment is a separate channel.

Consequently, from zero Energy:

- one Underworld Door plus the manual attachment can pay Copycat without Dimension Valley when two Psychic Energy cards are available;
- one manual attachment alone can pay Copycat with Dimension Valley;
- one Underworld Door alone can also pay the reduced cost while Mimikyu is still Benched.

The order matters. An Underworld Door attachment must happen before a later promotion of Mimikyu to the Active Spot.

The bounded deterministic test does not count the two cards drawn by Underworld Door as guaranteed future Energy. Those draws can create additional stochastic continuations.

## Promotion and Supporter contention

The list has Guzma, which can move the prepared Benched Mimikyu Active when its first switching clause succeeds.

Tulip can recover a Psychic Mimikyu from discard. Both are Supporters.

Under the ordinary one-Supporter quota, a same-turn line that needs:

\`Tulip recovery + Guzma promotion\`

is blocked by Supporter contention.

Night Stretcher can perform the Mimikyu recovery as an Item, leaving the Supporter window available for Guzma. This gives Night Stretcher discrete tactical value inside the counter-ALS even though Tulip can recover the same Pokémon from the same discard pile.

Other promotion routes, including ordinary retreat and Float Stone, can avoid Guzma entirely. Their board requirements are not enumerated by this focused kernel.

## Item-lock sensitivity

The named routing package is heavily Item-dependent.

With Item play disabled in the bounded model:

- deck and Prize routing disappear;
- Tulip can still recover Mimikyu from discard if Dialga-GX is already in discard;
- the resulting Supporter use can then collide with Guzma if Guzma is also needed to promote Mimikyu.

The counter therefore has a distinct pre-attack preparation surface that can be disrupted even when the nested copy interaction itself remains rules-legal.

## Nested execution endpoint

After the preparation state is reached, the regression reuses the repository's canonical attack-copy kernel.

The executed body chain is:

\`Copycat -> Apex Dragon -> Timeless-GX\`

The checks preserve four semantic facts:

1. Copycat sees the opponent's last declared Apex Dragon, which is not a GX attack.
2. Copied Apex Dragon reads the Mimikyu player's own discard pile.
3. Dragon-type Dialga-GX supplies Timeless-GX there.
4. Timeless-GX spends the Mimikyu player's GX-use channel and schedules another turn while skipping Pokémon Checkup.

The declared attack identity remains Copycat.

## Strategic interpretation

This empirical ALS has three coupled layers:

- **opponent history:** Regidrago must expose Apex Dragon as its last declared attack;
- **payload routing:** Mimikyu and Dialga-GX must occupy different zones at the response deadline;
- **attack readiness:** Mimikyu needs an attachment and promotion sequence before Copycat.

The champion list contains cards that service more than one layer at once.

Mysterious Treasure is the clearest example. In the favorable hand/deck state, its discard payment and search output jointly satisfy both singleton destinations. Dimension Valley compresses the Energy requirement from two attachments to one. Night Stretcher preserves the Supporter window that Tulip would spend.

This is stronger evidence for ALS modeling than a three-node interaction graph because the official event record confirms that the matchup-specific line mattered in tournament play.

## Evidence classification

**Official empirical observation**

- Kato deliberately included Mimikyu and Dialga-GX.
- He reported using Copycat after an opposing Regidrago VSTAR used Apex Dragon and described it as a game-turning play.

**Card-text and rules facts**

- Copycat's immediate non-GX filter;
- Apex Dragon's Dragon-in-own-discard selector;
- Timeless-GX's extra-turn effect;
- Mysterious Treasure, Heavy Ball, Compressor, Night Stretcher, Tulip, Guzma, Underworld Door, and Dimension Valley texts;
- constrained deck searches can choose fewer targets, including zero, under the repository's current rulebook interpretation.

**Mathematical result**

- the exact two-singleton initial Prize distribution.

**Computational result**

- 15 of 16 coarse payload-zone pairs are reachable with the bounded Aichi routing package;
- both-Prized is the unique unreachable pair before Prize taking;
- the representative coupled routes above;
- the 2-to-1 deterministic Copycat attachment threshold under Dimension Valley;
- the Tulip/Guzma ordinary Supporter collision;
- canonical nested execution of Copycat -> Apex Dragon -> Timeless-GX.

## Limits

The 4x4 zone matrix is a reachability model. It assumes the named connector cards themselves are available, one generic disposable hand card is available in the default matrix, Items are unlocked unless explicitly disabled, and Bench entry is legal.

It does not estimate the probability that the whole response turn is assembled from a random current hand. It also does not model every way to obtain the connectors, Forest Seal Stone, Underworld Door draw replenishment, opponent disruption during earlier turns, Bench capacity, retreat payment, or exact Prize positions after the game has progressed.

The Prize calculation concerns the two singleton payloads only. It does not include multi-Prized collapse involving Heavy Ball or the connectors needed to convert a rescued payload into the required destination.

A high-value continuation is an exact response-turn probability model conditioned on the observed opponent Apex Dragon, with K0/K1 Prize knowledge, connector access, Bench state, live Shadow Rider VMAX count, current Stadium, Energy in hand, and promotion route.
