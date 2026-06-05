from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from tracker import check_prices

scheduler = BlockingScheduler()

# Runs price checker every wednesday 9am
@scheduler.scheduled_job("cron", day_of_week="wed", hour=9, minute=0)
def weekly_check():
    print(f"⏰ Running weekly price check - {datetime.now()}")
    check_prices()

if __name__ == "__main__":
    print("🕐 Scheduler started - will check prices every Wednesday at 9am")
    print("   Keep this running in the background!")
    print("   Press Ctrl+C to stop\n")
    scheduler.start()