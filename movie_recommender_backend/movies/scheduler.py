import schedule
import time
import threading

def start_scheduler():
    """
    Runs in a background thread.
    Every Sunday at 3am, fetches new movies from TMDB.
    This keeps your database fresh without any manual work.
    """
    def job():
        print("⏰ Scheduled TMDB refresh starting...")
        try:
            # We need Django set up before importing models
            import django
            from movies.tmdb_fetcher import full_refresh
            full_refresh(pages=100)
        except Exception as e:
            print(f"Scheduler error: {e}")

    schedule.every().sunday.at("03:00").do(job)

    def run():
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour

    # Run in background so it doesn't block Django
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    print("✅ Movie refresh scheduler started (runs every Sunday at 3am)")