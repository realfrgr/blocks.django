from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title= models.CharField(max_length=200)
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    author=models.ForeignKey(User,on_delete=models.CASCADE,)
    likes=models.ManyToManyField(User,related_name="likes", blank=True)
    
    

    def __str__(self):
        return self.title
    
    def total_likes(self):
        return self.likes.count()
    
    
class Tournament(models.Model):
    name = models.CharField(max_length=200)
    max_participants = models.IntegerField(default=8)
    participants = models.ManyToManyField(User, related_name="tournaments", blank=True)
    is_active = models.BooleanField(default=False) # True when full and started
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, related_name="won_tournaments", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class TournamentMatch(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="matches")
    round_number = models.IntegerField(default=1)
    match_number = models.IntegerField(help_text="Match number within the round")
    player1 = models.ForeignKey(User, related_name="matches_as_p1", null=True, blank=True, on_delete=models.SET_NULL)
    player2 = models.ForeignKey(User, related_name="matches_as_p2", null=True, blank=True, on_delete=models.SET_NULL)
    winner = models.ForeignKey(User, related_name="matches_won", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        p1 = self.player1.username if self.player1 else "TBD"
        p2 = self.player2.username if self.player2 else "TBD"
        return f"{self.tournament.name} - R{self.round_number} - {p1} vs {p2}"



    



