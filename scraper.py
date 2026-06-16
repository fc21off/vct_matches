import requests
from bs4 import BeautifulSoup
import json
import time


def fetch_vct_matches():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    all_matches = []

    # Durchsuche die ersten 5 Seiten
    for page_number in range(1, 6):
        url = f"https://www.vlr.gg/matches?page={page_number}"
        print(f"Scrape Seite {page_number}...")

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for match in soup.select("a.match-item"):
                # Event-Name extrahieren
                event_element = match.select_one(".match-item-event")
                if not event_element:
                    continue

                event_full = event_element.get_text(" ", strip=True)

                # FILTER: Nur VCT, Masters oder Champions
                if any(keyword in event_full for keyword in ["VCT", "Masters", "Champions", "Challengers"]):

                    teams = match.select(".match-item-vs-team-name")
                    scores = match.select(".match-item-vs-team-score")

                    status_element = match.select_one(".ml-status")
                    status_text = status_element.get_text(strip=True) if status_element else "Unknown"

                    eta_element = match.select_one(".ml-eta")
                    eta = eta_element.get_text(strip=True) if eta_element else ""

                    logo_element = match.select_one(".match-item-icon img")
                    logo_url = "https:" + logo_element['src'] if logo_element and logo_element.has_attr('src') else None

                    match_data = {
                        "team1": teams[0].get_text(strip=True) if len(teams) > 0 else "TBD",
                        "team2": teams[1].get_text(strip=True) if len(teams) > 1 else "TBD",
                        "score1": scores[0].get_text(strip=True) if len(scores) > 0 else "–",
                        "score2": scores[1].get_text(strip=True) if len(scores) > 1 else "–",
                        "status": f"{status_text} - {eta}".strip(" - "),
                        "event": event_full,
                        "isLive": (status_text == "LIVE"),
                        "event_logo": logo_url,
                        "team1LogoUrl": None,
                        "team2LogoUrl": None
                    }

                    # Duplikate vermeiden
                    if match_data not in all_matches:
                        all_matches.append(match_data)

            # Kurze Pause zwischen den Requests
            time.sleep(1)

        except Exception as e:
            print(f"Fehler beim Scrappen von Seite {page_number}: {e}")
            continue

    # Nach Live-Status sortieren (Live zuerst)
    all_matches.sort(key=lambda x: x['isLive'], reverse=True)

    # Gib die top 4 zurück
    return all_matches[:8]


if __name__ == "__main__":
    data = fetch_vct_matches()
    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Fertig! matches.json wurde aktualisiert.")
    print(json.dumps(data, indent=2, ensure_ascii=False))