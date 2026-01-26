from django.db import models
from django.conf import settings

class Reservation(models.Model):
    TIME_CHOICES = [
        ('AM', '午前'),
        ('PM', '午後'),
    ]
    
    STATUS_CHOICES = [
        ('confirmed', '予約確定'),
        ('cancelled', 'キャンセル済み'),
        ('completed', '来店済み'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='ユーザー',
        null=True, blank=True
    )
    name = models.CharField('お名前', max_length=100)
    date = models.DateField('来店日')
    time_slot = models.CharField('時間帯', max_length=2, choices=TIME_CHOICES)
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='confirmed')
    note = models.TextField('備考（ユーザー）', blank=True)

    admin_memo = models.TextField(
        '管理者メモ',
        blank=True,
        help_text='スタッフ向けメモ（ユーザーには表示されません）'
    )

    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    class Meta:
        ordering = ['-date', 'time_slot']
        unique_together = ('date', 'time_slot')

    def __str__(self):
        return f"{self.date} {self.get_time_slot_display()} - {self.name}"
