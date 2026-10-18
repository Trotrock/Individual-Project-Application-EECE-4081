from django.test import TestCase
from django.urls import reverse
from .models import Match, Team, League
from django.utils import timezone

class MatchDashboardAcceptanceTest(TestCase):
    def test_match_displays_on_dashboard(self):
        league = League.objects.create(name="LaLiga")
        home = Team.objects.create(name="FC Barcelona")
        away = Team.objects.create(name="Real Madrid")
        
        Match.objects.create(
            league=league,
            home_team=home,
            away_team=away,
            match_date=timezone.now()
        )

      
        url = reverse('standings_dashboard')  
        response = self.client.get(url)

     
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FC Barcelona")
        self.assertContains(response, "Real Madrid")


class MatchModelUnitTest(TestCase):
    def test_match_creation_logic(self):
        """Step 2: Unit Test asserting behavior of the underlying data model."""
        # 1. Arrange
        league = League.objects.create(name="LaLiga")
        home = Team.objects.create(name="FC Barcelona")
        away = Team.objects.create(name="Real Madrid")
        
        # 2. Act
        match = Match.objects.create(
            league=league,
            home_team=home,
            away_team=away,
            match_date=timezone.now()
        )
        
        # 3. Assert (Checking fields and string representations directly)
        self.assertEqual(match.away_team.name, "Real Madrid")
        self.assertEqual(str(match), "FC Barcelona vs Real Madrid")
