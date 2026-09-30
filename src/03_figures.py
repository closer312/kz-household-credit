import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from config import RES, FIG

BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
GREY, INK, MUTED = "#b9b8b2", "#0b0b0b", "#52514e"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GREY, "axes.labelcolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": .8, "axes.axisbelow": True,
    "figure.dpi": 150, "savefig.bbox": "tight", "figure.facecolor": "white",
})
PF = matplotlib.ticker.PercentFormatter(1, decimals=0)
title = lambda ax, t: ax.set_title(t, loc="left", color=INK, fontsize=12)

def save(fig, name):
    fig.savefig(FIG / name); plt.close(fig)

s = pd.read_csv(RES / "t2_income_structure.csv").set_index("year")
parts = [("wage", "Зарплата", BLUE), ("self_employed", "Самозанятость", ORANGE),
         ("pension", "Пенсии", AQUA), ("social_transfers", "Соц. пособия", YELLOW), ("other", "Прочее", MAGENTA)]
fig, ax = plt.subplots(figsize=(7.5, 3.4))
years = s.index.astype(str)[::-1]
left = pd.Series(0.0, index=s.index)
for col, lab, c in parts:
    v = s[col]
    ax.barh(years, v[::-1], left=left[::-1], color=c, label=lab, height=.62, edgecolor="white", linewidth=2)
    for y, (l, w) in zip(years, zip(left[::-1], v[::-1])):
        if w > .07:
            ax.text(l + w / 2, y, f"{w:.0%}", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    left += v
ax.xaxis.set_major_formatter(PF); ax.set_xlim(0, 1); ax.grid(False)
ax.legend(ncol=5, frameon=False, loc="upper left", bbox_to_anchor=(0, -.1), fontsize=9, handlelength=1)
title(ax, "Структура денежного дохода домохозяйств")
save(fig, "f1_income_structure.png")

r = pd.read_csv(RES / "t3_by_region_2024.csv").sort_values("share_repaying")
fig, ax = plt.subplots(figsize=(6, 6.2))
ax.barh(r.region, r.share_repaying, color=BLUE, height=.65)
for i, v in enumerate(r.share_repaying):
    ax.text(v + .005, i, f"{v:.0%}", va="center", fontsize=9, color=INK)
ax.xaxis.set_major_formatter(PF); ax.grid(axis="y", visible=False)
title(ax, "Доля семей, выплачивающих кредит, 2024")
save(fig, "f2_regions.png")

t1 = pd.read_csv(RES / "t5_trend_by_year.csv")
src = pd.read_csv(RES / "t7_source_by_year.csv").set_index("year").T
src = src[src.max(axis=1) > .005].sort_values(2024)
pur = pd.read_csv(RES / "t6_purpose_by_year.csv").set_index("year").T.sort_values(2024)
pur = pur[pur[2024] >= .02]
q = pd.read_csv(RES / "t8_by_income_quintile_2024.csv")

fig, axs = plt.subplots(2, 2, figsize=(12, 7.4))
a = axs[0, 0]
a.plot(t1.year, t1.share_new_credit, color=BLUE, lw=2, marker="o", ms=7)
for x, y in zip(t1.year, t1.share_new_credit):
    a.annotate(f"{y:.1%}", (x, y), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=10, color=INK)
a.set_xticks(t1.year); a.set_ylim(0, .065); a.yaxis.set_major_formatter(PF)
title(a, "Взяли новый кредит за квартал, % семей")

a = axs[0, 1]
y = range(len(src)); h = .38
a.barh([i + h / 2 for i in y], src[2021], height=h, color=GREY, label="2021")
a.barh([i - h / 2 for i in y], src[2024], height=h, color=BLUE, label="2024")
for i, v in enumerate(src[2024]):
    a.text(v + .01, i - h / 2, f"{v:.0%}", va="center", fontsize=9, color=INK)
a.set_yticks(list(y)); a.set_yticklabels(src.index); a.xaxis.set_major_formatter(PF); a.grid(axis="y", visible=False)
a.legend(frameon=False, loc="lower right"); title(a, "Источник средств (вопрос 2.2)")

a = axs[1, 0]
a.barh(pur.index, pur[2024], color=BLUE, height=.6)
for i, v in enumerate(pur[2024]):
    a.text(v + .01, i, f"{v:.0%}", va="center", fontsize=9, color=INK)
a.xaxis.set_major_formatter(PF); a.grid(axis="y", visible=False)
title(a, "Цель кредита, 2024 (вопрос 2.1)")

a = axs[1, 1]
a.bar(q.quint, q.median_dsr_repayers, color=ORANGE, width=.6)
for x, v in zip(q.quint, q.median_dsr_repayers):
    a.text(x, v + .008, f"{v:.0%}", ha="center", fontsize=10, color=INK)
a.yaxis.set_major_formatter(PF); a.grid(axis="x", visible=False)
a.set_xlabel("квинтиль дохода на чел. (1 = беднейшие)")
title(a, "Выплаты / доход у платящих (медиана), 2024")
fig.tight_layout(h_pad=2.2, w_pad=2.5)
save(fig, "f3_borrowing.png")
print(sorted(p.name for p in FIG.glob("*.png")))
