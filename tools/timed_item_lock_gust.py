"""Finite deck Boss/defender-Switch chance minimax with turn-indexed Item permission."""
from fractions import Fraction
from functools import lru_cache

Pokemon = tuple[int,int]  # prize, hits


@lru_cache(None)
def attacker_draw(active: Pokemon, bench: tuple[Pokemon,...], boss_hand: int,
                  boss_deck: int, filler_a: int, switch_hand: int, switch_deck: int,
                  filler_d: int, allowed_turns: tuple[bool,...], elapsed: int=0,
                  needed: int=6) -> Fraction:
    assert boss_deck+filler_a>=active[1]+sum(x[1] for x in bench)
    total = boss_deck+filler_a
    result = Fraction(0)
    if boss_deck:
        result += Fraction(boss_deck,total)*attacker_act(
            active,bench,boss_hand+1,boss_deck-1,filler_a,switch_hand,switch_deck,
            filler_d,allowed_turns,elapsed,needed)
    if filler_a:
        result += Fraction(filler_a,total)*attacker_act(
            active,bench,boss_hand,boss_deck,filler_a-1,switch_hand,switch_deck,
            filler_d,allowed_turns,elapsed,needed)
    return result


@lru_cache(None)
def attacker_act(active,bench,boss_hand,boss_deck,filler_a,switch_hand,
                 switch_deck,filler_d,allowed_turns,elapsed,needed):
    moves=[(active,bench,boss_hand)]
    if boss_hand:
        for i,p in enumerate(bench):
            rest=tuple(sorted((active,)+bench[:i]+bench[i+1:]))
            moves.append((p,rest,boss_hand-1))
    out=[]
    for (reward,hits),rest,held in moves:
        if hits==1:
            if reward>=needed or not rest:
                out.append(Fraction(1))
            else:
                out.append(1 + max(defender_draw(
                    p,rest[:i]+rest[i+1:],held,boss_deck,filler_a,
                    switch_hand,switch_deck,filler_d,allowed_turns,elapsed+1,
                    needed-reward) for i,p in enumerate(rest)))
        else:
            out.append(1+defender_draw(
                (reward,hits-1),rest,held,boss_deck,filler_a,
                switch_hand,switch_deck,filler_d,allowed_turns,elapsed+1,needed))
    return min(out)


@lru_cache(None)
def defender_draw(active,bench,boss_hand,boss_deck,filler_a,switch_hand,
                  switch_deck,filler_d,allowed_turns,elapsed,needed):
    total=switch_deck+filler_d
    assert total>0
    outcome=Fraction()
    if switch_deck:
        outcome+=Fraction(switch_deck,total)*defender_act(
            active,bench,boss_hand,boss_deck,filler_a,switch_hand+1,switch_deck-1,
            filler_d,allowed_turns,elapsed,needed)
    if filler_d:
        outcome+=Fraction(filler_d,total)*defender_act(
            active,bench,boss_hand,boss_deck,filler_a,switch_hand,switch_deck,
            filler_d-1,allowed_turns,elapsed,needed)
    return outcome


@lru_cache(None)
def defender_act(active,bench,boss_hand,boss_deck,filler_a,switch_hand,
                 switch_deck,filler_d,allowed_turns,elapsed,needed):
    options=[attacker_draw(
        active,bench,boss_hand,boss_deck,filler_a,switch_hand,switch_deck,
        filler_d,allowed_turns,elapsed,needed)]
    if switch_hand and (elapsed>len(allowed_turns) or allowed_turns[elapsed-1]):
        for i,p in enumerate(bench):
            others=tuple(sorted((active,)+bench[:i]+bench[i+1:]))
            options.append(attacker_draw(
                p,others,boss_hand,boss_deck,filler_a,switch_hand-1,switch_deck,
                filler_d,allowed_turns,elapsed,needed))
    return max(options)
