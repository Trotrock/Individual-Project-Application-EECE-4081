from django.db import models

# --- LEAGUE & STANDINGS RETRIEVAL ---

class League(models.Model):
    """Represents a competition like LaLiga or Champions League."""
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100, blank=True)
    season = models.CharField(max_length=20, default="2026/2027")

    def __str__(self):
        return f"{self.name} ({self.season})"


class Team(models.Model):
    """Represents a football club participating in leagues."""
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=10, blank=True)
    logo_url = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class LeagueTableEntry(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="standings")
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    matches_played = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    
    # NEW FIELDS: Add tracking metrics for goals
    goals_for = models.PositiveIntegerField(default=0)
    goals_against = models.PositiveIntegerField(default=0)

    @property
    def goal_difference(self):
        """Dynamically calculates G/D (Goals For minus Goals Against)"""
        return self.goals_for - self.goals_against

    class Meta:
        # Default order sorts by points descending, then by goal differential descending!
        ordering = ['position']
        unique_together = ('league', 'team')

    def __str__(self):
        return f"#{self.position} {self.team.name}"


# --- ROSTER & TACTICS ---

class Player(models.Model):
    """Represents an active player belonging to a specific team roster."""
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DF', 'Defender'),
        ('MF', 'Midfielder'),
        ('FW', 'Forward'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    name = models.CharField(max_length=100)
    jersey_number = models.PositiveIntegerField()
    position = models.CharField(max_length=2, choices=POSITION_CHOICES)
    is_injured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.position}) - {self.team.name}"


# --- MATCH MANAGEMENT ---

class Match(models.Model):
    """Expanded match entity linking the live feed to teams and leagues."""
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="matches")
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    match_date = models.DateTimeField()
    stadium = models.CharField(max_length=150, default="Camp Nou")
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"


class TeamFormation(models.Model):
    """Captures tactical lineup details for a team in a specific match."""
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="formations")
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    system = models.CharField(max_length=10, help_text="e.g., 4-3-3, 3-4-3")
    starting_xi = models.ManyToManyField(Player, related_name="started_matches")
    substitutes = models.ManyToManyField(Player, related_name="benched_matches", blank=True)

    def __str__(self):
        return f"{self.team.name} {self.system} layout for Match ID {self.match.id}"
