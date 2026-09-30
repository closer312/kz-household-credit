\

import base64
import pandas as pd
from config import RES, FIG, ROOT

TEAM = "DataX"
AUTHORS = "Тариелова Алия Тариеловна, Ырысбеков Жаныбек Ырысбекович, Рахимбекова Салия Элнуровна, Джанболотов Кубат"

t0 = pd.read_csv(RES / "t0_datasets.csv").set_index("form")
t1 = pd.read_csv(RES / "t5_trend_by_year.csv").set_index("year")
t2 = pd.read_csv(RES / "t6_purpose_by_year.csv").set_index("year")
t3 = pd.read_csv(RES / "t7_source_by_year.csv").set_index("year")
t4 = pd.read_csv(RES / "t8_by_income_quintile_2024.csv").set_index("quint")
t5 = pd.read_csv(RES / "t3_by_region_2024.csv").set_index("region")
t6 = pd.read_csv(RES / "t4_urban_rural_2024.csv").set_index("urban")
t9 = pd.read_csv(RES / "t1_quality_checks.csv").set_index("year")
t10 = pd.read_csv(RES / "t2_income_structure.csv").set_index("year")

P = lambda x, d=0: f"{x*100:.{d}f}%".replace(".", ",")
N = lambda x: f"{x:,.0f}".replace(",", " ")
img = lambda n: "data:image/png;base64," + base64.b64encode((FIG / n).read_bytes()).decode()
rmin, rmax = t5["share_repaying"].idxmin(), t5["share_repaying"].idxmax()
who = (f"Команда «{TEAM}» · " if TEAM else "") + AUTHORS

FORMS = {"d004": "Д-004 бюджеты домохозяйств (квартальная)", "d008": "Д-008 состав домохозяйства",
         "d006": "Д-006 жилищные условия", "d002": "Д-002 самооценка / респондент",
         "1t_god": "1-Т годовая (труд, предприятия)", "1t_kv": "1-Т квартальная", "2t": "2-Т (предприятия)",
         "t001": "Т-001 обследование рабочей силы"}
rows = "".join(
    f"<tr class='{'use' if f in ('d004','d008') else ''}'><td>{FORMS[f]}</td><td>{int(r.tables)}</td>"
    f"<td>{N(r.rows_synthetic)}</td><td>{r.diff_pct:+.2f}%</td></tr>"
    for f, r in t0.sort_values("rows_synthetic", ascending=False).iterrows())

slides = []
S = lambda h: slides.append(f'<section class="slide">{h}</section>')

S(f"""<p class="kicker">STAT.DATATHON 2026 · Результат 1: дескриптивная аналитика датасетов · 30.09.2026</p>
<h1>Долговая нагрузка домохозяйств Казахстана, 2021–2024</h1>
<p class="muted">{who}</p>
<div class="cols">
<div><h3>Архив: 8 форм, {int(t0.tables.sum())} таблиц, {N(t0.rows_synthetic.sum())} строк</h3>
<table><tr><th>форма</th><th>таблиц</th><th>строк</th><th>vs реальные</th></tr>{rows}</table>
<p class="muted">Выделено — что используем. Отклонение числа строк от реальных данных — доли процента.</p></div>
<div><h3>Наша панель: домохозяйство × квартал</h3>
<ul>
<li>Д-004: <code>kv_vopr0</code> (регион, город/село), <code>kv_vopr1–7</code> (расходы), <code>kv_vopr11</code> (23 вида дохода), <code>kv_vopr12</code> (заёмные средства); Д-008 — состав семьи. Ключ <code>NOMER</code>.</li>
<li><b>{N(t9.hh_quarter_rows.sum())}</b> наблюдений = 12&nbsp;000 семей × 16 кварталов.</li>
<li>Проверки: {P(t9.matched_to_roster.min())} семей нашлись в Д-008; доходы есть у ≈{P(t9.with_income_rows.mean())}, расходы у ≈{P(t9.with_spending_rows.mean())}; раздел «Заёмные средства» заполнен у {P(t9.with_any_borrowing_row.min())}–{P(t9.with_any_borrowing_row.max())}.</li>
<li>В 2021 году в Д-008 нет года рождения → доля детей только с 2022.</li>
</ul>
<h3>Ловушки, которые учли</h3>
<ul>
<li>Все поля читаем как текст, в числа — только суммы.</li>
<li><code>KOD</code> в <code>kv_vopr12</code> — ответы на 2 разных вопроса: делим по <code>NOMVNEW</code> (21 — цель, 22 — источник).</li>
<li><code>GR3</code> в доходах — «из него» от <code>GR2</code>, в сумму не входит.</li>
<li>Годы между собой не связаны (ID не совпадают) — сравниваем только срезы.</li>
</ul></div></div>""")

