from main.models import Schedule
import datetime

schedules = [
    {"day": "Lundi", "start": "15:00", "end": "16:30"},
    {"day": "Mercredi", "start": "15:00", "end": "16:30"},
    {"day": "Vendredi", "start": "15:00", "end": "16:30"},
]

for s in schedules:
    offset = datetime.timedelta(hours=0) # No offset needed if using naive time or aware
    start = datetime.datetime.strptime(s["start"], "%H:%M").time()
    end = datetime.datetime.strptime(s["end"], "%H:%M").time()
    
    Schedule.objects.get_or_create(
        day=s["day"],
        defaults={
            "start_time": start,
            "end_time": end,
            "description": "Entraînement régulier"
        }
    )
print("Schedules added.")
