from django.core.management.base import BaseCommand
from movies.tmdb_fetcher import full_refresh

class Command(BaseCommand):
    help = 'Fetches latest movies from TMDB API and rebuilds the recommendation engine'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=100,
            help='Number of pages to fetch from TMDB (20 movies per page, default: 100)'
        )

    def handle(self, *args, **options):
        pages = options['pages']
        self.stdout.write(f"Starting TMDB refresh ({pages} pages = ~{pages * 20} movies)...")
        total = full_refresh(pages=pages)
        self.stdout.write(self.style.SUCCESS(f"Done! {total} movies in database."))