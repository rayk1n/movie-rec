from django.db import models

# Create your models here.

class Movie(models.Model):
    movie_id = models.IntegerField(unique=True)     
    title    = models.CharField(max_length=500)     
    tags     = models.TextField()                   

    class Meta:
        ordering = ['title']  

    def __str__(self):
        return self.title
