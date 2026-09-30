import numpy as np
import pandas as pd
from config import OUT, RES, PURPOSE, PURPOSE_GROUP, SOURCE, REGION, DATA_DIR, INCOME

df = pd.read_csv(OUT / "hh_quarter.csv.gz", dtype={"NOMER": str, "TE": str, "K": str,
                                                   "head_sex": str, "head_edu": str})

df["urban"] = (df["K"] == "1").astype(int)
df["pc_income"] = df["income"] / df["persons"]
df["new_credit"] = (df["credit_received"] > 0).astype(int)
df["new_informal"] = (df["informal_borrowed"] > 0).astype(int)
df["repaying"] = (df["credit_repaid"] > 0).astype(int)
df["debt_service"] = df["credit_repaid"] + df["informal_repaid"]
df["dsr"] = np.where(df["income"] > 0, df["debt_service"] / df["income"], np.nan)
df["answered_purpose"] = (df.filter(like="purpose_").sum(axis=1) > 0).astype(int)
for g in sorted(set(PURPOSE_GROUP.values())):
    cols = [f"purpose_{k}" for k, v in PURPOSE_GROUP.items() if v == g and f"purpose_{k}" in df]
    df["pg_" + g] = (df[cols].sum(axis=1) > 0).astype(int)
df["src_bank"] = df.get("source_2", 0)
df["src_nonbank"] = ((df.get("source_1", 0) + df.get("source_7", 0) + df.get("source_8", 0)) > 0).astype(int)
df["region"] = df["TE"].map(REGION).fillna(df["TE"])

df["quint"] = df.groupby(["year", "q"])["pc_income"].transform(
    lambda s: pd.qcut(s.rank(method="first"), 5, labels=[1, 2, 3, 4, 5])).astype(int)

rep = df[df.repaying == 1]
t1 = df.groupby("year").agg(
    households=("NOMER", "nunique"),
    share_new_credit=("new_credit", "mean"),
    share_new_informal=("new_informal", "mean"),
    share_repaying=("repaying", "mean"),
    median_income_q=("income", "median"),
).join(df[df.new_credit == 1].groupby("year")["credit_received"].median().rename("median_new_credit"))\
 .join(rep.groupby("year")["dsr"].median().rename("median_dsr_repayers"))\
 .join(rep.groupby("year")["dsr"].apply(lambda s: (s > .3).mean()).rename("share_dsr_gt30_repayers"))
t1.round(4).to_csv(RES / "t5_trend_by_year.csv")

ans = df[df.answered_purpose == 1]
pur = ans.groupby("year")[[f"purpose_{k}" for k in PURPOSE]].mean()
pur.columns = [PURPOSE[c.split("_")[1]] for c in pur.columns]
pur.round(4).to_csv(RES / "t6_purpose_by_year.csv")
scols = [f"source_{k}" for k in SOURCE if f"source_{k}" in df]
src = ans.groupby("year")[scols].mean()
src.columns = [SOURCE[c.split("_")[1]] for c in src.columns]
src.round(4).to_csv(RES / "t7_source_by_year.csv")

d24 = df[df.year == 2024]
a24 = d24[d24.answered_purpose == 1]
t4 = d24.groupby("quint").agg(share_new_credit=("new_credit", "mean"),
                              share_new_informal=("new_informal", "mean"),
                              share_repaying=("repaying", "mean"),
                              median_pc_income=("pc_income", "median"))
t4 = t4.join(d24[d24.repaying == 1].groupby("quint")["dsr"].median().rename("median_dsr_repayers"))
t4 = t4.join(a24.groupby("quint")[[c for c in df if c.startswith("pg_")]].mean())
t4 = t4.join(a24.groupby("quint")[["src_bank", "src_nonbank"]].mean())
t4.round(4).to_csv(RES / "t8_by_income_quintile_2024.csv")

t5 = d24.groupby("region").agg(share_new_credit=("new_credit", "mean"),
                               share_repaying=("repaying", "mean"),
                               median_pc_income=("pc_income", "median"),
                               n=("NOMER", "size")).sort_values("share_repaying")
t5.round(4).to_csv(RES / "t3_by_region_2024.csv")
d24.groupby("urban")[["new_credit", "new_informal", "repaying"]].mean().round(4).to_csv(RES / "t4_urban_rural_2024.csv")

man = pd.read_csv(DATA_DIR / "MANIFEST.csv")
t0 = man.groupby("form").agg(tables=("table", "size"), rows_synthetic=("rows_synthetic", "sum"),
                             rows_real=("rows_real", "sum"))
t0["diff_pct"] = (t0.rows_synthetic / t0.rows_real - 1) * 100
t0.round(3).to_csv(RES / "t0_datasets.csv")

chk = df.groupby("year").agg(
    hh_quarter_rows=("NOMER", "size"),
    matched_to_roster=("persons", lambda s: s.notna().mean()),
    with_income_rows=("income", lambda s: (s > 0).mean()),
    with_spending_rows=("spending", lambda s: (s > 0).mean()),
    with_any_borrowing_row=("NOMER", lambda s: 0.0),
)
b = ((df[["credit_received", "credit_repaid", "savings_used", "informal_borrowed",
          "informal_repaid", "debt_returned_to_hh"]].sum(axis=1) > 0) | (df.answered_purpose == 1))
chk["with_any_borrowing_row"] = b.groupby(df["year"]).mean()
chk["children_known"] = df.groupby("year")["children"].apply(lambda s: s.notna().mean())
chk.round(4).to_csv(RES / "t1_quality_checks.csv")

inc = df.groupby("year")[["income", "wage", "self_employed", "pension", "social_transfers"]].sum()
share = inc[["wage", "self_employed", "pension", "social_transfers"]].div(inc["income"], axis=0)
share["other"] = 1 - share.sum(axis=1)
share = share.join(df.groupby("year")["pc_income"].median().rename("median_pc_income_q"))
share = share.join(df.groupby("year")["spending"].median().rename("median_spending_q"))
share.round(4).to_csv(RES / "t2_income_structure.csv")

for p in sorted(RES.glob("t*.csv")):
    print("\n##", p.name); print(pd.read_csv(p).to_string())
