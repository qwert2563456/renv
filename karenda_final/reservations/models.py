from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class ServiceMenu(models.Model):
    """修理・整備メニュー"""
    name = models.CharField('メニュー名', max_length=100, unique=True)
    description = models.TextField('説明', blank=True)
    estimated_duration = models.IntegerField(
        '想定作業時間（分）',
        validators=[MinValueValidator(15)]
    )
    price_estimate = models.DecimalField(
        '料金目安（数値）',
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)]
    )
    price_display = models.CharField(
        '表示用料金テキスト',
        max_length=100,
        help_text='例: ¥5,000〜'
    )
    is_active = models.BooleanField('有効', default=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = '修理・整備メニュー'
        verbose_name_plural = '修理・整備メニュー'

    def __str__(self):
        return f"{self.name} ({self.price_display})"


class Reservation(models.Model):
    TIME_CHOICES = [
        ('AM', '午前'),
        ('PM', '午後'),
    ]
    
    STATUS_CHOICES = [
        ('confirmed', '予約確定'),
        ('cancelled', 'キャンセル済み'),
        ('in_progress', '作業中'),
        ('completed', '来店済み'),
    ]
    
    VISIT_REASON_CHOICES = [
        ('pickup', '受け取り'),
        ('repair', '修理'),
        ('consultation', '相談'),
        ('other', 'その他（備考欄に入力必須）'),
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
    
    # 新規追加：サービスメニュー
    service_menu = models.ForeignKey(
        ServiceMenu,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reservations',
        verbose_name='修理・整備メニュー'
    )
    
    visit_reason = models.CharField(
        '来店理由',
        max_length=20,
        choices=VISIT_REASON_CHOICES,
        default='consultation'
    )
    status = models.CharField(
        'ステータス',
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed'
    )
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


class BikeInfo(models.Model):
    """自転車情報"""
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='bike_info',
        verbose_name='予約'
    )
    manufacturer = models.CharField('メーカー名', max_length=100)
    model_name = models.CharField('モデル名', max_length=100)
    details = models.TextField('修理・整備箇所の詳細')
    has_parts_brought_in = models.BooleanField(
        'パーツ持ち込み有無',
        default=False
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = '自転車情報'
        verbose_name_plural = '自転車情報'

    def __str__(self):
        return f"{self.manufacturer} {self.model_name} - {self.reservation}"


class BikeImage(models.Model):
    """不具合箇所の写真"""
    bike_info = models.ForeignKey(
        BikeInfo,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='自転車情報'
    )
    image = models.ImageField('画像', upload_to='bike_images/%Y/%m/%d/')
    uploaded_at = models.DateTimeField('アップロード日時', auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']
        verbose_name = '自転車画像'
        verbose_name_plural = '自転車画像'

    def __str__(self):
        return f"Image for {self.bike_info}"


class TimeSlot(models.Model):
    """予約可能な時間枠"""
    start_time = models.TimeField('開始時間')
    end_time = models.TimeField('終了時間')
    capacity = models.IntegerField(
        '同時対応可能数',
        default=1,
        validators=[MinValueValidator(1)]
    )
    is_active = models.BooleanField('有効', default=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        ordering = ['start_time']
        verbose_name = '時間枠'
        verbose_name_plural = '時間枠'
        unique_together = ('start_time', 'end_time')

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')} (容量: {self.capacity})"

    @property
    def duration_minutes(self):
        """時間枠の長さ（分）"""
        from datetime import datetime
        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)
        return int((end_dt - start_dt).total_seconds() / 60)


class BusinessDay(models.Model):
    """営業日管理"""
    date = models.DateField('日付', unique=True)
    is_open = models.BooleanField('営業', default=True)
    note = models.CharField('備考', max_length=200, blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        ordering = ['date']
        verbose_name = '営業日'
        verbose_name_plural = '営業日'

    def __str__(self):
        status = '営業' if self.is_open else '休業'
        return f"{self.date} - {status}"


class Holiday(models.Model):
    """定休日・臨時休業日"""
    date = models.DateField('日付', unique=True)
    name = models.CharField('名称', max_length=100)
    is_permanent = models.BooleanField(
        '定休日',
        default=False,
        help_text='毎週同じ曜日の定休日の場合はチェック'
    )
    day_of_week = models.IntegerField(
        '曜日',
        choices=[
            (0, '月'),
            (1, '火'),
            (2, '水'),
            (3, '木'),
            (4, '金'),
            (5, '土'),
            (6, '日'),
        ],
        null=True, blank=True
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        ordering = ['date']
        verbose_name = '休日'
        verbose_name_plural = '休日'

    def __str__(self):
        return f"{self.date} - {self.name}"


class WorkHistory(models.Model):
    """作業履歴・見積もり"""
    STATUS_CHOICES = [
        ('pending', '予約中'),
        ('in_progress', '作業中'),
        ('completed', '完了'),
    ]

    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='work_history',
        verbose_name='予約'
    )
    estimated_amount = models.DecimalField(
        '見積金額',
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        null=True, blank=True
    )
    actual_amount = models.DecimalField(
        '確定金額',
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        null=True, blank=True
    )
    completion_photo = models.ImageField(
        '完了写真',
        upload_to='completion_photos/%Y/%m/%d/',
        null=True, blank=True
    )
    admin_comment = models.TextField(
        '管理者コメント',
        blank=True,
        help_text='作業内容、注意事項などをメモ'
    )
    status = models.CharField(
        'ステータス',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = '作業履歴'
        verbose_name_plural = '作業履歴'

    def __str__(self):
        return f"{self.reservation} - {self.get_status_display()}"
