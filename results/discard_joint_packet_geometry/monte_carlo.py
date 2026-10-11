"""Physical independent 53-card dual-packet shuffle after typed discard."""
import json
from math import sqrt
from random import Random
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from discard_joint_packet_probability import joint_packet_hit


def run(db,dt,quota=6,trials=200000,seed=20261128):
    rng=Random(seed)
    remaining=["B"]*(4-db)+["T"]*(4-dt)+["F"]*(45-(3-db-dt))
    success=0
    for _ in range(trials):
        rng.shuffle(remaining)
        subset=remaining[:quota]
        success+=int("B" in subset and "T" in subset)
    observed=success/trials
    exact=float(joint_packet_hit(50,4-db,4-dt,quota))
    sigma=sqrt(max(exact*(1-exact),1/trials)/trials)
    assert abs(observed-exact)<6*sigma+1/trials
    return {
        "discarded_B":db,"discarded_T":dt,"draw_quota":quota,
        "trials":trials,"observed_joint_percent":round(observed*100,7),
        "exact_joint_percent":round(exact*100,7)
    }


if __name__=="__main__":
    print(json.dumps([
        run(0,0,seed=20261128),
        run(1,0,seed=20261129),
        run(1,1,seed=20261130)
    ],indent=2))
