import requests
import re
import json, time
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

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


UMBCBASE_M = "https://www.tfrrs.org/teams/tf/MD_college_m_UMBC.html"
BINGBASE_M = "https://www.tfrrs.org/teams/tf/NY_college_m_Binghamton.html"
BRYANTBASE_M = "https://www.tfrrs.org/teams/tf/RI_college_m_Bryant.html"
UNHBASE_M = "https://www.tfrrs.org/teams/tf/NH_college_m_New_Hampshire.html"
ALBANYBASE_M = "https://www.tfrrs.org/teams/tf/NY_college_m_Albany.html"
MAINEBASE_M = "https://www.tfrrs.org/teams/tf/ME_college_m_Maine.html"
VERMONTBASE_M = "https://www.tfrrs.org/teams/tf/VT_college_m_Vermont.html"
NJITBASE_M = "https://www.tfrrs.org/teams/tf/NJ_college_m_New_Jersey_Institute_Technolog.html"
UMLBASE_M = "https://www.tfrrs.org/teams/tf/MA_college_m_UMass_Lowell.html"

UMBCBASE_F = "https://www.tfrrs.org/teams/tf/MD_college_f_UMBC.html"
BINGBASE_F = "https://www.tfrrs.org/teams/tf/NY_college_f_Binghamton.html"
BRYANTBASE_F = "https://www.tfrrs.org/teams/tf/RI_college_f_Bryant.html"
UNHBASE_F = "https://www.tfrrs.org/teams/tf/NH_college_f_New_Hampshire.html"
ALBANYBASE_F = "https://www.tfrrs.org/teams/tf/NY_college_f_Albany.html"
MAINEBASE_F = "https://www.tfrrs.org/teams/tf/ME_college_f_Maine.html"
VERMONTBASE_F = "https://www.tfrrs.org/teams/tf/VT_college_f_Vermont.html"
NJITBASE_F = "https://www.tfrrs.org/teams/tf/NJ_college_f_New_Jersey_Institute_Technolog.html"
UMLBASE_F = "https://www.tfrrs.org/teams/tf/MA_college_f_UMass_Lowell.html"





MALE_TEAMS = {
    "Binghamton": BINGBASE_M, "Bryant":BRYANTBASE_M, "Maine":MAINEBASE_M,
    "NJIT":NJITBASE_M, "UNH":UNHBASE_M, "Albany":ALBANYBASE_M,
    "UMBC":UMBCBASE_M, "UML":UMLBASE_M, "Vermont":VERMONTBASE_M
}

FEMALE_TEAMS = {
    "Binghamton": BINGBASE_F, "Bryant":BRYANTBASE_F, "Maine":MAINEBASE_F,
    "NJIT":NJITBASE_F, "UNH":UNHBASE_F, "Albany":ALBANYBASE_F,
    "UMBC":UMBCBASE_F, "UML":UMLBASE_F, "Vermont":VERMONTBASE_F
}

BASE = "https://www.tfrrs.org"

# repo root = one level up from the api/ folder
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)



HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"}


