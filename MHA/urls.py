"""
URL configuration for MHA project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap
from main.sitemaps import AnnouncementSitemap, StaticViewSitemap, GallerySitemap, ShopSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'announcements': AnnouncementSitemap,
    'gallery': GallerySitemap,
    'shop': ShopSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('main.urls')),
    path('news/', include('announcements.urls')),
    path('galerie/', include('gallery.urls')),
    path('boutique/', include('shop.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

