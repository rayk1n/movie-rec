import pandas as pd
from django.core.management.base import BaseCommand
from movies.models import Movie

class Command(BaseCommand):
    """
    Run it with: python manage.py load_movies
    """
    help = 'Loads movies from the cleaned CSV into PostgreSQL'

    def handle(self, *args, **options):
        self.stdout.write("Loading movies from CSV...")

        df = pd.read_csv('ml_data/movies_clean.csv')

        Movie.objects.all().delete()

        movies_to_create = []
        for _, row in df.iterrows():
            movies_to_create.append(Movie(
                movie_id=int(row['movie_id']),
                title=str(row['title']),
                tags=str(row['tags']),
            ))

        Movie.objects.bulk_create(movies_to_create, ignore_conflicts=True)

        count = Movie.objects.count()
        self.stdout.write(self.style.SUCCESS(f"✅ Loaded {count} movies into PostgreSQL!"))