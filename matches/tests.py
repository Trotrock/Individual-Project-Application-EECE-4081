from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Match, Team, League, LeagueTableEntry

class MatchDashboardAcceptanceTest(TestCase):
    def test_match_displays_on_dashboard_at_exact_time_boundary(self):
        """
        Acceptance Test: Verifies that an upcoming match exactly at the 
        current time boundary correctly renders on the UI boundary layout.
        """
        league = League.objects.create(name="LaLiga")
        home = Team.objects.create(name="FC Barcelona")
        away = Team.objects.create(name="Real Madrid")
        
        # Testing the exact boundary condition using an explicit timezone object
        boundary_time = datetime(2026, 10, 19, 21, 0, tzinfo=timezone.UTC)
        
        Match.objects.create(
            league=league,
            home_team=home,
            away_team=away,
            match_date=boundary_time
        )

        url = reverse('standings_dashboard')  
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FC Barcelona")
        self.assertContains(response, "Real Madrid")


class LeagueTablePropertyUnitTest(SimpleTestCase):
    def test_goal_difference_calculation_with_negative_differential(self):
        """
        Unit Test: Asserts the pure calculation behavior of the domain logic.
        Runs completely in-memory with zero database dependencies (Fast & Isolated).
        """
        # 1. Arrange - Construct objects cleanly in memory without .create() or .save()
        mock_team = Team(name="Málaga CF")
        entry = LeagueTableEntry(
            team=mock_team,
            goals_for=4,
            goals_against=13
        )
        
        # 2. Act - Invoke the pure computing business logic surface
        gd = entry.goal_difference
        
        # 3. Assert - Check the computational outcome instead of database boilerplate
        self.assertEqual(gd, -9)
