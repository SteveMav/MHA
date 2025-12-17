from .models import Schedule
from django.shortcuts import render

def index(request):
    schedules = Schedule.objects.all()
    return render(request, 'main/index.html', {'schedules': schedules})
