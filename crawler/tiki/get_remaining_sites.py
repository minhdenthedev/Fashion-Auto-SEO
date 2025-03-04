import json
import os

NAM_SITES_PATH = "/home/m1nhd3n/PycharmProjects/FashionAutoSEO/crawler/tiki/nam_urls.json"
NU_SITES_PATH = "/home/m1nhd3n/PycharmProjects/FashionAutoSEO/crawler/tiki/nu_urls.json"
DATE_FOLDER = "/home/m1nhd3n/PycharmProjects/FashionAutoSEO/modeling/data/tiki/2025-03-01"
SAVE_PATH = os.path.join(DATE_FOLDER, "2025_03_01.json")
filenames = os.listdir(DATE_FOLDER)

with open(NAM_SITES_PATH, "r", encoding="utf-8") as f:
    nam_sites: dict = json.load(f)
with open(NU_SITES_PATH, "r", encoding="utf-8") as f:
    nu_sites: dict = json.load(f)

for i, filename in enumerate(filenames):
    filenames[i] = filename.split(".")[0]

remaining_sites = {}
for i, nam_site in nam_sites.items():
    if i not in filenames:
        remaining_sites[i] = nam_site

for i, nu_site in nu_sites.items():
    if i not in filenames:
        remaining_sites[i] = nu_site

with open("remaining_sites.json", 'w', encoding='utf-8') as f:
    json.dump(remaining_sites, f)


