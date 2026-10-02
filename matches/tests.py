from django.test import TestCase
from .models import Match

class MatchModelTest(TestCase):
    def test_match_creation(self):
        # Verifies the storage layer integrates successfully
        match = Match.objects.create(opponent="Real Madrid", match_date="2026-10-25")
        self.assertEqual(match.opponent, "Real Madrid")
        self.assertEqual(str(match), "FC Barcelona vs Real Madrid")
