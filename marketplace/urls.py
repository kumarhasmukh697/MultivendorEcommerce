from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('vendor/<slug:vendor_slug>/', views.listing, name='listing'),
    path('cart/',views.cart, name='cart'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('search/', views.search, name='search'),
    # path('cart/', views.view_cart, name='view_cart'),
    # path('checkout/', views.checkout, name='checkout'),
]    