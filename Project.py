# This file will serve as the development enviroment for my individual project for software engineering

from datetime import date

from django.http import HttpResponse


def today(request):
	"""Display today's date."""
	return HttpResponse(date.today().isoformat())


