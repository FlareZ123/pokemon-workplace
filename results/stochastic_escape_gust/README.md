# Draw-limited gust versus a defender's escape

## Question and model

How does the opponent's ability to escape after a non-KO hit change the value of Boss's Orders that is still hidden in the attacker's draw pile? This combines the prior `results/stochastic_gust_draw/` draw recurrence and `results/defender_escape_gust/` damage-persistence adversarial game.

The exact `Fraction` dynamic program in [`tools/stochastic_escape_gust.py`](../../tools/stochastic_escape_gust.py) models one normal draw before each attack, one optional gust to a Benched Pokémon per attack turn, persistent target durability measured in one or two remaining hits, and defender choice of free post-KO promotion or one limited escape after an unsuccessful hit. The attacker minimizes expected attacks to win six Prizes or clear the opponent's Pokémon. The defender maximizes the attack count, choosing before the subsequent random draw.

Card-text anchors from the bundled English card pool: Boss's Orders `swsh2-154` chooses one opposing Benched Pokémon to become Active; Switch `sv1-194` demonstrates Active/Bench switching. The 2025 advanced rulebook limits Supporters to one per turn and distinguishes voluntary switching from normal retreat. Escape is a **free abstract token** here. No claim is made that a particular deck has that token available. The model excludes Energy, Trainer access, source-specific locks, draw Supporter contention, opponent attacks, KO Prize draws, recovery, evolution, healing, and turn clock effects.

## Constructive counterexample and independent physical oracle

Opponent board: Active `(3 Prizes, 2 hits)`, Bench `[(3,2),(3,2)]`. The attacker needs six Prizes; the unseen deck has 12 cards with 0, 1, or 2 Boss effects and otherwise filler, with no gust initially in hand.

| Opposing escape tokens | Boss in hidden deck | Minimum expected attacks |
| --- | ---: | ---: |
| 0 | 0 | 4 |
| 0 | 2 | 4 |
| 1 | 0 | 5 |
| 1 | 1 | 14/3 |
| 1 | 2 | 146/33 |
| 2 | 2 | 54/11 |

With no escape, four attacks are sufficient even without gust. With one escape, an opponent can abandon a wounded high-Prize Pokémon and make an ungusted line take five attacks. Having at least one Boss among the first four draws restores a four-attack line.

There are exactly `C(12,2)=66` distinct physical positions for two Boss copies; 38 have a copy in the first four draws and 28 have neither there. Thus the independent physical-order game-tree oracle and chance/minimax recurrence both obtain

`E[attacks] = (38*4 + 28*5)/66 = 146/33 = 4.424242...`.

The adversary's extra escape **creates** the positive expected attack-count value of these Boss copies on this board. Their value was zero with no escape.

## Exact structural census

Across **96** distinct synthetic states with 2..4 opposing Pokémon, each worth 1 or 3 Prizes, each requiring 1 or 2 hits, Active distinguished, an unordered Bench and total board rewards of at least six, the same 12-card pile held 0/1/2 Boss cards. When the defender gained one escape, the improvement from having two Boss cards (relative to none) **increased in 10 states**, **remained the same in 49**, and **decreased in 37**.

In four states the two-Boss package went from worthless to helpful; in twelve it went from helpful to worthless. The package reduced expected attack count in 66/96 classes with no escape, 58/96 with one, and 53/96 with two. These are equal-weight structural counts, **not** real-deck incidence, win rates or metagame frequencies.

The exact solver also checks monotonicity throughout the census: acquiring more Boss copies never raises the attacker's expected attacks, and adding an escape to a fixed board/draw configuration never lowers them.

## Reproduction and limitations

- [Exact implementation](../../tools/stochastic_escape_gust.py)
- [Reproduction script](reproduce.py) with source-text assertions, all 66 physical placements, 96-board census and exact Fraction checks
- [GitHub Actions validation](../../.github/workflows/validate-stochastic-escape-gust.yml)
- Related results: [defender escape](../defender_escape_gust/), [stochastic gust draws](../stochastic_gust_draw/), [typed retreat](../typed_retreat_gust/), [gust synthesis](../gust_option_value_synthesis/)

Run `python results/stochastic_escape_gust/reproduce.py` from the repository root. The physical oracle exposes the whole fixed future draw order when solving each tree; agreement on this witness is a special independently verified property and is not a general equivalence theorem between clairvoyant and nonclairvoyant policies.

Most valuable continuation: replace the free defender escape token with a state-dependent retreat or switching transaction that consumes Energy, Items, Tools, Bench space or another finite resource; couple both players' random access to those actions and check Boss's Orders Supporter contention. This would support matchup-specific value assessments.