S(f"""<h2>Портрет домохозяйств: доходы и география кредита</h2>
<div class="cols">
<div><img src="{img('f1_income_structure.png')}">
<ul>
<li>Зарплата — {P(t10.loc[2024,'wage'])} денежного дохода в 2024 (было {P(t10.loc[2021,'wage'])}), доля пенсий снизилась с {P(t10.loc[2021,'pension'])} до {P(t10.loc[2024,'pension'])}.</li>
<li>Медианный доход на человека за квартал: {N(t10.loc[2021,'median_pc_income_q'])} → {N(t10.loc[2024,'median_pc_income_q'])} тг (номинально +{P(t10.loc[2024,'median_pc_income_q']/t10.loc[2021,'median_pc_income_q']-1)}).</li>
<li>Город и село почти не различаются: кредит выплачивают {P(t6.loc[1,'repaying'])} городских и {P(t6.loc[0,'repaying'])} сельских семей.</li>
</ul></div>
<div><img class="tall" src="{img('f2_regions.png')}">
<p class="take">Разброс по регионам — от {P(t5.loc[rmin,'share_repaying'])} ({rmin}) до {P(t5.loc[rmax,'share_repaying'])} ({rmax}); с медианным доходом региона он почти не связан (r = {t5['share_repaying'].corr(t5['median_pc_income']):.2f}).</p>
</div></div>""")

S(f"""<h2>Заёмные средства: больше кредитов, тяжелее всего бедным</h2>
<div class="cols c73"><img src="{img('f3_borrowing.png')}">
<div>
<ul>
<li>Новый кредит за квартал: {P(t1.loc[2021,'share_new_credit'],1)} → {P(t1.loc[2024,'share_new_credit'],1)} семей; выплачивают кредит: {P(t1.loc[2021,'share_repaying'],1)} → {P(t1.loc[2024,'share_repaying'],1)}.</li>
<li>Медиана нового кредита стабильна, ≈{t1.loc[2024,'median_new_credit']/1000:.0f} тыс. тг.</li>
<li>Цель — чаще всего товары длительного пользования ({P(t2.loc[2024,'Товары длит. пользования'])}).</li>
<li>Банки — {P(t3.loc[2024,'Коммерческий банк'])}; доля МФО {P(t3.loc[2021,'МФО'])} → {P(t3.loc[2024,'МФО'])}, частных лиц {P(t3.loc[2021,'Частное лицо'])} → {P(t3.loc[2024,'Частное лицо'])}.</li>
<li>Выплаты / доход у платящих: {P(t4.loc[1,'median_dsr_repayers'])} у беднейших 20% против {P(t4.loc[5,'median_dsr_repayers'])} у богатейших; у {P(t1.loc[2024,'share_dsr_gt30_repayers'])} платящих — выше 30%.</li>
</ul>
<h3>Куда двигаемся (Результат 2, 7.10)</h3>
<p>Гипотезы: (1) закредитованность бедных семей растёт за счёт МФО; (2) региональные различия не объясняются доходом; (3) большие и городские семьи берут кредиты чаще.</p>
<p class="muted">Данные синтетические: доли близки к реальным, связи между переменными ослаблены.</p>
</div></div>""")

css = """
:root{--bg:#fcfcfb;--ink:#0b0b0b;--muted:#52514e;--accent:#2a78d6;--warm:#eb6834;--line:#e6e5e0}
*{box-sizing:border-box}html{scroll-snap-type:y mandatory}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.slide{width:100%;max-width:1400px;min-height:100vh;margin:0 auto;padding:3.5vh 4vw;scroll-snap-align:start;display:flex;flex-direction:column;justify-content:center;border-bottom:1px solid var(--line)}
h1{font-size:2rem;line-height:1.15;margin:.2em 0}h2{font-size:1.6rem;margin:0 0 .5em}h3{font-size:1rem;color:var(--muted);margin:.6em 0 .3em}
.kicker{color:var(--accent);font-weight:600;margin:0;font-size:.9rem}.muted{color:var(--muted);font-size:.82rem}
img{max-width:100%;display:block;margin:0 auto}img.tall{max-height:62vh}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:2.5vw;align-items:start}.cols.c73{grid-template-columns:1.75fr 1fr;align-items:center}
.take{border-left:4px solid var(--warm);padding:.4em .9em;background:#fdf3ee}
table{border-collapse:collapse;width:100%;font-size:.84rem}td,th{padding:.28em .45em;border-bottom:1px solid var(--line);text-align:left}
td:nth-child(n+2),th:nth-child(n+2){text-align:right}tr.use td{background:#eaf2fc;font-weight:600}
ul{padding-left:1.1em;margin:.3em 0}li{margin:.25em 0}
code{background:#efefe9;padding:.05em .3em;border-radius:3px;font-size:.86em}
@media(max-width:900px){.cols,.cols.c73{grid-template-columns:1fr}.slide{padding:4vh 16px}}
@media print{@page{size:1400px 800px;margin:0}html{scroll-snap-type:none}.slide{height:800px;min-height:0;page-break-after:always;border:0;overflow:hidden}}
"""
html = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Результат 1 — долговая нагрузка домохозяйств</title><style>{css}</style></head><body>{''.join(slides)}
<script>document.addEventListener('keydown',e=>{{const s=[...document.querySelectorAll('.slide')];const i=s.findIndex(x=>x.getBoundingClientRect().top>-10);
if(['ArrowRight','PageDown',' '].includes(e.key)){{e.preventDefault();(s[i+1]||s[i]).scrollIntoView({{behavior:'smooth'}})}}
if(['ArrowLeft','PageUp'].includes(e.key)){{e.preventDefault();s[Math.max(i-1,0)].scrollIntoView({{behavior:'smooth'}})}}}});</script></body></html>"""
out = ROOT / "presentation" / "index.html"
out.write_text(html, encoding="utf-8")
print(out.name, len(html) // 1024, "KB,", len(slides), "slides")
