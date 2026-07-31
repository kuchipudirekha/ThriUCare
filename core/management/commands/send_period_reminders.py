from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from core.models import PeriodTracker
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Send email reminders 2 days before the next expected period date"

    def handle(self, *args, **options):
        today = date.today()
        reminders_sent = 0

        self.stdout.write("🔍 Checking for users who need reminders...")

        trackers = PeriodTracker.objects.select_related("user").all()

        for tracker in trackers:
            try:
                next_date = tracker.next_period_date
                user_email = tracker.user.email
                username = tracker.user.username
            except Exception:
                continue

            # Skip if no next period date or no email
            if not next_date or not user_email:
                continue

            # Send reminder 2 days before next period
            remind_day = next_date - timedelta(days=2)

            if remind_day <= today:
                subject = "⏰ Period Reminder - Thriucare"
                message = (
                    f"Hi {username},\n\n"
                    f"This is a friendly reminder that your period is expected in 2 days "
                    f"(around {next_date}). Take care and stay healthy!\n\n"
                    f"— Thriucare Team"
                )

                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user_email],
                        fail_silently=False,
                    )
                    reminders_sent += 1
                    self.stdout.write(self.style.SUCCESS(f"✅ Sent reminder to {user_email}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Failed to send to {user_email}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"📨 Done. Total reminders sent: {reminders_sent}"))
