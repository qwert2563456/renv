from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import date
from .forms import ReservationForm, BikeInfoForm, BikeImageForm
from .models import Reservation, BikeInfo, BikeImage
from collections import defaultdict
from django.http import JsonResponse

@login_required
def dashboard(request):
    """マイページ：ユーザーの予約一覧を表示"""
    today = date.today()
    
    # 今後の予約（確定のみ）
    upcoming_reservations = Reservation.objects.filter(
        user=request.user,
        date__gte=today,
        status='confirmed'
    ).order_by('date', 'time_slot')
    
    # 過去の予約
    past_reservations = Reservation.objects.filter(
        user=request.user,
        date__lt=today
    ).order_by('-date', 'time_slot')
    
    context = {
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations,
    }
    return render(request, 'reservations/dashboard.html', context)

@login_required
def reserve(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        bike_form = BikeInfoForm(request.POST)
        # 複数枚の画像アップロードに対応
        files = request.FILES.getlist('images')
        
        if form.is_valid() and bike_form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()
            
            bike_info = bike_form.save(commit=False)
            bike_info.reservation = reservation
            bike_info.save()
            
            for f in files:
                BikeImage.objects.create(bike_info=bike_info, image=f)
                
            messages.success(request, '予約が完了しました。')
            return redirect('reserve_done', pk=reservation.pk)
    else:
        form = ReservationForm()
        bike_form = BikeInfoForm()

    reservations = Reservation.objects.filter(
        status='confirmed',
        date__gte=date.today()
    )

    booked_slots = defaultdict(list)
    for r in reservations:
        booked_slots[str(r.date)].append(r.time_slot)

    return render(request, 'reservations/reserve.html', {
        'form': form,
        'bike_form': bike_form,
        'booked_slots': dict(booked_slots),
    })

@login_required
def reserve_done(request, pk):
    """予約完了画面"""
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    return render(request, 'reservations/reserve_done.html', {'reservation': reservation})

@login_required
def reservation_detail(request, pk):
    """予約詳細画面"""
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    bike_info = getattr(reservation, 'bike_info', None)
    context = {
        'reservation': reservation,
        'bike_info': bike_info,
    }
    return render(request, 'reservations/reservation_detail.html', context)

@login_required
def cancel_reservation(request, pk):
    """予約キャンセル"""
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    
    if request.method == 'POST':
        if reservation.status == 'confirmed':
            reservation.status = 'cancelled'
            reservation.save()
            messages.success(request, '予約をキャンセルしました。')
        return redirect('dashboard')
    
    return render(request, 'reservations/cancel_confirmation.html', {'reservation': reservation})

def signup(request):
    """ユーザー登録"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'アカウントを作成しました。')
            return redirect('reserve')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})
