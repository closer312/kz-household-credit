\
\
\

import numpy as np
import pandas as pd
from config import (DATA_DIR, OUT, YEARS, QUARTERS, KODNU12, INCOME, SOCIAL, read)

num = lambda s: pd.to_numeric(s, errors="coerce")

def roster(year):
    r = read(f"d008/{year}/kontr_k.csv")
    r["NOMP"] = num(r["NOMP"])
    hh = r.groupby("NOMER").agg(persons=("NOMP", "size")).reset_index()
    head = r[r["RODSTVO"].str.lstrip("0") == "1"].drop_duplicates("NOMER")
    head = head[["NOMER", "POL", "UROV"]].rename(columns={"POL": "head_sex", "UROV": "head_edu"})
    if "GOD_ROJD" in r:
        r["age"] = year - num(r["GOD_ROJD"])
        a = r.groupby("NOMER").agg(children=("age", lambda x: (x < 18).sum()),
                                   elderly=("age", lambda x: (x >= 63).sum()))
        head_age = r[r["RODSTVO"].str.lstrip("0") == "1"].drop_duplicates("NOMER")[["NOMER", "age"]]
        hh = hh.merge(a.reset_index(), on="NOMER", how="left").merge(
            head_age.rename(columns={"age": "head_age"}), on="NOMER", how="left")
    return hh.merge(head, on="NOMER", how="left")

def quarter(year, q):
    base = f"d004/{year}/{q}"
    hh = read(f"{base}/kv_vopr0.csv")[["NOMER", "TE", "K", "KVARTAL", "GOD"]]

    inc = read(f"{base}/kv_vopr11.csv")
    g = inc[[f"GR{k}" for k in INCOME]].apply(num).fillna(0)
    g.columns = [INCOME[k] for k in INCOME]
    g["NOMER"] = inc["NOMER"]
    g = g.groupby("NOMER").sum()
    g["social_transfers"] = g[[INCOME[k] for k in SOCIAL]].sum(axis=1)
    g["income"] = g.drop(columns=["of_which_agri_sales", "social_transfers"]).sum(axis=1)
    g = g[["income", "wage", "self_employed", "pension", "social_transfers"]].reset_index()

    sp = []
    for t in range(1, 8):
        d = read(f"{base}/kv_vopr{t}.csv", usecols=["NOMER", "STOIMK"])
        sp.append(d.assign(STOIMK=num(d["STOIMK"])).groupby("NOMER")["STOIMK"].sum().rename(f"sp{t}"))
    sp = pd.concat(sp, axis=1).fillna(0)
    sp["spending"] = sp.sum(axis=1)
    sp = sp.rename(columns={"sp1": "sp_nonfood", "sp2": "sp_utilities"})[["spending", "sp_nonfood", "sp_utilities"]].reset_index()

    b = read(f"{base}/kv_vopr12.csv")
    amt = b[b["NOMVNEW"] == "20"].copy()
    amt["item"] = amt["KODNU"].str.strip().str.rstrip(",").map(KODNU12)
    amt["v"] = num(amt["STOIMK"])
    amt = amt.pivot_table(index="NOMER", columns="item", values="v", aggfunc="sum").reset_index()
    ans = b[b["NOMVNEW"].isin(["21", "22"])].copy()
    ans["col"] = np.where(ans["NOMVNEW"] == "21", "purpose_", "source_") + ans["KOD"].str.strip()
    ans = pd.crosstab(ans["NOMER"], ans["col"]).clip(upper=1).reset_index()

    out = (hh.merge(g, on="NOMER", how="left").merge(sp, on="NOMER", how="left")
             .merge(amt, on="NOMER", how="left").merge(ans, on="NOMER", how="left"))
    return out

def main():
    frames = []
    for y in YEARS:
        ros = roster(y)
        for q in QUARTERS:
            if not (DATA_DIR / f"d004/{y}/{q}").exists():
                continue
            d = quarter(y, q).merge(ros, on="NOMER", how="left")
            frames.append(d)
            print(y, q, len(d))
    df = pd.concat(frames, ignore_index=True)
    fill0 = [c for c in df if c.startswith(("purpose_", "source_"))] + list(
        {"credit_received", "credit_repaid", "savings_used", "informal_borrowed",
         "informal_repaid", "debt_returned_to_hh"})
    for c in fill0:
        if c not in df:
            df[c] = 0
        df[c] = df[c].fillna(0)
    for c in ["income", "wage", "self_employed", "pension", "social_transfers", "spending", "sp_nonfood", "sp_utilities"]:
        df[c] = df[c].fillna(0)
    df["year"] = df["GOD"].astype(int)
    df["q"] = df["KVARTAL"].astype(int)
    df.to_csv(OUT / "hh_quarter.csv.gz", index=False)
    print(df.shape)

if __name__ == "__main__":
    main()
