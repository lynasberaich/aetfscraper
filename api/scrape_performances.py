import requests
import re
import json, time
from pathlib import Path
from bs4 import BeautifulSoup

"""
EVENT ID KEY:
- standard_event_hnd_6 - 100m Dash
- standard_event_hnd_7 - 200m Dash
- standard_event_hnd_11 - 400m Dash
- standard_event_hnd_12 - 800m Run
- standard_event_hnd_13 - 1500m Run
- standard_event_hnd_21 - 5000m Run
- standard_event_hnd_22 - 10000m Run
- standard_event_hnd_5 - 110m Hurdles(men only)
- standard_event_hnd_4 - 100m Hurdles(women only)
- standard_event_hnd_9 - 400m Hurdles
- standard_event_hnd_19 - 3000m Steeplechase
"""

MALE_EVENTS = {"100m":"row gender_m standard_event_hnd_6", 
               "200m":"row gender_m standard_event_hnd_7", 
               "400m":"row gender_m standard_event_hnd_11", 
               "800m":"row gender_m standard_event_hnd_12", 
               "1500m":"row gender_m standard_event_hnd_13", 
               "3000msc":"row gender_m standard_event_hnd_19", 
               "5000m":"row gender_m standard_event_hnd_21", 
               "10000m":"row gender_m standard_event_hnd_22", 
               "110mh":"row gender_m standard_event_hnd_5", 
               "400mh":"row gender_m standard_event_hnd_9"}

MALE_SPRINT = ["100m", "200m", "400m"]
MALE_DISTANCE = ["800m", "1500m", "3000msc", "5000m", "10000m"]
MALE_HURDLE = ["110mh", "400mh"]
MALE_ALL = ["100m", "200m", "400m", "800m", "1500m", "3000msc", "5000m", "10000m", "110mh", "400mh"]

FEMALE_EVENTS = {"100m":"row gender_f standard_event_hnd_6", 
                 "200m":"row gender_f standard_event_hnd_7", 
                 "400m":"row gender_f standard_event_hnd_11", 
                 "800m":"row gender_f standard_event_hnd_12", 
                 "1500m":"row gender_f standard_event_hnd_13", 
                 "3000msc":"row gender_f standard_event_hnd_19", 
                 "5000m":"row gender_f standard_event_hnd_21", 
                 "10000m":"row gender_f standard_event_hnd_22", 
                 "100mh":"row gender_f standard_event_hnd_4", 
                 "400mh":"row gender_f standard_event_hnd_9"}

FEMALE_SPRINT = ["100m", "200m", "400m"]
FEMALE_DISTANCE = ["800m", "1500m", "3000msc", "5000m", "10000m"]
FEMALE_HURDLE = ["100mh", "400mh"]
FEMALE_ALL = ["100m", "200m", "400m", "800m", "1500m", "3000msc", "5000m", "10000m", "100mh", "400mh"]




#link to the america east conference page
AEURL = "https://www.tfrrs.org/leagues/61.html"
AE2025OUTDOOR = "https://www.tfrrs.org/lists/5104/America_East_Outdoor_Performance_List"

UMBC25OUTDOOR_M = "https://www.tfrrs.org/top_performances/MD_college_m_UMBC.html?list_hnd=5027&season_hnd=681"
BING25OUTDOOR_M = "https://www.tfrrs.org/top_performances/NY_college_m_Binghamton.html?list_hnd=5027&season_hnd=681"
BRYANT25OUTDOOR_M = "https://www.tfrrs.org/top_performances/RI_college_m_Bryant.html?list_hnd=5027&season_hnd=681"
UNH25OUTDOOR_M = "https://www.tfrrs.org/top_performances/NH_college_m_New_Hampshire.html?list_hnd=5027&season_hnd=681"
ALBANY25OUTDOOR_M = "https://www.tfrrs.org/top_performances/NY_college_m_Albany.html?list_hnd=5027&season_hnd=681"
MAINE25OUTDOOR_M = "https://www.tfrrs.org/top_performances/ME_college_m_Maine.html?list_hnd=5027&season_hnd=681"
VERMONT25OUTDOOR_M = "https://www.tfrrs.org/top_performances/VT_college_m_Vermont.html?list_hnd=5027&season_hnd=681"
NJIT25OUTDOOR_M = "https://www.tfrrs.org/top_performances/NJ_college_m_New_Jersey_Institute_Technolog.html?list_hnd=5027&season_hnd=681"
UML25OUTDOOR_M = "https://www.tfrrs.org/top_performances/MA_college_m_UMass_Lowell.html?list_hnd=5027&season_hnd=681"

