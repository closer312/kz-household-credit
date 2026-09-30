import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = Path(os.environ.get(
    "DATATHON_DATA",
    ROOT.parent.parent / "synthetic_microdata_2021-2024_20260921",
))
OUT = ROOT / "data_processed"
RES = ROOT / "results"
FIG = ROOT / "figures"
for p in (OUT, RES, FIG):
    p.mkdir(exist_ok=True)

YEARS = [2021, 2022, 2023, 2024]
QUARTERS = ["1kv", "2kv", "3kv", "4kv"]

KODNU12 = {
    "59": "credit_received",
    "2.1.1.4.1": "credit_repaid",
    "60": "savings_used",
    "61": "informal_borrowed",
    "2.1.1.4.2": "informal_repaid",
    "62": "debt_returned_to_hh",
}

PURPOSE = {
    "1": "Строительство дома", "2": "Покупка жилья/участка", "3": "Продукты питания",
    "4": "Открытие бизнеса", "5": "Образование", "6": "Товары длит. пользования",
    "7": "Здоровье, лекарства", "8": "Долги по коммуналке", "9": "Другое",
}
PURPOSE_GROUP = {
    "1": "Жильё", "2": "Жильё", "3": "Базовые нужды", "7": "Базовые нужды", "8": "Базовые нужды",
    "4": "Инвестиции (бизнес/образование)", "5": "Инвестиции (бизнес/образование)",
    "6": "Товары длит. пользования", "9": "Другое",
}

SOURCE = {
    "1": "МФО", "2": "Коммерческий банк", "3": "Фонд развития МСБ", "4": "НПО",
    "5": "Междунар. организации", "6": "Финцентр МОН", "7": "Частное лицо",
    "8": "Ломбард", "9": "Другое",
}

INCOME = {
    1: "wage", 2: "self_employed", 3: "of_which_agri_sales", 4: "pension", 5: "stipend",
    6: "targeted_social_aid", 7: "housing_aid", 8: "child_benefits", 9: "state_social_benefit",
    10: "special_state_benefit", 11: "other_state_transfers", 12: "social_transfers_in_kind",
    13: "material_aid_cash", 14: "material_aid_in_kind", 15: "other_transfers", 16: "alimony",
    17: "sale_real_estate", 18: "sale_personal_property", 19: "property_income",
    20: "rent_housing", 21: "rent_land", 22: "other_receipts", 23: "subsidies",
}
SOCIAL = [5, 6, 7, 8, 9, 10, 11, 12]

REGION = {
    "10": "Абайская", "11": "Акмолинская", "15": "Актюбинская", "19": "Алматинская",
    "23": "Атырауская", "27": "ЗКО", "31": "Жамбылская", "33": "Жетісу",
    "35": "Карагандинская", "39": "Костанайская", "43": "Кызылординская",
    "47": "Мангистауская", "55": "Павлодарская", "59": "СКО", "61": "Туркестанская",
    "62": "Улытау", "63": "ВКО", "71": "г. Астана", "75": "г. Алматы", "79": "г. Шымкент",
}

def read(path, **kw):

    import pandas as pd
    return pd.read_csv(DATA_DIR / path, dtype=str, **kw)