def fetch_html(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def get_outdoor_season_hnd(team_url, target_year):
    """
    Given a team page (e.g., https://www.tfrrs.org/teams/tf/MD_college_f_UMBC.html)
    and a target year (e.g., 2025), return the value that configures the link for that outdoor season
    """
    html = fetch_html(team_url)
    soup = BeautifulSoup(html, "html.parser")
    select = soup.find("select", {"name": "config_hnd"})
    if not select:
        print(f"No season dropdown found on {team_url}")
        return None

    for option in select.find_all("option"):
        text = option.text.strip()
        val = option.get("value", "").strip()
        if str(target_year) in text and "Outdoor" in text:
            return val 
    print(f"No matching Outdoor season found for {target_year} on {team_url}")
    return None

def get_top_link(season_hnd_url):
    """
    Return the link to top performances given the team's page for that season.
    """
    html = fetch_html(season_hnd_url)
    soup = BeautifulSoup(html, "html.parser")
    top_link = None
    for a in soup.find_all("a"):
        if a.text.strip().upper() == "ALL PERFORMANCES":
            top_link = a.get("href")
    
    return top_link


def get_col(selector, row):
    col = row.find("div", class_=selector)
    if not col:
        return {"text": None, "link": None}
    link_tag = col.find("a")
    text = link_tag.text.strip() if link_tag else col.text.strip()
    link = link_tag["href"] if link_tag else None
    return {"text": text, "link": link}

def get_america_east_performances_urls(urls, event_group, gender, team_name):
    """Same as get_america_east_performances but uses fully custom URLs"""
    if gender == "M":
        event_lookup = MALE_EVENTS
        events = MALE_ALL if event_group == "A" else (
            MALE_SPRINT if event_group == "S" else MALE_DISTANCE if event_group == "D" else MALE_HURDLE)
    else:
        event_lookup = FEMALE_EVENTS
        events = FEMALE_ALL if event_group == "A" else (
            FEMALE_SPRINT if event_group == "S" else FEMALE_DISTANCE if event_group == "D" else FEMALE_HURDLE)

    data_list = []
    for url in urls:
        html = fetch_html(url)
        data = {}
        soup = BeautifulSoup(html, "html.parser")

        for event in events:
            event_key = event_lookup[event]
            event_list = []
            event_div = soup.find("div", class_=event_key)
            place = 1
            if event_div:
                for row in event_div.find_all("div", class_="performance-list-row"):
                    entry = {}
                    entry["place"] = place
                    entry["athlete"] = get_col("col-athlete", row)
                    entry["team"] = {"text": team_name}
                    narrow_cols = row.find_all("div", class_="col-narrow")

                    year = narrow_cols[0].text.strip() if len(narrow_cols) > 0 else None
                    time_val = narrow_cols[1].text.strip() if len(narrow_cols) > 1 else None  
                    meet_date = narrow_cols[2].text.strip() if len(narrow_cols) > 2 else None
                    wind = narrow_cols[3].text.strip() if len(narrow_cols) > 3 else None
                    entry.update({"year": year, "time": time_val, "meet_date": meet_date, "wind": wind})
                    event_list.append(entry)
                    place += 1

                data[event] = event_list
        data_list.append(data)

    return data_list




def parse_meet_date(meet_date):
    """Try to parse a date string like 'Apr 27, 2025' or 'May 3, 2025'"""
    try:
        return datetime.strptime(meet_date, "%b %d, %Y")
    except:
        # handle alternative formats (e.g., 'Apr. 27, 2025')
        try:
            return datetime.strptime(meet_date.replace(".", ""), "%b %d, %Y")
        except:
            return None


def convert_time_to_seconds(time_str):
    """
    Converts time strings like '1:52.34' or '4:01.05' or '55.32' into seconds.
    Returns None if time is missing or malformed.
    """
    if not time_str:
        return None
    try:
        if ":" in time_str:
            parts = time_str.split(":")
            if len(parts) == 2:
                minutes, seconds = parts
                return float(minutes) * 60 + float(seconds)
            elif len(parts) == 3:  # e.g., 1:02:15.32
                hours, minutes, seconds = parts
                return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        else:
            return float(time_str)
    except:
        return None


def get_america_east_conference_performances(event_group, gender, target_year):
    """Scrape all schools for a given event group, gender, and outdoor year, combine, filter, and rank by time."""
    all_data = {}
    if event_group == 'S':
        for event in MALE_SPRINT:
            all_data[event] = []
    elif event_group == 'D':
         for event in MALE_DISTANCE:
            all_data[event] = []
    elif event_group == 'A' and gender=='M':
         for event in MALE_ALL:
            all_data[event] = []

    teams = MALE_TEAMS if gender == "M" else FEMALE_TEAMS
    print(f"\nFetching {gender} {event_group} performances for {target_year} Outdoor season...")

    for team_name, team_base_url in teams.items():
        
        print(f"\n🔍 Getting {team_name} ({gender}) {target_year} Outdoor season_hnd...")

        # Construct team page to find dropdown
        season_hnd = get_outdoor_season_hnd(team_base_url, target_year)
        if not season_hnd:
            continue
        season_hnd_url = team_base_url + "?config_hnd=" + season_hnd
        final_link = get_top_link(season_hnd_url)
        print(final_link)

        

        # ✅ Pass the dynamic URL directly (not team_name)
        team_data = get_america_east_performances_urls([final_link], event_group, gender, team_name)
        team_data = team_data[0]

        
        for event, performances in team_data.items():
            for entry in performances:
                date_obj = parse_meet_date(entry.get("meet_date", ""))
                if date_obj and date_obj < datetime(target_year, 5, 5):
                    sec_time = convert_time_to_seconds(entry["time"])
                    if sec_time is not None:
                        all_data[event].append({
                            "gender": gender,
                            "team": team_name,
                            "event": event,
                            "athlete": entry["athlete"]["text"],
                            "time": entry["time"],
                            "seconds": sec_time,
                            "year": entry["year"],
                            "meet_date": entry["meet_date"],
                            "wind": entry["wind"],
                        })

    for event in all_data.keys():
        all_data[event].sort(key=lambda x: x["seconds"])
        for i, item in enumerate(all_data[event], start=1):
            item["conference_rank"] = i
    

            

            

    

    output_file = DATA_DIR / f"aggregate_conference_{gender.lower()}_{event_group.lower()}_{target_year}_performance_list.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print(f"\n✅ Saved {len(all_data)} total performances to {output_file}")
    print("✅ Performances ranked by time across all schools.")
    return all_data



if __name__ == "__main__":
    print("Welcome to the America East Conference Performance Scraper!")
    print("Choose your event type:")
    print("  A = All events")
    print("  S = Sprints (100m–400m)")
    print("  D = Distance (800m–10000m)")
    print("  H = Hurdles (100/110m, 400m)")

    event_group = input("Enter event type (A/S/D/H): ").strip().upper()
    gender = input("Enter gender (M/F): ").strip().upper()
    target_year = int(input("Enter outdoor season year (e.g. 2025): ").strip())

    if event_group not in ["A", "S", "D", "H"] or gender not in ["M", "F"]:
        print("Invalid input. Please restart and enter correct options.")
    else:
        get_america_east_conference_performances(event_group, gender, target_year)
