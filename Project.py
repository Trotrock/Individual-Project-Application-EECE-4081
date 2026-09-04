# This file will serve as the development enviroment for my individual project for software engineering

# Create a Django view that displays today's date
from django.http import HttpResponse
from datetime import date

def todays_date(request):
    today = date.today()
    return HttpResponse(f"Today's date is {today}")