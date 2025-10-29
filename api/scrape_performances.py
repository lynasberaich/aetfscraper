import requests
import re
import json, time
from pathlib import Path
from bs4 import BeautifulSoup

#link to the america east conference page
AEURL = "https://www.tfrrs.org/leagues/61.html"
AE2025OUTDOOR = "https://www.tfrrs.org/lists/5104/America_East_Outdoor_Performance_List"
BASE = "https://www.tfrrs.org"

# repo root = one level up from the api/ folder
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)



HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"}

def slugify(s):
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)        # remove non-word chars
    s = re.sub(r"[\s_]+", "-", s)         # spaces/underscores -> hyphens
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s

def fetch_html(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def get_col(selector, row):
    col = row.find("div", class_=selector)
    if not col:
        return {"text": None, "link": None}
    link_tag = col.find("a")
    text = link_tag.text.strip() if link_tag else col.text.strip()
    link = link_tag["href"] if link_tag else None
    return {"text": text, "link": link}

def get_america_east_performances():
    html = fetch_html(AE2025OUTDOOR)
    Path("ae2025outdoor.html").write_text(html, encoding="utf-8")
    data = {}
    umbc_data = {}
    soup = BeautifulSoup(html, "html.parser")
    events = ["event6", "event7", "event11"] #100m, 200m, 400m
    for event in events:
        event_list = []
        umbc_event_list = []
        event_div = soup.find("div", class_="row gender_m standard_event_hnd_6")
        for row in event_div.find_all("div", class_="performance-list-row"):
            entry = {}
            entry["place"] = get_col("col-place", row)
            entry["athlete"] = get_col("col-athlete", row)
            entry["team"] = get_col("col-team", row)
            narrow_cols = row.find_all("div", class_="col-narrow")

            # according to order in HTML:
            year = narrow_cols[0].text.strip() if len(narrow_cols) > 0 else None
            time = narrow_cols[1].text.strip() if len(narrow_cols) > 1 else None  
            meet_date = narrow_cols[2].text.strip() if len(narrow_cols) > 2 else None
            wind = narrow_cols[3].text.strip() if len(narrow_cols) > 3 else None
            entry["year"] = year
            entry["time"] = time
            entry["meet_date"] = meet_date
            entry["wind"] = wind

            event_list.append(entry)
            if entry["team"]["text"] == "UMBC":
                umbc_event_list.append(entry)

        data[event] = event_list
        umbc_data[event] = umbc_event_list
    
    return data, umbc_data



if __name__ == "__main__":
    data, umbc_data = get_america_east_performances()
    directory = str(DATA_DIR) + "/performances.json"
    umbc_directory = str(DATA_DIR) + "/umbcperformances.json"
    with open(directory, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    with open(umbc_directory, "w", encoding="utf-8") as f:
        json.dump(umbc_data, f, indent=4, ensure_ascii=False)
    time.sleep(0.5)
    print("Scraping complete.")

