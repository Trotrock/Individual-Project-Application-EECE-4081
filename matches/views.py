from django.http import HttpResponse
from .client import SportsApiClient
from .models import Match

def sync_and_render_match(request):
    # 1. Ingest: Fetch dynamic data fields across the network client
    client = SportsApiClient()
    api_data = client.fetch_latest_match()
    
    if not api_data:
        return HttpResponse("<h3>No upcoming scheduled matches found for this season.</h3>")

    # 2. Process & Store: Save a clean new transaction row record inside the SQLite engine
    # FIX: Changed from update_or_create to create to completely bypass old duplicate rows!
    match_record = Match.objects.create(
        opponent=api_data["opponent"],
        match_date=api_data["date"]
    )
    
    # 3. Render: Output the raw confirmation text payload right to your client window
    return HttpResponse(
        f"<h3>Walking Skeleton Success!</h3>"
        f"<p>Synced from API and saved to Database: "
        f"<strong>FC Barcelona vs {match_record.opponent}</strong> on {match_record.match_date}</p>"
    )
