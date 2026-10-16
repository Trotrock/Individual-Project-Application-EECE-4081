from django.test import TestCase
from .models import Match, Team, League
from django.utils import timezone

class MatchModelTest(TestCase):
    def test_match_creation(self):
        league = League.objects.create(name="LaLiga")
        home = Team.objects.create(name="FC Barcelona")
        away = Team.objects.create(name="Real Madrid")
        
        match = Match.objects.create(
            league=league,
            home_team=home,
            away_team=away,
            match_date=timezone.now()
        )
        self.assertEqual(match.away_team.name, "Real Madrid")
        self.assertEqual(str(match), "FC Barcelona vs Real Madrid")
