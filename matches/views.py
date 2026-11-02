from django.shortcuts import render
from django.http import HttpResponse
from django.db import models
from .client import SportsApiClient
from .models import League, Team, LeagueTableEntry, Player, Match, TeamFormation
from datetime import datetime, timezone
import logging
from django.http import JsonResponse

def standings_dashboard(request):
    """
    Renders the public-facing LaLiga Dashboard table alongside 
    FC Barcelona's exclusive next match, tactical formation, and player squad lists.
    """
    # 1. Fetch & Sort the League Standings
    la_liga_table = sorted(
        LeagueTableEntry.objects.all(),
        key=lambda x: (-x.points, -x.goal_difference)
    )
    
    # 2. Fetch FC Barcelona's Next Upcoming Match
    next_match = Match.objects.filter(
        models.Q(home_team__name="FC Barcelona") | models.Q(away_team__name="FC Barcelona")
    ).order_by('match_date').first()

    # 3. Fetch FC Barcelona's Tactical Formation for that match
    barca_formation = None
    if next_match:
        barca_formation = TeamFormation.objects.filter(
            match=next_match, 
            team__name="FC Barcelona"
        ).first()

    # 4. Fetch the Complete FC Barcelona Squad (grouped by position)
    barca_players = Player.objects.filter(team__name="FC Barcelona").order_by('jersey_number')

    # 5. Build presentation state wrapper context
    context = {
        'la_liga_table': la_liga_table,
        'next_match': next_match,
        'barca_formation': barca_formation,
        'barca_players': barca_players,
    }
    
    return render(request, 'matches/dashboard.html', context)

def sync_and_render_match(request):
    """
    Executes the ingestion sync pipeline.
    Parses the full 20-team ecosystem from client.py and saves it cleanly.
    """
    # Initialize the logger instance
    logger = logging.getLogger("matches.views")
    
    # Line 1: Log the start of the operation
    logger.info("Initiating external sports API match sync")
    
    client = SportsApiClient()
    try:
        # Line 2: Log the outgoing request check
        logger.info("Checking database and contacting upstream match stats endpoint")
        
        # --- SIMULATION FOR RUNBOOK ASSIGNMENT ---
        # Add '?fail=true' to the URL to instantly simulate the runbook failure criteria
        if request.GET.get("fail") == "true":
            raise TimeoutError("Connection to ://sportsapi.com timed out after 5000ms")
        # ----------------------------------------
        
        api_data = client.fetch_latest_match()
        
    except Exception as e:
        # Line 3 (Failure): Machine-parseable record capturing structured extra details
        logger.error("Failed to complete match sync operation", extra={
            "extra_data": {
                "api_endpoint": "://sportsapi.com/v1/matches", 
                "error_type": type(e).__name__,
                "status_code": 504
            }
        })
        return HttpResponse(f"<h3>Sync Failed: {str(e)}</h3>", status=504)
    
    if not api_data:
        logger.warning("Data sync completed but payload returned empty results")
        return HttpResponse("<h3>No data retrieved.</h3>")

    # 1. Ingest & Store League
    league_data = api_data["league"]
    league, _ = League.objects.get_or_create(
        name=league_data["name"], 
        defaults={"season": league_data["season"]}
    )

    # 2. Ingest & Store Teams, Standings, and Player Rosters
    for standing in api_data["standings"]:
        team_name = standing["team"]
        team, _ = Team.objects.get_or_create(name=team_name)
        
        LeagueTableEntry.objects.update_or_create(
            league=league,
            team=team,
            defaults={
                "position": standing["position"],
                "points": standing["points"],
                "matches_played": standing["played"],
                "wins": standing["wins"],
                "losses": standing["losses"],
                "draws": standing["draws"],
                "goals_for": standing.get("gf", 0),       
                "goals_against": standing.get("ga", 0),   
            }
        )
        
        for player_data in api_data["rosters"].get(team_name, []):
            Player.objects.get_or_create(
                team=team,
                name=player_data["name"],
                defaults={
                    "jersey_number": player_data["number"],
                    "position": player_data["position"]
                }
            )

    # 3. Ingest & Store Match Details
    m_info = api_data["match_details"]
    home_team = Team.objects.get(name=m_info["home_team"])
    away_team = Team.objects.get(name=m_info["away_team"])
    
    naive_date = datetime.strptime(m_info["date"], "%Y-%m-%d")
    aware_date = naive_date.replace(tzinfo=timezone.utc)
    
    match_record, _ = Match.objects.get_or_create(
        league=league,
        home_team=home_team,
        away_team=away_team,
        defaults={
            "match_date": aware_date,
            "stadium": m_info.get("stadium", "Spotify Camp Nou")
        }
    )

    # 4. Ingest & Store Match Tactical Lineups (Formations)
    for team_name, form_info in api_data["formations"].items():
        current_team = Team.objects.get(name=team_name)
        formation_record, _ = TeamFormation.objects.get_or_create(
            match=match_record,
            team=current_team,
            defaults={"system": form_info["system"]}
        )
        
        for player_name in form_info["starters"]:
            try:
                p = Player.objects.get(team=current_team, name=player_name)
                formation_record.starting_xi.add(p)
            except Player.DoesNotExist:
                pass

    # Line 3 (Success Path): Record metric details structurally
    logger.info("Successfully completed ingestion sync pipeline processing", extra={
        "extra_data": {"league_name": league.name, "status_code": 200}
    })

    return HttpResponse(
        f"<h3>Data Sync Pipeline Complete!</h3>"
        f"<p>Automated processing finished. Head back to the <a href='/'>Home Dashboard</a> "
        f"to see your updated standings with Goal Difference sorting!</p>"
    )



logger = logging.getLogger(__name__)

def match_detail_view(request, match_id):
    logger.info(f"Fetching record data for match", extra={
        "extra_data": {"match_id": match_id}
    })
    
    try:
        raise ValueError("Match data payload corrupt")
        
    except Exception as e:
        logger.error("Failed to retrieve match metrics", extra={
            "extra_data": {"match_id": match_id, "error_msg": str(e), "status_code": 500}
        })
        return JsonResponse({"status": "error", "message": "Internal error"}, status=500)