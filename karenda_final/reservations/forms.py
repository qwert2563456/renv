from django import forms
from .models import Reservation, BikeInfo, BikeImage, ServiceMenu
from django.core.exceptions import ValidationError
from datetime import date


class ReservationForm(forms.ModelForm):
    time_slot = forms.ChoiceField(
        choices=Reservation.TIME_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label='時間帯'
    )
    
    visit_reason = forms.ChoiceField(
        choices=Reservation.VISIT_REASON_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label='来店理由'
    )

    class Meta:
        model = Reservation
        fields = ['name', 'date', 'time_slot', 'service_menu', 'visit_reason', 'note']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '山田 太郎',
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'service_menu': forms.Select(attrs={
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
        visit_reason = cleaned_data.get('visit_reason')
        note = cleaned_data.get('note')

        if visit_reason == 'other' and not note:
            raise ValidationError('来店理由で「その他」を選択した場合は、備考欄への入力が必須です。')

        if date_value and time_slot:
            if Reservation.objects.filter(
                date=date_value,
                time_slot=time_slot,
                status='confirmed'
            ).exists():
                raise ValidationError('その日付・時間帯はすでに予約されています。')

        return cleaned_data


class BikeInfoForm(forms.ModelForm):
    class Meta:
        model = BikeInfo
        fields = ['manufacturer', 'model_name', 'details', 'has_parts_brought_in']
        widgets = {
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'トレック、キャノンデール など'
            }),
            'model_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Domane AL 5 など'
            }),
            'details': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': '修理・整備箇所の詳細をお知らせください'
            }),
            'has_parts_brought_in': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class BikeImageForm(forms.ModelForm):
    class Meta:
        model = BikeImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }


class ServiceMenuForm(forms.ModelForm):
    class Meta:
        model = ServiceMenu
        fields = ['name', 'description', 'estimated_duration', 'price_estimate', 'price_display', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
            'estimated_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '15'
            }),
            'price_estimate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'price_display': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '¥5,000〜'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
