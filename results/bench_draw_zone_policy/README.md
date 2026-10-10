# Adaptive Crobat/Dedenne policy changes with target destination value

## Question

When an important singleton K is found, should the player stop drawing to keep it, or use Dedenne-GX's Dedechange to place it into the discard pile? Cards that are useful as attack-copy payloads, such as some Dragons in Regidrago-style decks, can have higher value in the discard pile. This is a direct case where a single scalar “accessed target” event loses information about the destination and subsequent actions.

This experiment computes an exact nonanticipative within-turn policy frontier for target K using Crobat V, Dedenne-GX, and finite Bench capacity. It adds a hypothetical reward for final-hand K, a separate reward for discarded K, and a penalty per extra support Pokémon benched.

[Optimal policy kernel](../../tools/bench_draw_zone_policy.py) and [independent material-zone regression](reproduce.py).

## Rules and bounded state

The bundled cards supply these exact concepts: Crobat V's hand-to-Bench Dark Asset draws until the hand contains six, preserving cards already held; Dedenne-GX's hand-to-Bench Dedechange discards the remaining hand and draws six. The single K has one of three final statuses: in hand, discarded, or still elsewhere. Both support Basics are already retained in hand; two Bench slots are available and the Abilities are legal to use. A support Pokémon benched remains an exposed two-Prize liability until removed by another action, which is outside this model.

Baseline: a valid opening in which K is absent, one later normal draw, six hidden Prizes and 46 live-deck cards. Thus K is uniform among N=53 locations. After prior non-target hand reduction, Crobat's Dark Asset would draw a=2 cards. The player observes whether K is held before support actions and after Crobat's draw. The player does not know which unknown location contains K before a search.

Allowed actions: stop, Dedenne immediately, or Crobat first, followed by a choice to stop or play Dedenne after seeing whether Crobat drew K. A previously drawn K permits stopping immediately or Dedenne to discard it. No third support, pickup, search, or other tactical utility is modeled.

## Utility and nonanticipative dynamic value

Assign final K in hand reward **H**, final K in discard reward **G**, and per-Bench-support occupancy cost **C**, each nonnegative. For a policy \(\pi\),

\[
U(\pi)=H P_{\pi}(K\text{ in hand})+
G P_{\pi}(K\text{ discarded})-
C\, E_{\pi}[\text{new Bench occupants}].
\]

Let r denote cards drawn before the support decision, a the initial Crobat draw width, and N the total originally unseen target locations. Assume the live deck is large enough to complete both a-card and six-card draws. The target-only value upon already holding K is

\[
V_{\mathrm{held}}=\max(H,G-C).
\]

If K is still unknown, using Dedenne directly has value

\[
V_D=\frac{6H}{N-r}-C,
\]

while staging Crobat and subsequently choosing optimally has value

\[
V_C=-C+\frac{a}{N-r}V_{\mathrm{held}}
+\frac{N-r-a}{N-r}
\max\!\left(0,\frac{6H}{N-r-a}-C\right).
\]

The optimal expected value is

\[
V^*=\frac{r}{N}V_{\mathrm{held}}+
\frac{N-r}{N}\max(0,V_D,V_C).
\]

The envelope respects observation timing. It does not permit a player to choose different actions based on whether an unseen K is Prized versus located deep in their deck.

## Exact example at hand size five

Here \(N=53,r=1,a=2\), and set \(H=1\). Values of G and C in the table are **hypothetical relative utilities**, not estimated match statistics.

| Discard value G | Bench cost C | Optimal action if K is missing before support | K in hand | K discarded | Expected added Bench bodies |
| ---: | ---: | --- | ---: | ---: | ---: |
| 0 | 0 | Crobat; Dedenne only if K remains missing | 9/53 | 0 | 102/53 |
| 0 | 0.04 | Dedenne immediately | 7/53 | 0 | 52/53 |
| 2 | 0 | Crobat; Dedenne even if it finds K | 6/53 | 3/53 | 105/53 |
| 2 | 0.04 | Crobat; Dedenne even if it finds K | 6/53 | 3/53 | 105/53 |
| 2 | 0.10 | Dedenne immediately | 6/53 | 1/53 | 1 |

When G=0, the point where adding Crobat ceases to be strictly worthwhile under this narrow objective is

\[
C/H=\frac{a}{N-r-a}=\frac2{50}=4\%.
\]

At that tie the optimizer prefers Dedenne alone because it occupies fewer Bench slots.

When G=2H, spending another Bench slot to move Crobat-drawn K into discard can be worthwhile at C=4% even though the hand-only policy would already choose Dedenne directly. A K held before any support action can be discarded with Dedenne alone, saving Crobat's additional body. The gain depends on the destination that the target requires in the current game state.

## Verification

The exact implementation evaluates all 24 observable deterministic policy branches over all 53 possible target locations, recording final target zone, number of support bodies, and utility as rational numbers. An independent reproducer constructs physical hands, Prize partitions, shuffled decks, Bench and discard lists; it tests conservation of the unique K after all transitions. The resulting four metrics agree with the primary policy evaluator.

For varying earlier draws, Prize counts, live-deck sizes, Crobat draw widths and utility weights, a separate closed-form decision-tree envelope also agrees with the best enumerated policy. The regression checks **2,898** independent policy/utility cases plus the displayed benchmark points.

Run \`python results/bench_draw_zone_policy/reproduce.py\`.

## Strategic use and limitations

This model formalizes one aspect of the human-developed DCI/AMR distinction: when a card is needed as a discard-pile attack payload, the same draw/discard sequence can have a different value than when it is an indispensable hand-held card.

The utility coefficients are scenario inputs. The analysis does not value other cards Dedenne may discard, opponents' gust access to two-Prize Bench Pokémon, eventual recovery from discard, whether K is legally useful in discard, attack cost, Supporter contention, lock effects, or the likelihood of reaching the starting hand size. The simple value frontier is therefore an exact illustration of action and destination coupling, not a competitive deck optimization or win-rate estimate.
