from django.core.management.base import BaseCommand
from django.utils.timezone import localdate
from base.models import Medicine
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = "Send email reminders for medicines expiring in 30, 7, 1, or 0 days"

    def handle(self, *args, **kwargs):
        today = localdate()  # Safe for timezone
        reminder_days = [30, 7, 1, 0]

        self.stdout.write(f"Running expiry reminder for date: {today}")

        for days in reminder_days:
            target_date = today + timedelta(days=days)
            self.stdout.write(f"Checking medicines expiring on: {target_date}")

            # ✅ CORRECT for DateField
            expiring_meds = Medicine.objects.filter(expiry_date=target_date)

            self.stdout.write(f"Found {expiring_meds.count()} medicines")

            for med in expiring_meds:
                user = med.user

                if not user or not user.email:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping {med.medicine_name}: user/email missing"
                        )
                    )
                    continue

                days_left = (target_date - today).days
                if days_left == 0:
                    when = "today"
                elif days_left == 1:
                    when = "tomorrow"
                else:
                    when = f"in {days_left} days"

                subject = f"Medicine Expiry Reminder: {med.medicine_name}"

                message = (
                    f"Dear {user.username},\n\n"
                    f"Your medicine '{med.medicine_name}' is expiring {when} "
                    f"(on {target_date}).\n\n"
                    f"Please take necessary action.\n\n"
                    f"Regards,\n"
                    f"First Aid Kit Management System"
                )

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Email sent to {user.email} for "
                        f"{med.medicine_name} ({when})"
                    )
                )
