# Wobbuffet versus Flutter Mane: distinct Thorns counter windows for Shadow Rider

## Strategic question

Can the champion Shadow Rider Calyrex VMAX deck use a one-card non-Rule-Box Psychic Basic as a persistent counter to Active Iron Thorns ex? Both Wobbuffet and Flutter Mane suppress the opposing Iron Thorns, yet they affect the champion's Radiant Eternatus launch very differently.

This research is a conditional rules test, not a measured win-rate or a verified 60-card modification. Neither card is in the published Aichi champion 60.

## Relevant exact card text

- **Wobbuffet (xy4-36)**: Bide Barricade, while Active, removes Abilities from non-Psychic Pokémon on both sides, including Pokémon in hands and discard piles. Wobbuffet is Psychic and has no Rule Box.
- **Flutter Mane (sv5-78, sv8pt5-43, svp-97)**: Midnight Fluttering, while Active, makes the opposing Active Pokémon have no Abilities, except Midnight Fluttering. Flutter Mane is Psychic, non-Rule-Box.
- **Iron Thorns ex (sv6-77)**: while Active, Initialization removes Abilities from Rule Box Pokémon on both sides except Future Pokémon. Iron Thorns itself is Basic Future, but does not have an exemption from Bide Barricade or Midnight Fluttering.
- **Shadow Rider VMAX (swsh6-75)**: Psychic VMAX, Underworld Door. **Radiant Eternatus (swsh12pt5-105)**: Dragon Basic with a Rule Box, Climactic Gate, which can place two VMAX directly onto the Bench and ends the turn. **Latias ex (sv8-76)**: Psychic Basic Rule Box, Skyliner gives Basics free retreat.

All named Ability text is asserted from exact source prints.

## Executable lock-source outcomes

The test uses one unified shared dependency-graph resolver, with a newly included Midnight Fluttering profile alongside existing Bide Barricade and Initialization. It checks four conditional board states.

| Our Active | Effective lock source | Shadow Rider Underworld Door | Radiant Eternatus Climactic Gate | Latias Skyliner |
| --- | --- | --- | --- | --- |
| No counter Active | Iron Thorns Initialization | Suppressed | Suppressed | Suppressed |
| Wobbuffet | Wobbuffet Bide Barricade | Available (Psychic exception) | Suppressed (Dragon) | Available (Psychic exception) |
| Flutter Mane | Flutter Mane Midnight Fluttering | Available | Available | Available |
| Wobbuffet or Flutter Mane facing Hooded Thorns | Both sources remain effective | Suppressed | Suppressed | Suppressed |

Stealthy Hood on opponent's Thorns prevents opposing Ability effects on that holder, so either counter cannot silence Initialization. Jamming Tower disables Hood, restoring each counter's one-way source-to-source suppression edge. Neither matchup is an ambiguous reciprocal lock cycle.

## Time-boundary implications

With Active Wobbuffet, the Shadow Rider player can operate Psychic Underworld Door if VMAX was already established. Bide Barricade itself prevents Dragon Radiant Eternatus from triggering Climactic Gate if Eternatus is played onto the Bench while Wobbuffet remains Active.

A direct Wobbuffet Active-to-Bench pivot turns off Bide Barricade, at which point an effective opposing Active Iron Thorns resumes Initialization. Thus exchanging Wobbuffet for Flutter Mane in a Radiant launch search line is unsound without a separate suppression effect. In a different line, the player can first prepare and charge a VMAX under Active Wobbuffet and then pivot to attack, if sufficient Energy and legal switching are available.

Active Flutter Mane instead suppresses only the opponent's Active Ability. It allows the Radiant Eternatus Ability at the moment of Bench entry and can continue suppressing Thorns over the subsequent turn if it survives and stays Active, matching the distinct continuation analyzed in results/tests/shadow_rider_thorns_continuation/.

Latias ex is itself Psychic, so Skyliner remains available under Wobbuffet and can make a Basic Wobbuffet's ordinary Retreat Cost zero. The regression verifies Ability availability, not whether Latias has actually been found and Benched, nor the once-per-turn retreat budget.

## Reproduction and limitations

Run results/wobbuffet_flutter_thorns_continuation/reproduce.py. This source-text and exact-board regression checks Wobbuffet, all three Flutter prints, Iron Thorns, VMAX, Eternatus, and Latias; then compares resulting live source sets, suppression targets, Hood, and Jamming Tower.

It does not evolve VMAX, play Radiant Eternatus, spend Supporters, enforce Bench entry timing, select Prizes, model damage, or simulate matches. Its temporal conclusions follow stated active-position dependencies plus the official rule that hand-to-Bench trigger Abilities are checked on entry. Deck-building payoff cannot be inferred from this conditional witness alone.
