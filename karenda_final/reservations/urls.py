from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reserve/', views.reserve, name='reserve'),
    path('reserve/done/<int:pk>/', views.reserve_done, name='reserve_done'),
    path('reservation/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('reservation/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('signup/', views.signup, name='signup'),
]
