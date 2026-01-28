from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/<int:pk>/work-history/', views.work_history_edit, name='work_history_edit'),
    path('menus/', views.service_menu_list, name='service_menu_list'),
    path('menus/add/', views.service_menu_form, name='service_menu_add'),
    path('menus/<int:pk>/edit/', views.service_menu_form, name='service_menu_edit'),
    path('holidays/', views.holiday_list, name='holiday_list'),
    path('holidays/add/', views.holiday_form, name='holiday_add'),
    path('holidays/<int:pk>/edit/', views.holiday_form, name='holiday_edit'),
]
