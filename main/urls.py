from django.urls import path
from . import views
from . import admin_portal_views

urlpatterns = [
    path('', views.index, name='index'),
    path('programmes/', views.programmes, name='programmes'),
    path('programmes/<slug:slug>/', views.programme_detail, name='programme_detail'),
    path('methode/', views.methode, name='methode'),
    path('staff/', views.staff, name='staff'),
    path('inscription/', views.inscription, name='inscription'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('llms.txt', views.llms_txt, name='llms_txt'),

    # Espace Administration (/gestion/)
    path('gestion/', admin_portal_views.admin_dashboard, name='admin_dashboard'),
    path('gestion/utilisateurs/', admin_portal_views.admin_users_list, name='admin_users_list'),
    path('gestion/utilisateurs/<int:user_id>/', admin_portal_views.admin_user_detail, name='admin_user_detail'),
    path('gestion/abonnements/<int:sub_id>/action/', admin_portal_views.admin_subscription_quick_action, name='admin_subscription_quick_action'),
    path('gestion/horaires/', admin_portal_views.admin_schedules, name='admin_schedules'),
    path('gestion/horaires/<int:pk>/supprimer/', admin_portal_views.admin_schedule_delete, name='admin_schedule_delete'),
    path('gestion/contenu/', admin_portal_views.admin_site_content, name='admin_site_content'),
    path('gestion/contenu/pilier/<int:pk>/supprimer/', admin_portal_views.admin_pillar_delete, name='admin_pillar_delete'),
    path('gestion/galerie/', admin_portal_views.admin_gallery, name='admin_gallery'),
    path('gestion/galerie/album/<int:pk>/supprimer/', admin_portal_views.admin_album_delete, name='admin_album_delete'),
    path('gestion/galerie/photo/<int:pk>/supprimer/', admin_portal_views.admin_photo_delete, name='admin_photo_delete'),
    path('gestion/annonces/', admin_portal_views.admin_announcements, name='admin_announcements'),
    path('gestion/annonces/<int:pk>/supprimer/', admin_portal_views.admin_announcement_delete, name='admin_announcement_delete'),
]
