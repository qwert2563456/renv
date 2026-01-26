from django import forms
from .models import Reservation
from django.core.exceptions import ValidationError
from datetime import date

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'date', 'time_slot', 'note']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '山田 太郎',
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'note': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'ご不明な点やご要望があればお知らせください'
            }),
        }

    def clean_date(self):
        date_value = self.cleaned_data.get('date')
        if date_value and date_value < date.today():
            raise ValidationError('過去の日付は選択できません。')
        return date_value

    def clean(self):
        cleaned_data = super().clean()
        date_value = cleaned_data.get('date')
        time_slot = cleaned_data.get('time_slot')

        if date_value and time_slot:
            if Reservation.objects.filter(
                date=date_value,
                time_slot=time_slot,
                status='confirmed'
            ).exists():
                raise ValidationError('その日付・時間帯はすでに予約されています。')

        return cleaned_data