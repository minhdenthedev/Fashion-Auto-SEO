import json
import os

import pandas as pd
import numpy as np
from underthesea import word_tokenize


RAW_DATA_PATH = "/home/m1nhd3n/PycharmProjects/FashionAutoSEO/modeling/data/raw/2025-03-03/2025-03-03.json"
VIETNAMESE_DICTIONARY_PATH = "/home/m1nhd3n/PycharmProjects/FashionAutoSEO/modeling/data/vietnamese_dictionary.txt"
PREPROCESSED_FOLDER = "/home/m1nhd3n/PycharmProjects/FashionAutoSEO/modeling/data/preprocessed"

with open(VIETNAMESE_DICTIONARY_PATH, "r") as f:
    words = []
    lines = f.read()
    for line in lines.split("\n"):
        js = json.loads(line)
        words.append(js["text"])

words = pd.Series(words)
words = words[words.str.islower()]
words = words.reset_index()

df = pd.read_json(RAW_DATA_PATH)

df["is_combo_or_set"] = df["caption"].str.contains(r"combo|set", case=False, na=False).astype(int)

print(df["is_combo_or_set"].sum())

df["tokenized_caption"] = [word_tokenize(x) for x in df["caption"]]
df.to_csv(os.path.join(PREPROCESSED_FOLDER, "tokenized.csv"), sep='|')
print(df.head())
