import json
import os
import re
import time
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

RAW_DATA_PATH = "/home/m1nhd3n/PycharmProjects/FashionAutoSEO/modeling/data/raw"
TODAY = str(datetime.today().date())

with open("nu_urls.json", "r") as f:
    NAME_URL = json.load(f)

print(json.dumps(NAME_URL, indent=2))

if not os.path.exists(os.path.join(RAW_DATA_PATH, TODAY)):
    os.mkdir(os.path.join(RAW_DATA_PATH, TODAY))


def get_html(url, drv, site_name):
    print(f"Getting site {site_name}")
    drv.get(url)
    while True:
        state = drv.execute_script("return document.readyState")
        if state == "complete":
            print(f"Site {site_name} ready")
            break
        time.sleep(1)  # Wait and recheck
    load_more_count = 0
    press_load_more(drv, load_more_count)
    pg_src = drv.page_source
    return pg_src


def press_load_more(drv, load_more_count):
    max_load_more = 10
    while True:
        try:
            # Wait until the button is clickable
            load_more_button = WebDriverWait(drv, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[starts-with(@class, 'styles__Button-sc')]"))
            )
            # Scroll into view
            drv.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_button)
            # Click the button
            load_more_button.click()
            time.sleep(3)
            load_more_count += 1
            print(f"\tClicked: {load_more_count}")
            if load_more_count >= max_load_more:
                break
        except Exception as e:
            break


def pipeline(names_urls: dict):
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--disable-gpu")
    driver = webdriver.Firefox(options=options)
    error_logs = {}
    info_logs = {}
    success_names = []
    fail_count = 0
    while len(success_names) < len(NAME_URL) and fail_count < 10:
        for name, url in names_urls.items():
            if name in success_names:
                continue
            json_save_path = os.path.join(RAW_DATA_PATH, TODAY, name + ".json")
            try:
                html = get_html(url, driver, name)
                print("Getting products")
                products = get_products(html, name)
                with open(json_save_path, "w", encoding="utf-8") as f:
                    json.dump(products, f)
                info_logs[name] = len(products)
                print(f"{name}: success {len(products)} items")
                if len(products) > 0:
                    success_names.append(name)
                else:
                    fail_count += 1
            except Exception as e:
                error_logs[name] = str(e)
                fail_count += 1
                print(f"{name}: fail")
                continue
    driver.close()

    with open("info_logs.json", "w") as f:
        json.dump(info_logs, f)

    with open("error_logs.json", "w") as f:
        json.dump(error_logs, f)


def get_products(html_str, category):
    answers = []
    soup = BeautifulSoup(html_str, "html.parser")
    products = soup.find_all(class_=re.compile(r"styles__ProductItemContainerStyled-sc"))
    for product in products:
        click_id = product.find("a", class_=re.compile(r"style__ProductLink-sc")) \
            .get('data-view-content')
        click_json = json.loads(str(click_id))
        click_id = click_json["click_data"]["id"]
        image_tag = product.find("div", class_=re.compile(r"styles__ThumbnailStyled-sc")) \
            .find("img", class_=re.compile(r"styles__StyledImg-sc")).get("srcset")
        image_url = str(image_tag).split(", ")[0].split(" ")[0]
        caption = product.find("h3", class_=re.compile(r"style__NameStyled-sc")).text
        price = product.find("div", class_=re.compile(r"price-discount__price")).text
        price = re.sub(r"\D", "", price)
        answers.append({
            'click_id': click_id,
            'image_url': image_url,
            'caption': caption,
            'price': price,
            'category': category
        })

    return answers


pipeline(NAME_URL)

# def get_json(html_str):
#     soup = BeautifulSoup(html_str, "html.parser")
#     script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
#     if script_tag:
#         json_data = json.loads(script_tag.string)  # Convert to Python dictionary
#         return json_data
#     else:
#         print("JSON data not found!")


# def save_to_csv(p_data, filename):
#     """Save product data to a CSV file."""
#     # Define CSV headers
#     headers = ["id", "caption", "image_url", "price", "average_rating"]
#
#     # Open CSV file for writing
#     with open(filename, mode="w", newline="", encoding="utf-8") as file:
#         writer = csv.writer(file, delimiter="|")
#
#         # Write the header row
#         writer.writerow(headers)
#
#         # Write product data rows
#         for d in p_data:
#             writer.writerow([d["id"], d["name"], d["thumbnail_url"], d["price"], d["rating_average"]])
#
#     print(f"Data saved successfully to {filename}")

# def dfs_recursive(json_data: dict, path=None, visited=None):
#     if visited is None:
#         visited = set()
#     if path not in visited:
#         print(path)
#         visited.add(path)
#
#         if isinstance(json_data, dict):
#             for key in json_data.keys():
#                 new_json = json_data[key]
#                 new_path = path + "/" + key
#                 dfs_recursive(new_json, new_path, visited)
#         elif isinstance(json_data, list):
#             print(f"ABOVE IS LIST WITH LENGTH {len(json_data)}")
#             return


# dfs_recursive(data, '')

# print("Getting products")
# product_data = data['props']['initialState']['catalog']['data']

# print("Saving raw data")
# save_to_csv(product_data, CSV_SAVE_PATH)
# print(f"Saved {len(product_data)} rows.")
# print(product_data[0].keys())

# def get_images(html_str):
#     soup = BeautifulSoup(html_str, "html.parser")
#     images = soup.find_all(class_=re.compile(r"styles__ThumbnailStyled-sc"))
#     return images
#
#
# def get_captions(html_str):
#     soup = BeautifulSoup(html_str, "html.parser")
#     images = soup.find_all(class_=re.compile(r"style__NameStyled-sc"))
#     return images
