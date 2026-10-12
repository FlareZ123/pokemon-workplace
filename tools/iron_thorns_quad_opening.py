"""Exact four-Iron-Thorns opening access using grouped and independent labelled oracles."""
from __future__ import annotations
from fractions import Fraction
from itertools import product
from math import comb

def choose(n: int, k: int) -> int:
    return comb(n,k) if 0<=k<=n else 0

def grouped_opening_access() -> dict[str, Fraction]:
    """Four Basics, two Tag Call, two Guzma & Hala, DCE, Thunder Mountain, 50 other."""
    den=choose(60,7)*choose(53,6)
    valid=route=direct=0
    for basic in range(5):
      for tag in range(3):
       for gh in range(3):
        for dce in range(2):
         for stadium in range(2):
          other=7-basic-tag-gh-dce-stadium
          ways=choose(4,basic)*choose(2,tag)*choose(2,gh)*choose(1,dce)*choose(1,stadium)*choose(50,other)
          if ways==0 or basic==0:continue
          valid+=ways*choose(53,6)
          if dce==1 and stadium==1:direct+=ways*choose(53,6)
          if tag+gh==0:continue
          other_remaining=53-(2-gh)-(1-dce)-(1-stadium)
          for prized_gh in range(3-gh):
           if gh==0 and prized_gh==2:continue
           route+=ways*choose(2-gh,prized_gh)*choose(other_remaining,6-prized_gh)
    return {
        "valid_seven":Fraction(valid,den),
        "gh_route_cond_valid":Fraction(route,valid),
        "direct_dce_thunder_cond_valid":Fraction(direct,valid),
        "expected_own_mulligans":Fraction(den-valid,valid),
    }

def independent_labeled_oracle() -> dict[str, Fraction]:
    """Assign each relevant physical card to hand, Prize or deck; aggregate 50 others."""
    labels=("B","B","B","B","TAG","TAG","GH","GH","DCE","THUNDER")
    den=choose(60,7)*choose(53,6)
    valid=route=direct=0
    for zones in product(range(3),repeat=len(labels)):
        num_hand=sum(z==0 for z in zones)
        num_prized=sum(z==1 for z in zones)
        other_hand=7-num_hand
        other_prized=6-num_prized
        ways=choose(50,other_hand)*choose(50-other_hand,other_prized)
        if ways==0:continue
        held={labels[i] for i,z in enumerate(zones) if z==0}
        if "B" not in held:continue
        valid+=ways
        if "DCE" in held and "THUNDER" in held:direct+=ways
        prizes={labels[i] for i,z in enumerate(zones) if z==1}
        if "DCE" in prizes or "THUNDER" in prizes:continue
        if not ("TAG" in held or "GH" in held):continue
        if "GH" not in held and not any(labels[i]=="GH" and z==2 for i,z in enumerate(zones)):continue
        route+=ways
    return {
        "valid_seven":Fraction(valid,den),
        "gh_route_cond_valid":Fraction(route,valid),
        "direct_dce_thunder_cond_valid":Fraction(direct,valid),
        "expected_own_mulligans":Fraction(den-valid,valid),
    }
