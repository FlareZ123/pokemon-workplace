# Physical-card witness: Bellelba pays G&H while protecting a Ticket

## Why this witness matters

In the larger, exactly reweighted Aichi conditional sample, allowing
the supplemental Tag Call to search Bellelba & Brycen-Man sometimes
improves first-reset access beyond the benefit of simply removing
Bellelba from the deck.

The effect was rare, but the result is a **constructive physical
60-card state**: one named TAG TEAM Supporter fetched by Tag Call
is used as a Guzma & Hala (G&H) discard-payment card. That choice
preserves a held hypothetical Prize-reset Ticket which the
Bellelba-protected route would otherwise have to sacrifice.

Implementation: [reproduce.py](reproduce.py).
[Passing GitHub Actions validation 38062663291](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38062663291).

## Card count and counterfactual package

The underlying deck begins with the published Aichi runner-up
Vileplume list's named Pokémon, G&H4, Tag Call4,
Bellelba1, Artazon2, Jet Energy2, and related setup cards.

The agent4 first-reset model replaces four first-turn-neutral
Supporter slots with generic TechSlot cards. For this witness,
the two-Ticket/one-Map assignment designates a held **TechSlot2**
as a hypothetical Prize-reset Ticket.

The original published deck plays the corresponding Supporter
instead. This is a physically conserving **counterfactual tech
package**, not a claim that the published Aichi runner-up ran a Ticket.

## Exact physical opening and Prizes

The 60-card permutation is preserved by its physical-card indices in
the reproducer, where each index identifies a specific card instance
in tools/aichi_post_gnh_prize_reset.py. The drawn zones are:

| Zone | Named cards |
| --- | --- |
| Opening seven | Artazon; Bunnelby; Jirachi; Guzma & Hala; Jet Energy; Tag Call; TechSlot2 |
| Six hidden Prizes | Guzma & Hala; Mr. Mime; Jet Energy; Guzma & Hala; Guzma & Hala; Budew |
| Next natural draw | Pidgey |

The preparer selects Jirachi as Active and reserves the naturally
held G&H as the turn's Supporter. The resulting other hand cards are
Artazon, Bunnelby, Jet Energy, Tag Call, TechSlot2 and Pidgey.

Three other G&H copies are Prized. The singleton Bellelba is
searchable, and the early Jirachi Stellar Wish remains unused.

The first five cards that a hypothetical early Stellar Wish could
have looked at are Counter Gain, Bellelba, TM: Evolution,
Lillipup and Gladion. The model defers that Ability while the
natural G&H connection is available; G&H's deck search reshuffles
before the later Wish.

## The named action and three outcomes

The new line:

1. **Tag Call:** search the deck for the singleton
   Bellelba & Brycen-Man, move it to the hand and shuffle.
   This is a legal single TAG TEAM search under "up to 2."
   The full deck inspection also reveals that the other G&H
   copies are Prized.
2. **Guzma & Hala:** play the previously held G&H and discard
   the held Artazon and the just-searched Bellelba.
3. **G&H search:** fetch TM: Evolution and a replacement Artazon
   from the deck. Jet Energy was already held.
4. **Retain TechSlot2:** the hypothetical Ticket remains in hand,
   providing immediate access to the first Prize reset.

Three distinct local outcomes for the inherited
item_lock-plus-Pidgeot endpoint with two Tickets and one Map:

| Modeled option | First-reset access |
| --- | ---: |
| No additional searchable G&H, G&H-only route | 11.111111111% = 1/9 |
| Prior Tag Call fetches Bellelba, but Bellelba is protected against discard | 11.627906977% = 5/43 |
| Tag Call fetches Bellelba and G&H discards it with Artazon | **100%** |

The local payoff from relaxing Bellelba's discard protection is

\[
1-\frac5{43}=\frac{38}{43}=88.372093023\text{ percentage points}.
\]

The difference between 1/9 and 5/43 comes from thinning the
searchable deck by one card before late Stellar Wish. The far
larger improvement to 100% comes from the two-card G&H payment
that preserves an already-held Ticket.

There is no use of a second Supporter on that turn. Bellelba
is a searched physical discard card, and the real turn's
Supporter is the already-held G&H. This line requires a turn
where playing G&H is permitted, such as going second on turn one.

## Validation

The reproducer asserts:

- a unique permutation of all 60 physical card instances;
- precisely the opening, six Prizes, next draw, and eligible
  Jirachi board state above;
- zero G&H and one Bellelba physically remaining searchable;
- ordinary held extra Tag Call and an unused later Stellar Wish;
- the G&H-only route has no extra searchable G&H target;
- the Bellelba fetch moves a card to hand and consumes Tag Call;
- an endpoint-preserving G&H payment specifically discards
  Artazon and Bellelba;
- all required TM/Energy/Artazon outputs and the Ticket remain
  available after that payment;
- first-reset access equals 1/9, 5/43 and 1 under the
  three permitted policies.

This is an **existence proof within the stated simulator**.
The sampled prevalence of the state family is much less
certain, and the physical witness is selected from a larger
conditional Monte Carlo run.

## Interpretation and next tests

The rare line combines search-target diversification,
irreversible payment, replacement Stadium access, and
preservation of a high-value Item slot. It illustrates why
counting search connectors without modeling which cards
are consumed can miss discrete winning-resource paths.

Bellelba normally contributes important later control utility.
Discarding it simply for a first-reset access improvement may
be strategically poor in a real game, especially when the
control matchup requires Bellelba. This abstract score
does not evaluate that tradeoff.

The model also omits opponent pressure, actual evolution
execution and future turn timing. Further work should
calculate a confidence interval for the tiny aggregate
Bellelba-payment premium and compare it with the
larger, better-supported deck-thinning component.
