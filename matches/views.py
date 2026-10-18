from django.http import HttpResponse
from django.db import models
from .client import SportsApiClient
from .models import League, Team, LeagueTableEntry, Player, Match, TeamFormation
from datetime import datetime, timezone

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
#Original code
    next_match = Match.objects.filter(
        models.Q(home_team__name="FC Barcelona") | models.Q(away_team__name="FC Barcelona")
    ).order_by('match_date').first()
#2 Ijected bug to break the next match fetch logic for testing purposes
 #   next_match = Match.objects.filter(is_finished=True).order_by('match_date').first()  


    # 3. Fetch FC Barcelona's Tactical Formation for that match
    barca_formation = None
    if next_match:
        barca_formation = TeamFormation.objects.filter(
            match=next_match, 
            team__name="FC Barcelona"
        ).first()

    # 4. Fetch the Complete FC Barcelona Squad (grouped by position)
    barca_players = Player.objects.filter(team__name="FC Barcelona").order_by('jersey_number')

    # Build out the HTML template layout
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LaLiga Standings & FC Barcelona Tracker</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f8f9fa; color: #333; }
            h1 { color: #001f3f; border-bottom: 3px solid #001f3f; padding-bottom: 10px; }
            h2 { color: #0056b3; margin-top: 30px; border-bottom: 2px solid #ddd; padding-bottom: 5px; }
            .container { display: flex; gap: 30px; flex-wrap: wrap; }
            .main-content { flex: 2; min-width: 600px; }
            .sidebar { flex: 1; min-width: 300px; background: white; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; max-height: 800px; overflow-y: auto; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
            th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #001f3f; color: white; text-transform: uppercase; font-size: 14px; }
            tr:hover { background-color: #f1f4f9; }
            .pos-col { font-weight: bold; width: 50px; text-align: center; color: #ffc107; background-color: #001f3f; }
            .barca-row { background-color: #fff3f3; font-weight: bold; border-left: 5px solid #a50044; }
            .match-card { background: linear-gradient(135deg, #a50044 0%, #004d98 100%); color: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 25px; }
            .match-card h3 { margin: 0 0 10px 0; font-size: 22px; }
            .sync-btn { display: inline-block; background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
            .sync-btn:hover { background-color: #218838; }
            .player-badge { padding: 6px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
            .position-tag { font-size: 11px; background: #eedcda; color: #a50044; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🏆 Spanish LaLiga & FC Barcelona Hub</h1>
        <p>Live Application Dashboard as of October 15, 2026</p>
        <a href="/matches/sync/" class="sync-btn">🔄 Trigger Live Network API Sync</a>

        <!-- Upcoming Match Widget Banner -->
    """

    if next_match:
        html += f"""
        <div class="match-card">
            <h3>NEXT FIXTURE: {next_match.home_team.name} vs {next_match.away_team.name}</h3>
            <p>📍 <strong>Stadium:</strong> {next_match.stadium}</p>
            <p>📅 <strong>Date & Time:</strong> {next_match.match_date.strftime('%A, %B %d, %Y at %H:%M UTC')}</p>
        """
        if barca_formation:
            html += f"<p>📋 <strong>Barça Tactical System:</strong> {barca_formation.system}</p>"
            html += "<p>🏃 <strong>Starting Lineup Pool:</strong> "
            html += ", ".join([p.name for p in barca_formation.starting_xi.all()]) + "</p>"
        html += "</div>"
    else:
        html += "<div class='match-card'><h3>No upcoming scheduled match details synced.</h3></div>"

    html += """
        <div class="container">
            <!-- Left Side: Official League Table Layout -->
            <div class="main-content">
                <h2>Official League Standings Table</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Pos</th>
                            <th>Club Team</th>
                            <th>Pld</th>
                            <th>W</th>
                            <th>D</th>
                            <th>L</th>
                            <th>GF</th>
                            <th>GA</th>
                            <th>GD</th>
                            <th>Pts</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    for idx, entry in enumerate(la_liga_table, start=1):
        row_class = 'class="barca-row"' if "Barcelona" in entry.team.name else ""
        gd_display = f"+{entry.goal_difference}" if entry.goal_difference > 0 else entry.goal_difference
        
        html += f"""
                <tr {row_class}>
                    <td class="pos-col">{idx}</td>
                    <td>{entry.team.name}</td>
                    <td>{entry.matches_played}</td>
                    <td>{entry.wins}</td>
                    <td>{entry.draws}</td>
                    <td>{entry.losses}</td>
                    <td>{entry.goals_for}</td>
                    <td>{entry.goals_against}</td>
                    <td><strong>{gd_display}</strong></td>
                    <td><strong>{entry.points}</strong></td>
                </tr>
        """

    html += """
                    </tbody>
                </table>
            </div>

            <!-- Right Side: Complete FC Barcelona Roster Feed -->
            <div class="sidebar">
                <h2>🔵🔴 FC Barcelona Squad</h2>
                <p>Complete 2026/27 First-Team Roster</p>
    """

    for player in barca_players:
        html += f"""
                <div class="player-badge">
                    <span><strong>#{player.jersey_number}</strong> {player.name}</span>
                    <span class="position-tag">{player.position}</span>
                </div>
        """
        
    if not barca_players:
        html += "<p>No active roster data ingested yet. Run sync loop.</p>"

    html += """
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)


def sync_and_render_match(request):
    """
    Executes the ingestion sync pipeline.
    Parses the full 20-team ecosystem from client.py and saves it cleanly.
    """
    client = SportsApiClient()
    try:
        api_data = client.fetch_latest_match()
    except Exception as e:
        return HttpResponse(f"<h3>Sync Failed: {str(e)}</h3>")
    
    if not api_data:
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
        
        # update_or_create relies on unique league/team pairing to dissolve duplicate entries
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
        
        # Seed out the active rosters safely
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
        
    # 4. Ingest & Store Match Tactical Lineups (Formations)
    for team_name, form_info in api_data["formations"].items():
        current_team = Team.objects.get(name=team_name)
        formation_record, _ = TeamFormation.objects.get_or_create(
            match=match_record,
            team=current_team,
            defaults={"system": form_info["system"]}
        )
        
        # ADD THESE LINES RIGHT HERE (Indented inside the formations loop)
        for player_name in form_info["starters"]:
            try:
                p = Player.objects.get(team=current_team, name=player_name)
                formation_record.starting_xi.add(p)
            except Player.DoesNotExist:
                pass

    # Unindented back to the main function level at the very end of the file
    return HttpResponse(
        f"<h3>Data Sync Pipeline Complete!</h3>"
        f"<p>Automated processing finished. Head back to the <a href='/'>Home Dashboard</a> "
        f"to see your updated standings with Goal Difference sorting!</p>"
    )
