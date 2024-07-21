import requests as rq
import re
import json
import pandas as pd
def get_data(url: str) -> str:
    req = rq.get(url)
    return req.text

def extract_json_from_html(html_content: str) -> dict:
    pattern = r'<script type="application/ld\+json">(.*?)</script>'
    matches = re.findall(pattern, html_content, re.DOTALL)
    
    for match_ in matches:
        try:
            data = json.loads(match_)
            if data.get("@type") == "ItemList" and data.get("name") == "Villa - Palace for Rent in  Oman ":
                return data
        except json.JSONDecodeError:
            continue
    
    return {}

def get_number_of_villas(data: dict) -> int:
    return len(data.get("itemListElement", []))

def save_data(data: dict):
    items = data.get("itemListElement", [])
    df = pd.read_csv("villas.csv")
    for item in items:
        name = item.get("name")
        price = item.get("offers", {}).get("price")
        currency = item.get("offers", {}).get("priceCurrency")
        description = item.get("description")
        df = pd.concat([df, pd.DataFrame({
            "name": [name],
            "price": [price],
            "currency": [currency],
            "description": [description]
        })], ignore_index=True)
    df.to_csv("villas.csv", index=False)

def main():
    print("Scraping villas...")
    # clean csv file
    pd.DataFrame({
        "name": [],
        "price": [],
        "currency": [],
        "description": []
    }).to_csv("villas.csv", index=False)
    c = 0
    url = "https://om.opensooq.com/en/real-estate-for-rent/villa-palace-for-rent"
    while True:
        html_content = get_data(url)
        data = extract_json_from_html(html_content)
        save_data(data)
        if get_number_of_villas(data) < 30:
            break
        c += 1
        url = f"{url}?page={c}"
        print(f"Scraping page {c}")
if __name__ == "__main__":
    main()
