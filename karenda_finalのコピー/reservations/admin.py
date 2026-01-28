from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'time_slot',
        'visit_reason',
        'name',
        'has_admin_memo',
        'created_at',
    )

    list_filter = (
        'date',
        'time_slot',
        'visit_reason',
    )

    search_fields = (
        'name',
        'note',
        'admin_memo',
    )

    ordering = ('date', 'time_slot')

    fieldsets = (
        ('予約情報', {
            'fields': (
                'name',
                'date',
                'time_slot',
                'visit_reason',
            )
        }),
        ('ユーザー備考', {
            'fields': ('note',)
        }),
        ('管理者メモ（非公開）', {
            'fields': ('admin_memo',)
        }),
    )

    def has_admin_memo(self, obj):
        return bool(obj.admin_memo)

    has_admin_memo.short_description = '管理メモ'
    has_admin_memo.boolean = True