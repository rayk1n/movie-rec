from django.db import models

class Movie(models.Model):
    movie_id     = models.IntegerField(unique=True)
    title        = models.CharField(max_length=500)
    tags         = models.TextField()
    release_year = models.IntegerField(null=True, blank=True)   # ← NEW
    poster_path  = models.CharField(max_length=500, blank=True) # ← NEW
    vote_average = models.FloatField(default=0.0)               # ← NEW

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.release_year})"
    



    
