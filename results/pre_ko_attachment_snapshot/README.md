# KO-trigger attachment snapshot

## Question

Which physical attachment state should a Knock Out-triggered recovery effect see
when the attack that causes the Knock Out has already removed an attachment?

Implementation: `tools/pre_ko_attachment_snapshot.py`  
Regression: `results/pre_ko_attachment_snapshot/reproduce.py`

## Rules boundary

The attack-resolution order in the bundled Advanced Player's Rulebook places
ordinary effects outside damage before the Knock Out check.

The separate Knock Out process then applies effects activated by the Knock Out
before the Knocked Out Pokemon and its remaining attached cards leave play.

Therefore a KO trigger must inspect the board after earlier attack effects have
finished.

## Physical regression

The regression reuses the conserved three-card evolution-stack fixture from the
KO-routing work. Its Active Pokemon begins with:

- Basic Water Energy `water-1`;
- Basic Water Energy `water-2`;
- Double Colorless Energy `dce-a`;
- Muscle Band `band-a`.

An attack-phase transition discards `water-1` before the KO batch is prepared.

The prepared KO batch then contains only `water-2`, `dce-a`, and
`band-a` as attachments on the doomed Pokemon.

A Huntail Diver's Catch-like routing request that tries to recover both
`water-1` and `water-2` is rejected because `water-1` is no longer
attached. A request for only `water-2` succeeds.

After KO disposal:

- one Basic Water Energy is in discard from the earlier attack effect;
- one Basic Water Energy is in hand from the KO recovery;
- Double Colorless Energy and Muscle Band are in discard;
- every card-class total is conserved.

## Finding

Trigger eligibility must be evaluated against the state at the trigger boundary,
not against the state that existed when the attack was announced.

This matters for the 216 damaging attachment-removal signatures catalogued in
`pre_ko_attachment_removal`. A static interaction graph can correctly notice
that a KO recovery effect exists while still overestimating what material the
effect can recover.

The physical-state sequence should be:

`attack phase mutation -> KO check -> prepare KO batch -> KO triggers -> disposal`

Moving `prepare KO batch` earlier aliases cards that have already left the
Pokemon with cards that are still attached.

## Limits

`apply_attack_attachment_discard()` is a small physical transition. It does
not decide whether a particular card text can discard the selected attachment,
whether a coin flip succeeded, how much damage was dealt, or whether the target
is actually Knocked Out.

Those semantic decisions remain upstream. The result establishes the state
boundary those semantics must feed.
