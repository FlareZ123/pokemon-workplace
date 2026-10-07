# Harto Miki Raichu/Electrode: timed access to the backup Gladion

## Question

The two-Gladion belief result counts the visible Gladion as safely discardable whenever the backup copy is not Prized and some legal continuation exists.

How much of that redundancy is actually available **in time** after Quick Ball reveals that Alolan Raichu is Prized?

The gap is large.

Implementation: `tools/raichu_backup_gladion_timing.py`  
Regression: `results/raichu_backup_gladion_timing/reproduce.py`

## Conditioning

This result starts after a specific sequence boundary:

1. the visible Gladion was discarded for Quick Ball before deck inspection;
2. Quick Ball successfully found Crobat V, proving that Crobat was in deck;
3. the deck search reveals that Alolan Raichu is Prized.

At that point two identities are fixed:

- Alolan Raichu occupies one Prize slot;
- Crobat V occupied one deck position and has now been searched out.

Among the **50 remaining unresolved cards**:

- 5 occupy the remaining Prize slots;
- 45 occupy the post-search deck;
- one is the backup Gladion.

Therefore the backup Gladion is in deck with probability:

**45/50 = 90%**.

That 90% is a topology ceiling. It says a backup route exists somewhere in the deck, without implying that the card reaches hand before the current deadline.

## Random-access timing

Quick Ball leaves the representative hand at five cards after Crobat V enters the Bench, so Dark Asset has a one-card draw-to-six window.

Conditional on this state, the backup Gladion is equally likely to occupy any of the 50 unresolved locations. One Dark Asset draw covers exactly one of those locations.

| Random deck exposures after the search | Backup Gladion reached by then |
| ---: | ---: |
| 0 | 0% |
| 1 | **2%** |
| 2 | **4%** |
| 5 | 10% |
| 10 | 20% |
| 45 | 90% |

The same-turn Dark Asset line therefore reaches the backup in only **2%** of these post-search K1 states.

The gap between topological redundancy and same-turn random access is:

**90% - 2% = 88 percentage points**.

## Why the formula is simple

After conditioning, the backup singleton has 50 possible unresolved locations.

- 5 are inaccessible Prize locations;
- 45 are ordered deck locations.

Seeing `h` distinct random deck cards before the deadline succeeds exactly when the backup occupies one of those `h` exposed deck positions.

So for `0 <= h <= 45`:

`P(access by h exposures) = h / 50`.

The reproducer independently enumerates all 50 labeled locations and matches the analytic result exactly.

## Deterministic connector contrast

A Supporter-preserving deterministic any-card connector that is already executable after the Quick Ball search can reach the backup whenever it is in deck.

Its ceiling is therefore the full **90%** topology value rather than the 2% one-draw value.

This is the same structural distinction seen elsewhere in the repository:

`card exists outside Prizes != card is accessible before the deadline`.

The connector still needs its own payment and action-channel gates. The 90% figure assumes those have already been satisfied.

## DCI implication

Before the initial Quick Ball search, discarding the visible Gladion can look protected by the second copy.

After the search reveals Raichu is Prized, the strategic quality of that earlier discard depends on more than whether the backup survived the Prize cards. The backup must also become available before Gladion needs to be played.

This gives a three-layer representation of redundancy:

1. **copy redundancy**: another Gladion exists in the list;
2. **Prize topology**: the backup is outside Prizes;
3. **timed access**: the backup reaches hand before the rescue deadline.

A DCI model that stops at layer 1 or 2 can substantially overrate the safety of discarding the visible copy.

## Relation to the two-Gladion belief result

`raichu_two_gladion_belief_discard/` answers an existential hidden-world question: in what fraction of Prize worlds does any modeled continuation remain after discarding the visible Gladion?

This result answers a later timing question after Quick Ball has established K1 and the target is known Prized.

The percentages measure different objects:

- 98.868778% in the preceding result is hidden-world existential continuation safety under its grouped belief;
- 90% here is the post-search topology ceiling for the backup under the tighter conditioning;
- 2% is same-turn access through one random Dark Asset draw.

They should not be substituted for one another.

## Limits

This timing result deliberately isolates random exposure of the backup singleton.

It does not include Computer Search, Forest Seal Stone, VS Seeker, another targeted connector, Dedenne-GX, additional draw engines, shuffled redraw effects, Supporter lock, Bench failure, ordinary Prize-taking, or alternative attack lines.

The random exposures are without replacement from the post-search deck and assume no intervening shuffle that changes the uniform-order argument.

## Next useful work

The strongest continuation is to add concrete deterministic connector states.

For example, after K1 shows the backup Gladion is in deck:

- Computer Search can reach it if its two-card discard cost remains payable;
- Forest Seal Stone can reach it if Crobat V is in play, the Tool/VSTAR path is live, and the VSTAR Power remains unused.

That would decompose the 88-point timing gap into the portion recovered by real typed connectors versus the portion still stranded by payment or action gates.
