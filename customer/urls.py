from . import views
from django.urls import path

urlpatterns = [
    path('registerUser/', views.registerUser, name='registerUser'),
    path('custDashboard/', views.custDashboard, name='custDashboard'),
    path('profile/', views.profile, name='profile'),
    path('bookings/', views.bookings, name='bookings'),
    path('orders/', views.orders, name='orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('place_order/', views.place_order, name='place_order'),
    path('order_complete/', views.order_complete, name='order_complete'),
]