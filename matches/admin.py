from django.contrib import admin
from .models import League, Team, LeagueTableEntry, Player, Match, TeamFormation

admin.site.register(League)
admin.site.register(Team)
admin.site.register(LeagueTableEntry)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(TeamFormation)
