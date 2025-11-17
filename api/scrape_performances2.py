import requests
import re
import json, time
from pathlib import Path
from bs4 import BeautifulSoup

import os
import time
import random

#link to the america east conference page
AEURL = "https://www.tfrrs.org/leagues/61.html"
AE2025OUTDOOR = "https://www.tfrrs.org/lists/5104/America_East_Outdoor_Performance_List"
BASE = "https://www.tfrrs.org"

# repo root = one level up from the api/ folder
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PAGE_CACHE = "./pages/"
DATA_DIR = "./data/"
SLEEP_TIME = 5
SLEEP_TIME_RAND = 5
SPRING_2025_HND = 681

MEET_KEY = "MEET_"
TEAM_KEY = "TEAM_"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"}

def slugify(s):
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)        # remove non-word chars
    s = re.sub(r"[\s_]+", "-", s)         # spaces/underscores -> hyphens
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s

def fetch_html(url):
    r = requests.get(url, headers = HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def fetch_html_cached(url, title, allow_cache = True):
    if os.path.exists(PAGE_CACHE + title + ".html") and allow_cache:
        print("Loaded Page")
        with open(PAGE_CACHE + title + ".html", "r", encoding = "utf-8") as input_page:
            html = input_page.read()
        was_cached = True
    else:
        html = fetch_html(url)
        print("Fetched Page")
        Path(PAGE_CACHE + title + ".html").write_text(html, encoding = "utf-8")
        was_cached = False
    return html, was_cached


def scan_meet(meet_url):
    meet_url = meet_url.split("?")[0]
    meet_title = meet_url.split("/")[-1]
     
    print("Loading Men's Results")
    html, was_cached = fetch_html_cached(meet_url.replace(meet_title, "m/" + meet_title), MEET_KEY + "m_" + meet_title)
    soup = BeautifulSoup(html, "html.parser")
    if not was_cached: time.sleep(SLEEP_TIME + random.randint(0, SLEEP_TIME_RAND))
    
    mens_tables = parse_page_tables(soup)
    
    with open(DATA_DIR + MEET_KEY + "m_" + meet_title + ".json", "w") as js_out:
        json.dump(mens_tables, js_out, indent = 4)
    
    print("Loading Women's Results")
    html, was_cached = fetch_html_cached(meet_url.replace(meet_title, "f/" + meet_title), MEET_KEY + "f_" + meet_title)
    soup = BeautifulSoup(html, "html.parser")
    if not was_cached: time.sleep(SLEEP_TIME + random.randint(0, SLEEP_TIME_RAND))
    
    womens_tables = parse_page_tables(soup)
    
    with open(DATA_DIR + MEET_KEY + "f_" + meet_title + ".json", "w") as js_out:
        json.dump(womens_tables, js_out, indent = 4)
    
    print("Loading Main Page")
    html, was_cached = fetch_html_cached(meet_url, MEET_KEY + meet_title)
    soup = BeautifulSoup(html, "html.parser")
    if not was_cached: time.sleep(SLEEP_TIME + random.randint(0, SLEEP_TIME_RAND))
    
    team_selector = soup.find("select", attrs = {"name": "team_filter"})
    
    found_team_ids = []
    found_team_names = []
    
    for team in team_selector.findChildren():
        if team.has_attr("value") and not (team["value"] in found_team_ids):
            found_team_names.append(team.text)
            found_team_ids.append(team["value"])
            print(found_team_names[-1] + " : " + str(found_team_ids[-1]))
    
    print(str(len(found_team_ids)) + " Teams Found")
    print("Loading Teams")
    
    for team_index in range(0, len(found_team_ids)):
        print(str(team_index) + "/" + str(len(found_team_ids)))
        
        team_id = found_team_ids[team_index]
        team_name = found_team_names[team_index]
        
        
        meet_team_url = meet_url + "?team_hnd=" + str(team_id)
        meet_team_title = meet_title + "_" + str(team_id) + "_" + team_name
        
        html, was_cached = fetch_html_cached(meet_team_url, MEET_KEY + TEAM_KEY + meet_team_title)
        soup = BeautifulSoup(html, "html.parser")
        if not was_cached: time.sleep(SLEEP_TIME + random.randint(0, SLEEP_TIME_RAND))
        
        team_internal_name_link = soup.find("a", attrs = {"href" : re.compile("https://www.tfrrs.org/teams/tf/*")})
        team_internal_name = team_internal_name_link["href"].split("/")[-1].split(".")[0]
        
        #https://www.tfrrs.org/teams/tf/MD_college_m_UMBC.html
        #https://www.tfrrs.org/all_performances/MD_college_m_UMBC.html?list_hnd=5027&season_hnd=681#event29
        team_performances_link = "https://www.tfrrs.org/all_performances/" + team_internal_name + ".html?list_hnd=5027&season_hnd=" + str(SPRING_2025_HND)
        html, was_cached = fetch_html_cached(team_performances_link, TEAM_KEY + team_internal_name + "_" + str(SPRING_2025_HND))
        soup = BeautifulSoup(html, "html.parser")
        if not was_cached: time.sleep(SLEEP_TIME + random.randint(0, SLEEP_TIME_RAND))
        
        parse_team_performances(soup)
        
        
        
# Note: "List" pages like full team results or region results, e.g., AE2025OUTDOOR, use only divs instead of real tables, and therefor can't use this function. 
def parse_page_tables(soup):
    invisible_entries = []
    tables = {}

    main_content = soup.find("div", class_="panel-body")
    
    # Note: Some results are hidden via inline CSS. I assume the visible ones are the true values, so I have to find all the classes that are hidden...
    styles = main_content.find_all("style")
    
    for style in styles:
        style_results = re.sub(r'\s+', '', style.text)
        style_results_clean = style_results.replace(".", "")
        style_results_split = style_results_clean.split("{display:none!important;}")[:-1]
        
        for entry in style_results_split:
            invisible_entries.append(entry)
    
    # ~ print(invisible_entries)
    print("Potentially Removed Entries: " + str(len(invisible_entries)))
    
    rows = main_content.find_all("div", class_ = "row")
    print("Row Count: " + str(len(rows)))
    
    for row in rows:
        row_tables = row.find_all("div", recursive = False)
        
        for table in row_tables:
            pot_titles = table.find_all("h3")
            if len(pot_titles) > 0:
                table_name = pot_titles[0].text.strip()
            else:
                pot_titles = table.find_all("h5")
                if len(pot_titles) > 0:
                    table_name = pot_titles[0].text.strip()
                else:
                    if "quick-links" in str(table):
                        print("Skipped Quick Links.")
                        continue
                    else:
                        print(table)
                        print("Failed out finding table title")
                        exit()
            
            col_heads = table.find_all("th")
            table_rows = table.find("tbody").find_all("tr")
            
            tables[table_name] = []
            
            heads = []
            
            for col_head in col_heads:
                if col_head.has_attr("class") and col_head["class"][0] in invisible_entries:
                    continue
                
                heads.append(col_head.text.strip())
                
            tables[table_name].append(heads)
            
            for table_row in table_rows:
                row_entires = []
                table_row_entries = table_row.find_all("td")
                
                for table_row_entry in table_row_entries:
                    if table_row_entry.has_attr("class") and table_row_entry["class"][0] in invisible_entries:
                        continue
                    
                    row_entires.append(table_row_entry.text.strip())
                
                if len(row_entires) == 0:
                    print(table_row)
                
                tables[table_name].append(row_entires)
            
    # ~ for k in list(tables.keys()):
        # ~ print(k)
    print("Finished")
    return tables
    

def parse_team_performances(soup):
    return {}

if __name__ == "__main__":
    
    os.makedirs(PAGE_CACHE, exist_ok = True)
    os.makedirs(DATA_DIR, exist_ok = True)
    
    redownload = False
    
    test_page = "https://www.tfrrs.org/results/89890/2025_George_Mason_Dalton_Ebanks_Invitational_"
    scan_meet(test_page)
    
    exit()