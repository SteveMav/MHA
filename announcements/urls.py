from django.urls import path
from . import views

app_name = 'announcements'

urlpatterns = [
    path('', views.announcement_list, name='announcement_list'),
    path('create/', views.announcement_create, name='announcement_create'),
    path('<int:pk>/update/', views.announcement_update, name='announcement_update'),
    path('<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
    path('<int:pk>/', views.announcement_detail_legacy, name='announcement_detail_legacy'),
    path('<slug:slug>/', views.announcement_detail, name='announcement_detail'),
]
