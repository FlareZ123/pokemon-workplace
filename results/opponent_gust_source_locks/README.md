# Temporary source locks change the value of mixed Boss/Counter arrivals

## Question and exact model

The [physical multi-source gust race](../multisource_opponent_gust_race/) allows either opposing Boss or Counter to be used immediately when its usual Prize gate allows. Actual paper Expanded has distinct action types: Boss's Orders is a Supporter, Counter Catcher is an Item. This study adds **exogenous source-class lock windows indexed by the opponent's next reply**.

The [exact rational solver](../../tools/opponent_source_lock_schedule.py) composes our optimal abstract Prize attacks, adversarial promotions, the opponent's optional pass, public source counts in hand, one opponent natural draw per reply, and fixed card-source locks. Boss copies held under Supporter lock and Counter copies held under Item lock stay held for potential later play. Opposing Counter still requires its remaining Prizes to exceed ours. The lock schedule is supplied from outside this model; it does not represent a particular in-play lock Pokémon, which could be removed by attacks or gusts.

## A controlled two-reply source deadline

We begin with Active worth one Prize and Bench (1,1,3), holding Boss + Counter. Our opponent has three Prizes remaining, Active worth two and Bench (2,2), and a physical Basic-valid 60-card opening with B Basic Pokémon and four combined Boss/Counter copies. All attacks are one-hit KOs. Winning for us requires three opposing two-Prize knockouts. Opponent can pass after our first KO to leave its Counter gate initially closed, then our second KO opens Counter for its second reply. An opposing gust reaching our three-Prize Bench target on either reply wins the opponent's game.

Four lock regimes, all applied on **opponent reply 2 only**, yield four exact source-arrival deadlines:

1. **No lock:** Boss or Counter by reply 2 can win.
2. **Item lock on reply 2:** Counter cannot be played during its first legal window, so only Boss seen by reply 2 can win.
3. **Supporter lock on reply 2:** Boss must arrive by reply 1; Counter can arrive by reply 2.
4. **Both locks on reply 2:** Boss must arrive by reply 1; Counter is unusable at its decisive window.

The natural first opponent reply remains unlocked in all four regimes. Counter is still illegal on that reply because of the Prize differential. In particular, a Counter card already drawn into the opponent's hand does not become an immediate threat when the Item window closes on the second reply.

## Exact four-source results

The percentages are **our** optimal modeled winning chances. B=4 Basic Pokémon in the opposing hypothetical 60-card deck.

| Opposing Boss / Counter | No lock | Item locked, reply 2 | Supporter locked, reply 2 | Both locked, reply 2 |
| --- | ---: | ---: | ---: | ---: |
| 0 / 4 | 54.2795% | 100.0000% | 54.2795% | 100.0000% |
| 1 / 3 | 54.2795% | 86.2053% | 55.4103% | 87.8956% |
| 2 / 2 | 54.2795% | 74.1054% | 56.5412% | 77.0696% |
| 3 / 1 | 54.2795% | 63.5185% | 57.6720% | 67.4074% |
| 4 / 0 | 54.2795% | 54.2795% | 58.8028% | 58.8028% |

A striking comparison: with four opposing Counters, a second-reply Item lock restores our certain win, while a Supporter lock leaves our win chance at 54.2795%. With four opposing Bosses, the item lock has no effect, while the Supporter lock increases our win chance to 58.8028%. For fixed four total gust copies, the no-lock column is identical across splits, while the locked columns make source-class allocation decisive.

## Independent exact formulas

Let F(B,G,k) be the probability of seeing at least one of G non-Basic sources by the first k natural draws, conditional on a Basic-valid opening (from [multi-copy access](../gust_copy_opening_access/)). Our win probability is:

- No lock: 1-F(B,4,2).
- Item lock on second reply: 1-F(B,b,2), where b is the number of Boss copies.
- Both locks on second reply: 1-F(B,b,1).

The Supporter-lock-only regime has a mixed *deadline*, rather than one uniform source-count threshold. We win only if **no Boss** was seen in the opening hand or first reply, and **no Counter** by the second. Let `A=C(60,7)-C(60-B,7)` be the accepted hand count and `A0=C(56,7)-C(56-B,7)` the accepted hand count with none of the four sources. Given such a source-free hand, the first of 53 post-hand cards must be a filler, and the second of 52 must avoid Counter. Therefore the exact chance we win is

`(A0/A) * (49/53) * ((52-c)/52)`,

where c is the number of Counter copies. The term for reply-2 Boss is allowed, since Boss is then locked. This expression agrees with the independently sequenced tactical solver.

The analysis averages uniformly over the six Prize cards. Its early source-arrival results are invariant under Prize count as long as two natural draws remain possible; the tactical Prize race still explicitly tracks both players' remaining Prize counts.

## Verification

The [reproducer](reproduce.py) independently enumerates 144 complete **ordered, labeled** ten-card opening/Prize/first-two-draw physical populations and checks their source-deadline outcomes against the adversarial tactical solver. A further 324 unrestricted-source static states exactly match the previous solver. Another 100 exact 60-card four-source computations match the independently derived formulas across B=4,8,12,16,20, all five Boss/Counter splits, and all four lock regimes.

Run `python -m results.opponent_gust_source_locks.reproduce` at repository root. Every probability is an exact Fraction, without simulation sampling.

## Scope

The source locks are exogenous and apply to specified reply numbers. Actual Item/Supporter locks may depend on Active Position, Ability suppression, removability, Pokémon Tools, and Trainer play quota. Those mechanisms are absent. The opponent source locations and draws remain publicly revealed in the general solver, and attacks ignore Energy, HP and damage. This is an exact controlled interaction among source identity, Prize gate, and arrival time, rather than a matchup win-rate prediction.

A future model should derive each reply's source eligibility from actual board objects, lock-causing Pokémon, and the order in which gust/KO actions change that board.