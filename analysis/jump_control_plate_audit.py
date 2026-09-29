"""Audit of all-vehicle (DMSO-only) plates in JUMP cpg0016, from the public metadata.

Input : jump-cellpainting/datasets metadata folder (plate.csv.gz, well.csv.gz).
Output: data/jump_all_vehicle_plates.csv and a printed summary.
Finding (22 Sep 2026): 120 plates in 8 sources are entirely DMSO (46,077 wells).
Plate 1053600681 (source_2, batch 20210614_Batch_1) is one of 11 at its source; its
batch also holds 20 ordinary compound plates and one Target2 plate. JUMP types it
COMPOUND although every well is DMSO.
"""
import sys, pandas as pd
M = sys.argv[1] if len(sys.argv) > 1 else "metadata"
p = pd.read_csv(f"{M}/plate.csv.gz"); w = pd.read_csv(f"{M}/well.csv.gz")
p["Metadata_Plate"] = p.Metadata_Plate.astype(str); w["Metadata_Plate"] = w.Metadata_Plate.astype(str)
g = w.groupby("Metadata_Plate").agg(n=("Metadata_Well", "size"), dmso=("Metadata_JCP2022", lambda s: (s == "JCP2022_033924").sum()))
pp = p.merge(g, left_on="Metadata_Plate", right_index=True)
allD = pp[pp.dmso == pp.n]
print("all-vehicle plates:", len(allD), "wells:", int(allD.n.sum()), "sources:", allD.Metadata_Source.nunique())
print(allD.groupby(["Metadata_Source", "Metadata_PlateType"]).size())
allD.to_csv("data/jump_all_vehicle_plates.csv", index=False)
