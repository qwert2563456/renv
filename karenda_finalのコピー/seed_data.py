#!/usr/bin/env python
"""
初期データ作成スクリプト
このスクリプトを実行して、デモ用の初期データを作成します。

使用方法:
    python manage.py shell < seed_data.py
    または
    python seed_data.py
"""

import os
import django
from datetime import time, date, timedelta

# Django設定の初期化
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reservation_project.settings')
django.setup()

from django.contrib.auth.models import User
from reservations.models import (
    ServiceMenu, TimeSlot, Holiday, Reservation, BikeInfo
)

def create_admin_user():
    """管理者ユーザーを作成"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@renv.local', 'admin123')
        print("✓ 管理者ユーザーを作成しました (username: admin, password: admin123)")
    else:
        print("✓ 管理者ユーザーは既に存在します")

def create_demo_user():
    """デモ用ユーザーを作成"""
    if not User.objects.filter(username='demo').exists():
        User.objects.create_user('demo', 'demo@renv.local', 'demo123')
        print("✓ デモユーザーを作成しました (username: demo, password: demo123)")
    else:
        print("✓ デモユーザーは既に存在します")

def create_service_menus():
    """修理・整備メニューを作成"""
    menus = [
        {
            'name': 'ホイール組み',
            'estimated_duration': 120,
            'base_price': 8000,
            'price_display': '8,000円～',
            'description': 'ホイールの組み立て・調整を行います。スポーク張力の調整も含まれます。'
        },
        {
            'name': 'フレーム塗装',
            'estimated_duration': 240,
            'base_price': 15000,
            'price_display': '15,000円～',
            'description': 'フレームの塗装・補修を行います。色選択可能です。'
        },
        {
            'name': 'メンテナンス',
            'estimated_duration': 90,
            'base_price': 5000,
            'price_display': '5,000円～',
            'description': 'チェーン交換、ディレイラー調整、ブレーキ調整など基本的なメンテナンス。'
        },
        {
            'name': 'フィッティング',
            'estimated_duration': 60,
            'base_price': 3000,
            'price_display': '3,000円～',
            'description': 'ポジション調整、サドル高さ調整など、快適な乗車姿勢をサポート。'
        },
        {
            'name': 'カスタムオーダー相談',
            'estimated_duration': 45,
            'base_price': 0,
            'price_display': '応相談',
            'description': 'カスタマイズやアップグレードについての相談。見積もり無料。'
        },
    ]
    
    for menu_data in menus:
        menu, created = ServiceMenu.objects.get_or_create(
            name=menu_data['name'],
            defaults={
                'estimated_duration': menu_data['estimated_duration'],
                'base_price': menu_data['base_price'],
                'price_display': menu_data['price_display'],
                'description': menu_data['description'],
            }
        )
        if created:
            print(f"✓ メニュー「{menu.name}」を作成しました")
        else:
            print(f"✓ メニュー「{menu.name}」は既に存在します")

def create_time_slots():
    """予約可能な時間枠を作成"""
    slots = [
        {'start_time': time(10, 0), 'end_time': time(12, 0), 'capacity': 2},
        {'start_time': time(12, 0), 'end_time': time(14, 0), 'capacity': 1},
        {'start_time': time(14, 0), 'end_time': time(16, 0), 'capacity': 2},
        {'start_time': time(16, 0), 'end_time': time(18, 0), 'capacity': 2},
    ]
    
    for slot_data in slots:
        slot, created = TimeSlot.objects.get_or_create(
            start_time=slot_data['start_time'],
            end_time=slot_data['end_time'],
            defaults={'capacity': slot_data['capacity']}
        )
        if created:
            print(f"✓ 時間枠「{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}」を作成しました")
        else:
            print(f"✓ 時間枠「{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}」は既に存在します")

def create_holidays():
    """定休日を作成"""
    # 毎週月曜日を定休日
    holiday, created = Holiday.objects.get_or_create(
        date=date.today(),
        defaults={
            'name': '定休日（毎週月曜日）',
            'is_permanent': True,
            'day_of_week': 0,  # 月曜日
        }
    )
    if created:
        print("✓ 定休日「毎週月曜日」を作成しました")
    else:
        print("✓ 定休日「毎週月曜日」は既に存在します")
    
    # 年末年始
    holiday, created = Holiday.objects.get_or_create(
        date=date(2025, 1, 1),
        defaults={
            'name': '年始休業',
            'is_permanent': False,
        }
    )
    if created:
        print("✓ 臨時休業「年始休業」を作成しました")
    else:
        print("✓ 臨時休業「年始休業」は既に存在します")

def main():
    print("\n" + "="*50)
    print("renv - 初期データ作成スクリプト")
    print("="*50 + "\n")
    
    print("【ユーザー作成】")
    create_admin_user()
    create_demo_user()
    
    print("\n【メニュー作成】")
    create_service_menus()
    
    print("\n【時間枠作成】")
    create_time_slots()
    
    print("\n【休日設定】")
    create_holidays()
    
    print("\n" + "="*50)
    print("初期データ作成が完了しました！")
    print("="*50)
    print("\n【ログイン情報】")
    print("  管理者: username=admin, password=admin123")
    print("  デモユーザー: username=demo, password=demo123")
    print("\n【アクセスURL】")
    print("  ユーザー向け予約画面: http://localhost:8000/")
    print("  管理者ダッシュボード: http://localhost:8000/dashboard/")
    print("  Django Admin: http://localhost:8000/admin/")
    print("\n")

if __name__ == '__main__':
    main()
