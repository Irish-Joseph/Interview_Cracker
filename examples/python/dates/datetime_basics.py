"""
Topic: Date and time handling with the datetime module.

Concepts:
- datetime vs date vs time vs timedelta
- Parsing strings (strptime) and formatting (strftime)
- Timezone-aware datetimes (fromisoformat, astimezone)
- Arithmetic: adding/subtracting timedelta
- Common pitfalls: mixing naive and aware datetimes

"Naive" datetime = no timezone info. "Aware" = UTC offset attached.
Mixing them in comparisons raises TypeError — a good thing, because
comparing 14:00 in Tokyo with 14:00 in London is a silent bug
otherwise.

Time Complexity: O(1) for the operations shown
"""

from datetime import date, datetime, timedelta, timezone

# --- 1. "Now" and components ------------------------------------------------

now = datetime.now()
print(f"now: {now}")
print(f"year={now.year} month={now.month:02d} day={now.day:02d}")
print(f"weekday: {now.strftime('%A')}")          # e.g. Saturday
print(f"ISO: {now.isoformat()}")

# --- 2. Parsing and formatting ---------------------------------------------

# strptime: parse a STRING with a format (p = parse)
flight = datetime.strptime("2026-09-13 08:30:00", "%Y-%m-%d %H:%M:%S")
print(f"parsed: {flight}")

# strftime: format a datetime INTO a string (t = to)
print(f"formatted: {flight.strftime('%d %b %Y, %I:%M %p')}")
# -> 13 Sep 2026, 08:30 AM

# ISO format is the machine-friendly standard:
print(f"iso: {flight.isoformat()}")
# -> 2026-09-13T08:30:00

# fromisoformat parses ISO back — round-trips cleanly:
roundtrip = datetime.fromisoformat(flight.isoformat())
assert roundtrip == flight
print("iso round-trip ok")

# --- 3. timedelta: arithmetic --------------------------------------------------

departure = datetime(2026, 9, 13, 8, 30)
arrival = departure + timedelta(hours=2, minutes=45)
print(f"depart {departure.time()} -> arrive {arrival.time()}")
# -> depart 08:30:00 -> arrive 11:15:00

delta = arrival - departure
print(f"duration: {delta} (days={delta.days}, seconds={delta.seconds})")
# -> duration: 2:45:00 (days=0, seconds=9900)

# Date math: days between two dates
today = date.today()
next_month = date(today.year + (1 if today.month == 12 else 0),
                  (today.month % 12) + 1, 1)
print(f"days until first of next month: {(next_month - today).days}")

# --- 4. Timezones: aware datetimes ------------------------------------------------

# A naive datetime with UTC explicitly attached:
utc_meeting = datetime(2026, 9, 13, 15, 0, tzinfo=timezone.utc)
print(f"UTC: {utc_meeting.isoformat()}")

# Convert to other offsets (still the SAME instant):
tokyo = utc_meeting.astimezone(timezone(timedelta(hours=9)))
nyc = utc_meeting.astimezone(timezone(timedelta(hours=-4)))
print(f"Tokyo: {tokyo.isoformat()}")   # -> 2026-09-14T00:00:00+09:00
print(f"NYC:   {nyc.isoformat()}")     # -> 2026-09-13T11:00:00-04:00

# The classic trap: naive vs aware cannot be compared.
naive = datetime(2026, 9, 13, 15, 0)
try:
    _ = naive < utc_meeting
except TypeError as e:
    print(f"mixing naive/aware raises: {e}")

# --- 5. Practical: is a meeting in the past? --------------------------------------

def is_past(when: datetime, now: datetime) -> bool:
    # Both must be aware (or both naive) — this raises if mixed.
    return when < now

print("meeting already past?", is_past(utc_meeting, datetime.now(timezone.utc)))

# Cheat sheet:
#   %Y year  %m month  %d day  %H hour(24)  %M minute  %S second
#   %A weekday name   %B month name  %I hour(12)  %p AM/PM
#   strptime  = parse   (string -> datetime)
#   strftime  = format  (datetime -> string)
#   isoformat()/fromisoformat() = the standard machine exchange
