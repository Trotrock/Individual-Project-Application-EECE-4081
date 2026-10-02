from django.db import models

class Match(models.Model):
    opponent = models.CharField(max_length=100)
    match_date = models.CharField(max_length=50)

    def __str__(self):
        return f"FC Barcelona vs {self.opponent}"
