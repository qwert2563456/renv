from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime


def send_reservation_confirmation_email(reservation):
    """予約完了メールを送信"""
    if not reservation.user or not reservation.user.email:
        return False
    
    context = {
        'reservation': reservation,
        'site_name': 'renv',
    }
    
    subject = f'【renv】予約完了のお知らせ - {reservation.date.strftime("%Y年%m月%d日")}'
    
    # テキストメール
    message = f"""
{reservation.name} 様

この度は、ご予約いただきありがとうございます。

【ご予約内容】
予約番号: #{reservation.id}
来店日: {reservation.date.strftime("%Y年%m月%d日")}
時間帯: {reservation.get_time_slot_display()}
メニュー: {reservation.service_menu.name if reservation.service_menu else "未選択"}

ご不明な点がございましたら、お気軽にお問い合わせください。

renv
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [reservation.user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"メール送信エラー: {e}")
        return False


def send_reminder_email(reservation):
    """予約前日のリマインダーメールを送信"""
    if not reservation.user or not reservation.user.email:
        return False
    
    context = {
        'reservation': reservation,
        'site_name': 'renv',
    }
    
    subject = f'【renv】ご予約のリマインダー - {reservation.date.strftime("%Y年%m月%d日")}'
    
    message = f"""
{reservation.name} 様

明日のご予約をお忘れではありませんか？

【ご予約内容】
予約番号: #{reservation.id}
来店日: {reservation.date.strftime("%Y年%m月%d日")}
時間帯: {reservation.get_time_slot_display()}
メニュー: {reservation.service_menu.name if reservation.service_menu else "未選択"}

ご来店の際は、予約時間の5分前にお越しください。

キャンセルが必要な場合は、マイページからお手続きください。

renv
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [reservation.user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"メール送信エラー: {e}")
        return False


def send_work_completion_email(work_history):
    """作業完了メールを送信"""
    reservation = work_history.reservation
    
    if not reservation.user or not reservation.user.email:
        return False
    
    subject = f'【renv】作業完了のお知らせ - {reservation.date.strftime("%Y年%m月%d日")}'
    
    message = f"""
{reservation.name} 様

ご来店いただきありがとうございました。
本日の作業が完了いたしましたので、ご報告いたします。

【作業内容】
予約番号: #{reservation.id}
メニュー: {reservation.service_menu.name if reservation.service_menu else "未選択"}
見積金額: {work_history.estimated_amount}円
確定金額: {work_history.actual_amount}円

{work_history.admin_comment}

ご不明な点がございましたら、お気軽にお問い合わせください。

renv
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [reservation.user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"メール送信エラー: {e}")
        return False
