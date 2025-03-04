import pandas as pd
import numpy as np


RAW_DATA_PATH = "/home/m1nhd3n/PycharmProjects/FashionAutoSEO/modeling/data/tiki/2025-03-03/2025-03-03.json"

df = pd.read_json(RAW_DATA_PATH)
df.to_csv(RAW_DATA_PATH[:-4] + "csv")
print(df.columns)
print(df.caption)
df["is_combo_or_set"] = df["caption"].str.contains(r"combo|set", case=False, na=False).astype(int)

print(df["is_combo_or_set"].sum())
