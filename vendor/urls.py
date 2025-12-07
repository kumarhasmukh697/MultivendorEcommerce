from django.urls import path
from . import views

urlpatterns = [

    path('registerVendor/',views.registerVendor,name='registerVendor'),
    path('vendorDashboard/',views.vendorDashboard,name='vendorDashboard'),
    path('vprofile/', views.vprofile, name='vprofile'),

    path('menu_builder/', views.menu_builder, name='menu_builder'),
    path('menu_builder/category/<int:pk>/', views.fooditems_by_category, name='fooditems_by_category'),

    # CRUD Category
    path('menu_builder/add_category/', views.add_category, name='add_category'),
    path('menu_builder/edit_category/<int:pk>/', views.edit_category, name='edit_category'),
    path('menu_builder/delete_category/<int:pk>/', views.delete_category, name='delete_category'),
    path('menu_builder/add_fooditem/', views.add_fooditem, name='add_fooditem'),

    # CRUD FoodItem
    path('menu_builder/edit_fooditem/<int:pk>/', views.edit_fooditem, name='edit_fooditem'),
    path('menu_builder/delete_fooditem/<int:pk>/', views.delete_fooditem, name='delete_fooditem'),

    path('opening_hours/', views.opening_hours, name='opening_hours'),
     path('add-opening-hour/', views.add_opening_hour, name='add_opening_hour'),
    path('delete-opening-hour/', views.delete_opening_hour, name='delete_opening_hour'),


    path('orders/', views.orders, name='orders'),
    path('particular_order/<int:order_number>/', views.particular_order, name='particular_order'),
    path('earnings/', views.earnings, name='earnings')
]