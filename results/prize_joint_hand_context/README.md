# Full hidden hand composition may depend on deck top and Prize worlds

## Question and scope

The existing private Prize-hand expansion assumes the other cards in the hand are conditionally independent of the deck top and remaining Prize positions, given the class of the Prize-derived card. That assumption is convenient and can be false in a finite deck. This study retains a separate distribution of other-hand card classes for every hidden (deck top, remaining Prizes, tagged Prize class) world and observer.

Implementation: `tools/prize_joint_hand_context.py`. Regression: `results/prize_joint_hand_context/reproduce.py`. The resulting beliefs feed directly into the existing physical random-hand-discard executor and preserve card-instance conservation and observer support for the true world.

## Independently enumerated witness

A face-down Chansey Prize was taken after declining its optional Lucky Bonus. The four initial (top, tag) worlds have probabilities 2/5, 1/10, 1/10, 2/5 for (S,C), (F,C), (S,O), (F,O). A decline has probability 2/5 for tag C, and 1 for tag O. The affected hand then holds the tagged card and one other card. The observer's probability that the other card is C depends on the full world:

| Hidden (top, tag) | P(other C) |
| --- | ---: |
| (S,C) | 1 |
| (F,C) | 0 |
| (S,O) | 1/2 |
| (F,O) | 1/4 |

The actor's exact physical world is (S,C,other C). The opponent sees one uniformly random hand card publicly discarded as C, while the actor knows which physical copy was discarded. An independent exact-rational enumeration gives:

| Quantity conditioned on public discard C | Full joint model | Collapsed tag-only model |
| --- | ---: | ---: |
| P(tagged Prize class C) | 12/17 | 12/17 |
| P(top card class S) | **37/51 = 72.55%** | **53/85 = 62.35%** |
| P(tagged card remains in hand) | 31/51 | 31/51 |

The top-card inference differs by **26/255 = 10.20 percentage points**. A tag-only model that correctly marginalizes the other-hand distribution still reproduces the tagged-card and survival probabilities. Thus testing only tag marginals misses the error. The proof enumerates both physically distinct copies and all hidden worlds rather than using the new expansion implementation as its oracle.

## Validation and limits

Both possible physical C discard origins pass the same opponent posterior, the actor observes which copy left the hand, and the ledger conserves instances. Missing hidden-world hypotheses and unnormalized conditionals are rejected. The new expansion is intentionally opt-in, preserving older API semantics.

These are hypothetical conditional beliefs and a uniform-random-discard observation. Their frequencies and behavioral assumptions are not tournament data or estimated match wins. Known card-copy conservation should eventually constrain admissible joint hypotheses, and actual discard effects have their own payment, timing and play restrictions.

## Strategic implication

The class of a public discard can change the estimated contents of an otherwise unseen deck even when the tagged Prize identity posterior is unchanged. A card-search or draw decision based on a tag-only posterior can therefore select the wrong line. Preserve joint hidden-zone correlations until the utility-relevant marginal has been calculated.
