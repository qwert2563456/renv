from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import date, timedelta
from reservations.models import (
    Reservation, ServiceMenu, BikeInfo, TimeSlot, 
    Holiday, BusinessDay, WorkHistory
)
from reservations.forms import ServiceMenuForm, ReservationForm


def is_staff(user):
    """スタッフユーザーかチェック"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff)
def dashboard_home(request):
    """管理者ダッシュボード - ホーム"""
    today = date.today()
    
    # 本日の予約
    today_reservations = Reservation.objects.filter(
        date=today,
        status__in=['confirmed', 'in_progress']
    ).select_related('service_menu', 'user')
    
    # 明日以降の予約（確定分）
    upcoming_reservations = Reservation.objects.filter(
        date__gte=today + timedelta(days=1),
        status='confirmed'
    ).select_related('service_menu', 'user')[:10]
    
    # ステータス別集計
    status_summary = Reservation.objects.filter(
        date__gte=today
    ).values('status').annotate(count=Count('id'))
    
    context = {
        'today_reservations': today_reservations,
        'upcoming_reservations': upcoming_reservations,
        'status_summary': status_summary,
        'today': today,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
@user_passes_test(is_staff)
def reservation_list(request):
    """予約一覧"""
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    reservations = Reservation.objects.select_related('service_menu', 'user')
    
    if status:
        reservations = reservations.filter(status=status)
    
    if date_from:
        reservations = reservations.filter(date__gte=date_from)
    
    if date_to:
        reservations = reservations.filter(date__lte=date_to)
    
    reservations = reservations.order_by('-date', 'time_slot')
    
    context = {
        'reservations': reservations,
        'status_choices': Reservation.STATUS_CHOICES,
        'current_status': status,
        'current_date_from': date_from,
        'current_date_to': date_to,
    }
    return render(request, 'dashboard/reservation_list.html', context)


@login_required
@user_passes_test(is_staff)
def reservation_detail(request, pk):
    """予約詳細・編集"""
    reservation = get_object_or_404(Reservation, pk=pk)
    bike_info = getattr(reservation, 'bike_info', None)
    work_history = getattr(reservation, 'work_history', None)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, '予約を更新しました。')
            return redirect('dashboard:reservation_detail', pk=pk)
    else:
        form = ReservationForm(instance=reservation)
    
    context = {
        'reservation': reservation,
        'form': form,
        'bike_info': bike_info,
        'work_history': work_history,
    }
    return render(request, 'dashboard/reservation_detail.html', context)


@login_required
@user_passes_test(is_staff)
def work_history_edit(request, pk):
    """作業履歴・見積もり編集"""
    reservation = get_object_or_404(Reservation, pk=pk)
    work_history, created = WorkHistory.objects.get_or_create(reservation=reservation)
    
    if request.method == 'POST':
        estimated_amount = request.POST.get('estimated_amount')
        actual_amount = request.POST.get('actual_amount')
        admin_comment = request.POST.get('admin_comment')
        status = request.POST.get('status')
        completion_photo = request.FILES.get('completion_photo')
        
        if estimated_amount:
            work_history.estimated_amount = estimated_amount
        if actual_amount:
            work_history.actual_amount = actual_amount
        if admin_comment:
            work_history.admin_comment = admin_comment
        if status:
            work_history.status = status
        if completion_photo:
            work_history.completion_photo = completion_photo
        
        work_history.save()
        messages.success(request, '作業履歴を更新しました。')
        return redirect('dashboard:reservation_detail', pk=pk)
    
    context = {
        'reservation': reservation,
        'work_history': work_history,
        'status_choices': WorkHistory.STATUS_CHOICES,
    }
    return render(request, 'dashboard/work_history_edit.html', context)


@login_required
@user_passes_test(is_staff)
def service_menu_list(request):
    """メニュー一覧"""
    menus = ServiceMenu.objects.all().order_by('name')
    
    context = {
        'menus': menus,
    }
    return render(request, 'dashboard/service_menu_list.html', context)


@login_required
@user_passes_test(is_staff)
def service_menu_form(request, pk=None):
    """メニュー追加・編集"""
    if pk:
        menu = get_object_or_404(ServiceMenu, pk=pk)
    else:
        menu = None
    
    if request.method == 'POST':
        form = ServiceMenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            messages.success(request, 'メニューを保存しました。')
            return redirect('dashboard:service_menu_list')
    else:
        form = ServiceMenuForm(instance=menu)
    
    context = {
        'form': form,
        'menu': menu,
        'is_edit': pk is not None,
    }
    return render(request, 'dashboard/service_menu_form.html', context)


@login_required
@user_passes_test(is_staff)
def holiday_list(request):
    """休日一覧"""
    holidays = Holiday.objects.all().order_by('date')
    
    context = {
        'holidays': holidays,
    }
    return render(request, 'dashboard/holiday_list.html', context)


@login_required
@user_passes_test(is_staff)
def holiday_form(request, pk=None):
    """休日追加・編集"""
    if pk:
        holiday = get_object_or_404(Holiday, pk=pk)
    else:
        holiday = None
    
    if request.method == 'POST':
        date_val = request.POST.get('date')
        name = request.POST.get('name')
        is_permanent = request.POST.get('is_permanent') == 'on'
        day_of_week = request.POST.get('day_of_week')
        
        if holiday:
            holiday.date = date_val
            holiday.name = name
            holiday.is_permanent = is_permanent
            holiday.day_of_week = day_of_week if day_of_week else None
            holiday.save()
        else:
            Holiday.objects.create(
                date=date_val,
                name=name,
                is_permanent=is_permanent,
                day_of_week=day_of_week if day_of_week else None
            )
        
        messages.success(request, '休日を保存しました。')
        return redirect('dashboard:holiday_list')
    
    context = {
        'holiday': holiday,
        'day_of_week_choices': Holiday._meta.get_field('day_of_week').choices,
        'is_edit': pk is not None,
    }
    return render(request, 'dashboard/holiday_form.html', context)
