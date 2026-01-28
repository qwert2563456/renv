from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from reservations.models import Reservation
from reservations.email_utils import send_reminder_email


class Command(BaseCommand):
    help = '予約前日のリマインダーメールを送信します'

    def handle(self, *args, **options):
        # 明日の予約を取得
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        reservations = Reservation.objects.filter(
            date=tomorrow,
            status='confirmed'
        )
        
        count = 0
        for reservation in reservations:
            if send_reminder_email(reservation):
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ リマインダーメール送信: {reservation.name} ({reservation.date})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ リマインダーメール送信失敗: {reservation.name} ({reservation.date})'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n合計 {count} 件のリマインダーメールを送信しました。')
        )
