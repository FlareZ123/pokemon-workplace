"""Exact Tag Call material acquisition and conditional G&H Tool-replacement value.

Toy: one essential held Tool, b identical-name backup Tools, one sought
Ticket, g otherwise unneeded TAG TEAM Supporters, and filler among U
unknown cards; P cards are uniformly Prized. A saved Jirachi Stellar Wish
samples s cards from the shuffled deck. G&H itself is already in hand.

An optional Tag Call searches at most two additional TAG TEAM Supporters,
removes those cards from the deck, and establishes K1 before G&H's optional
payment. K1 permits replacing the held Tool only when a backup and target
are both known searchable. Other G&H outputs/requirements are exogenous.
In worlds with no searched Supporter, this optimistic upper-bound model
declines the Tag Call; a real presearch player cannot know this at K0.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb


@dataclass(frozen=True)
class Bounds:
    keep_joint: Fraction
    tag_material_joint: Fraction
    tag_full_joint: Fraction
    tag_playable: Fraction
    tag_material_lift: Fraction
    conditional_tool_replacement_lift: Fraction


def model(
    unseen: int, prizes: int, sample_size: int,
    backup_tools: int, gnh_searchable_pool: int,
) -> Bounds:
    """Exact weighted Prize-category enumeration, no Monte Carlo."""
    u,p,s,b,g = unseen,prizes,sample_size,backup_tools,gnh_searchable_pool
    filler = u-b-g-1  # plus exactly one designated Ticket target
    d=u-p
    if not (b>=1 and g>=0 and filler>=0 and p>=0 and
            d>=s+min(2,g)+1 and s>=1):
        raise ValueError("Invalid physical population or Wish sample")
    total=comb(u,p)
    keep=material=full=playable=Fraction()
    for bp in range(max(0,p-(u-b)),min(b,p)+1):
        for tp in range(2):
            for gp in range(max(0,p-bp-tp-filler),min(g,p-bp-tp)+1):
                fp=p-bp-tp-gp
                if fp<0 or fp>filler:
                    continue
                weight=Fraction(
                    comb(b,bp)*comb(1,tp)*comb(g,gp)*comb(filler,fp),
                    total
                )
                backups=b-bp
                ticket=1-tp
                g_available=g-gp
                removed=min(2,g_available)
                keep+=weight*ticket*Fraction(s,d)
                if removed:
                    playable+=weight
                    material+=weight*ticket*Fraction(s,d-removed)
                    if backups and ticket:
                        full+=weight*Fraction(s,d-removed-1)
                    else:
                        full+=weight*ticket*Fraction(s,d-removed)
                else:
                    material+=weight*ticket*Fraction(s,d)
                    full+=weight*ticket*Fraction(s,d)
    assert material>=keep
    assert full>=material
    return Bounds(keep,material,full,playable,material-keep,full-material)


def brute_force(
    unseen: int, prizes: int, sample_size: int,
    backup_tools: int, gnh_searchable_pool: int,
) -> Bounds:
    """Enumerate independent labeled physical Prize subsets."""
    u,p,s,b,g=unseen,prizes,sample_size,backup_tools,gnh_searchable_pool
    d=u-p
    if d<s+min(2,g)+1 or u-b-g-1<0:
        raise ValueError("Invalid population")
    keep=material=full=playable=Fraction()
    worlds=0
    for prized in combinations(range(u),p):
        ps=set(prized)
        backups=sum(i not in ps for i in range(b))
        ticket=int(b not in ps)
        g_count=sum(i not in ps for i in range(b+1,b+g+1))
        m=min(2,g_count)
        keep+=ticket*Fraction(s,d)
        if m:
            playable+=1
            material+=ticket*Fraction(s,d-m)
            full+=ticket*Fraction(s,d-m-int(backups>0 and ticket>0))
        else:
            material+=ticket*Fraction(s,d)
            full+=ticket*Fraction(s,d)
        worlds+=1
    keep/=worlds
    material/=worlds
    full/=worlds
    playable/=worlds
    return Bounds(keep,material,full,playable,material-keep,full-material)


def output(
    unseen: int = 52, prizes: int = 6, sample_size: int = 5,
    backup_tools: int = 1,
) -> str:
    lines=[
        f"U={unseen}, P={prizes}, s={sample_size}, backup_tools={backup_tools}",
        "extra G&H | TagCall output possible% | keep% | material% | "
        "material+K1% | material lift pp | K1 allowed-replacement lift pp",
    ]
    for g in (0,1,2,3):
        x=model(unseen,prizes,sample_size,backup_tools,g)
        lines.append(
            f"{g} | {100*float(x.tag_playable):.9f} | "
            f"{100*float(x.keep_joint):.9f} | "
            f"{100*float(x.tag_material_joint):.9f} | "
            f"{100*float(x.tag_full_joint):.9f} | "
            f"{100*float(x.tag_material_lift):+.9f} | "
            f"{100*float(x.conditional_tool_replacement_lift):+.9f}"
        )
    return "\n".join(lines)


if __name__=="__main__":
    print(output())
