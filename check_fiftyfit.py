"""
Checkt FiftyFit (Leeghwaterbad, Spurd) op vrije plekken en stuurt een
push via ntfy.sh zodra een volle les plekken vrij krijgt.

Instellen via environment variables:
  NTFY_TOPIC   verplicht, je eigen geheime ntfy-topicnaam
  WEEKDAYS     optioneel, bv "0,2"  (0=ma ... 6=zo). Leeg = alle dagen
  TIMES        optioneel, bv "11:00,13:00". Leeg = alle tijden
"""
import json
import os
import urllib.request
from datetime import date
from pathlib import Path

API_URL = "https://spurd.booqi.me/api/products/293152/plots?order%5Bquantity%5D=1&language=nl"
BOOK_URL = "https://spurd.booqi.me/product/293152/fiftyfit"
STATE_FILE = Path("state.json")
DAGEN = ["ma", "di", "wo", "do", "vr", "za", "zo"]


def get_slots():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0 (plekken-checker)"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    return data["response"]


def matches_filter(slot):
    weekdays = os.environ.get("WEEKDAYS", "").strip()
    times = os.environ.get("TIMES", "").strip()
    d = date.fromisoformat(slot["date"])
    if weekdays and str(d.weekday()) not in weekdays.split(","):
        return False
    if times and slot["time"]["start"] not in times.split(","):
        return False
    return True


def notify(message):
    topic = os.environ["NTFY_TOPIC"]
    req = urllib.request.Request(
        f"https://ntfy.sh/{topic}",
        data=message.encode("utf-8"),
        headers={"Title": "FiftyFit: plek vrij!", "Click": BOOK_URL, "Tags": "swimmer"},
    )
    urllib.request.urlopen(req, timeout=20)


def main():
    previous = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    slots = get_slots()
    current = {}
    newly_free = []

    for slot in slots:
        sid = str(slot["id"])
        free = slot["availability"]["amount"] if slot["selectable"] else 0
        current[sid] = free

        if not matches_filter(slot):
            continue
        was_free = previous.get(sid, 0)
        # Melding als een les van 0 naar >0 gaat (of nieuw verschijnt met plek)
        if free > 0 and was_free == 0:
            d = date.fromisoformat(slot["date"])
            newly_free.append(
                f"{DAGEN[d.weekday()]} {d.strftime('%d-%m')} {slot['time']['start']}: {free} vrij"
            )

    # Eerste run: alleen state opslaan, geen spam met alles wat nu al vrij is
    if previous and newly_free:
        notify("\n".join(newly_free))
        print("Melding verstuurd:\n" + "\n".join(newly_free))
    else:
        print(f"Geen nieuwe plekken ({len(slots)} lessen gecheckt).")

    STATE_FILE.write_text(json.dumps(current, indent=0))


if __name__ == "__main__":
    main()
