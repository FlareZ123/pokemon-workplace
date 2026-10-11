"""Exhaustive two-packet typed discard and density counterexample."""
from fractions import Fraction
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from discard_joint_packet_probability import joint_packet_hit,packet_discard_change


def run():
    checked=non_target_cases=0
    for N in range(3,21):
        for B in range(1,N):
            for T in range(1,N-B+1):
                neutral=N-B-T
                for m in range(1,min(4,N-2)+1):
                    for db in range(min(B,m)+1):
                        for dt in range(min(T,m-db)+1):
                            if not 0<=m-db-dt<=neutral:
                                continue
                            for n in range(1,min(6,N-m)+1):
                                d=packet_discard_change(N,B,T,n,m,db,dt)
                                assert 0<=d["before"]<=1
                                assert 0<=d["after"]<=1
                                if db==dt==0:
                                    assert d["after"]>=d["before"]
                                    non_target_cases+=1
                                checked+=1
    witness=packet_discard_change(10,1,1,2,6,1,0)
    assert witness["before"]==Fraction(1,45)
    assert witness["after"]==0
    assert Fraction(1,4)>Fraction(2,10) # total packet density rises

    lines=[]
    for n in (4,6):
        for db,dt in ((0,0),(1,0),(0,1),(1,1),(2,0),(0,2)):
            z=packet_discard_change(53,4,4,n,3,db,dt)
            lines.append({
                "draws":n,"discarded_B":db,"discarded_T":dt,
                "baseline_joint_percent":round(float(z["before"])*100,8),
                "after_joint_percent":round(float(z["after"])*100,8),
                "change_pp":round(float(z["change"])*100,8)
            })
    return {
        "exact_states_checked":checked,
        "non_target_only_cases":non_target_cases,
        "density_failure_witness":{
            "N":10,"B":1,"T":1,"draws":2,
            "discarded_total":6,"discarded_B":1,"discarded_T":0,
            "original_joint":"1/45","after_joint":"0",
            "total_B_T_density_before":"1/5",
            "total_B_T_density_after":"1/4"
        },
        "illustrative_B4_T4":lines
    }


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