UMBC25OUTDOOR_F = "https://www.tfrrs.org/top_performances/MD_college_f_UMBC.html?list_hnd=5027&season_hnd=681"
BING25OUTDOOR_F = "https://www.tfrrs.org/top_performances/NY_college_f_Binghamton.html?list_hnd=5027&season_hnd=681"
BRYANT25OUTDOOR_F = "https://www.tfrrs.org/top_performances/RI_college_f_Bryant.html?list_hnd=5027&season_hnd=681"
UNH25OUTDOOR_F = "https://www.tfrrs.org/top_performances/NH_college_f_New_Hampshire.html?list_hnd=5027&season_hnd=681"
ALBANY25OUTDOOR_F = "https://www.tfrrs.org/top_performances/NY_college_f_Albany.html?list_hnd=5027&season_hnd=681"
MAINE25OUTDOOR_F = "https://www.tfrrs.org/top_performances/ME_college_f_Maine.html?list_hnd=5027&season_hnd=681"
VERMONT25OUTDOOR_F = "https://www.tfrrs.org/top_performances/VT_college_f_Vermont.html?list_hnd=5027&season_hnd=681"
NJIT25OUTDOOR_F = "https://www.tfrrs.org/top_performances/NJ_college_f_New_Jersey_Institute_Technolog.html?list_hnd=5027&season_hnd=681"
UML25OUTDOOR_F = "https://www.tfrrs.org/top_performances/MA_college_f_UMass_Lowell.html?list_hnd=5027&season_hnd=681"

MALE_TEAMS = {
    "Binghamton": BING25OUTDOOR_M, "Bryant":BRYANT25OUTDOOR_M, "Maine":MAINE25OUTDOOR_M,
    "NJIT":NJIT25OUTDOOR_M, "UNH":UNH25OUTDOOR_M, "Albany":ALBANY25OUTDOOR_M,
    "UMBC":UMBC25OUTDOOR_M, "UML":UML25OUTDOOR_M, "Vermont":VERMONT25OUTDOOR_M
}

FEMALE_TEAMS = {
    "Binghamton": BING25OUTDOOR_F, "Bryant":BRYANT25OUTDOOR_F, "Maine":MAINE25OUTDOOR_F,
    "NJIT":NJIT25OUTDOOR_F, "UNH":UNH25OUTDOOR_F, "Albany":ALBANY25OUTDOOR_F,
    "UMBC":UMBC25OUTDOOR_F, "UML":UML25OUTDOOR_F, "Vermont":VERMONT25OUTDOOR_F
}

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

def get_america_east_performances(teams, event_group, gender):
    urls = []
    events = []
    data_locs = []

    if gender == "M":
        event_lookup = MALE_EVENTS
    else:
        event_lookup = FEMALE_EVENTS

    if teams == "ALL":
        urls.append(AE2025OUTDOOR)
        data_locs.append(str(DATA_DIR) + "/" + event_group +  "_" + gender.lower() + "_performances.json")
    else:
        if gender == "M":
            for team in teams:
                urls.append(MALE_TEAMS[team])
                data_locs.append(str(DATA_DIR) + "/" + team + event_group + "_m_performances.json")
        else:
            for team in teams:
                urls.append(FEMALE_TEAMS[team])
                data_locs.append(str(DATA_DIR) + "/" + team + event_group + "_f_performances.json")

    if gender == "M":
        if event_group == "A":
            events = MALE_ALL
        elif event_group == "D":
            events = MALE_DISTANCE
        elif event_group == "S":
            events = MALE_SPRINT
        else:
            events = MALE_HURDLE
    else:
        if event_group == "A":
            events = FEMALE_ALL
        elif event_group == "D":
            events = FEMALE_DISTANCE
        elif event_group == "S":
            events = FEMALE_SPRINT
        else:
            events = FEMALE_HURDLE

    data_list = []
    for url in urls:
        html = fetch_html(url)
        #Path("ae2025outdoor.html").write_text(html, encoding="utf-8")
        data = {}
        soup = BeautifulSoup(html, "html.parser")
        for event in events:
            event_key = event_lookup[event]
            event_list = []
            # umbc_event_list = []
            event_div = soup.find("div", class_=event_key)
            place = 1
            if event_div:
                for row in event_div.find_all("div", class_="performance-list-row"):
                    entry = {}
                    entry["place"] = get_col("col-place", row) if event_group == "A" else place
                    entry["athlete"] = get_col("col-athlete", row)
                    entry["team"] = get_col("col-team", row) if event_group == "A" else None
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
                    place += 1
                    #THIS IS WITHIN THE CONTEXT OF THE CONFERENCES WHICH STILL MIGHT BE IMPORTANT???
                    # if entry["team"]["text"] == "UMBC":
                    #     umbc_event_list.append(entry)

                data[event] = event_list

        data_list.append(data)

    return data_list, data_locs



if __name__ == "__main__":
    print("Hi! Welcome to the AE track and field performance scraper!")
    print("Here is a list of all of the teams in America East:")
    print("\t -Binghamton \t -Bryant \t -Maine")
    print("\t -NJIT \t -UNH \t -Albany")
    print("\t -UMBC \t -UML \t -Vermont")
    teams = input("If you would like to see data for the whole conference enter 'ALL'\n" \
                  "Otherwise, please input the names of the schools you would like data for separated by a single space: ")
    if teams != "ALL":
        teams = teams.split()

    event_group = input("We are able to gather data for either all events(A), just sprints(S), just hurdles(H), or just distance(D) \n" \
          "Indicate your preference by entereing either A, S, H, or D: ")
    
    gender = input("Lastly, are you interested in male performances(M) or female performances(F): ")
    

    data_list, data_locs = get_america_east_performances(teams, event_group, gender)
    for data, loc in zip(data_list, data_locs):
        directory = loc
        print("Writing to ", directory)
        with open(directory, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    
    time.sleep(0.5)
    print("Scraping complete.")

