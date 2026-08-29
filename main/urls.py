from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('programmes/', views.programmes, name='programmes'),
    path('programmes/<slug:slug>/', views.programme_detail, name='programme_detail'),
    path('methode/', views.methode, name='methode'),
    path('staff/', views.staff, name='staff'),
    path('inscription/', views.inscription, name='inscription'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('llms.txt', views.llms_txt, name='llms_txt'),
]
