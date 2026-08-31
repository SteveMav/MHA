from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('panier/', views.cart_detail, name='cart_detail'),
    path('panier/ajouter/<int:product_id>/', views.cart_add, name='cart_add'),
    path('panier/modifier/', views.cart_update, name='cart_update'),
    path('panier/supprimer/<int:product_id>/<int:variant_id>/', views.cart_remove, name='cart_remove'),
    path('commander/', views.checkout, name='checkout'),
    path('commande/confirmation/<str:numero_commande>/', views.order_confirmation, name='order_confirmation'),
    path('suivi/', views.order_tracking, name='order_tracking'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
