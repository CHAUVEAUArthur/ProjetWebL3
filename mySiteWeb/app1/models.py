from django.db import models
from django.contrib.auth.models import User

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    room = models.CharField(max_length=100)
    participants = models.IntegerField()
    participant1 = models.EmailField(default='default@example.com')
    participant2 = models.EmailField(default='default@example.com')
    participant3 = models.EmailField(blank=True, null=True)
    participant4 = models.EmailField(blank=True, null=True)
    terms = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.room} - {self.start_time}"