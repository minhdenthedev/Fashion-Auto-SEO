import json
import os


DATE_FOLDER = "/home/m1nhd3n/PycharmProjects/FashionAutoSEO/modeling/data/tiki/2025-03-03"
SAVE_PATH = os.path.join(DATE_FOLDER, "2025-03-03.json")
filenames = os.listdir(DATE_FOLDER)
data = []
for n in filenames:
    with open(os.path.join(DATE_FOLDER, n), "r", encoding="utf-8") as f:
        data.extend(json.load(f))

print(len(data))
with open(SAVE_PATH, "w", encoding='utf-8') as f:
    json.dump(data, f)



