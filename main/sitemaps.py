from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from announcements.models import Annonce
from main.views import PROGRAMS
from gallery.models import GalleryAlbum
from shop.models import Product


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        static_routes = [
            ('index', None),
            ('programmes', None),
            ('methode', None),
            ('staff', None),
            ('inscription', None),
            ('announcements:announcement_list', None),
            ('gallery:gallery_list', None),
            ('shop:product_list', None),
        ]
        program_routes = [('programme_detail', {'slug': program['slug']}) for program in PROGRAMS]
        return static_routes + program_routes

    def location(self, item):
        route_name, kwargs = item
        return reverse(route_name, kwargs=kwargs)


class AnnouncementSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Annonce.objects.all()

    def lastmod(self, obj):
        return obj.date_publication

    def location(self, obj):
        return obj.get_absolute_url()


class GallerySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return GalleryAlbum.objects.filter(est_publie=True)

    def lastmod(self, obj):
        return obj.date_creation

    def location(self, obj):
        return obj.get_absolute_url()


class ShopSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Product.objects.filter(est_actif=True)

    def lastmod(self, obj):
        return obj.date_creation

    def location(self, obj):
        return obj.get_absolute_url()
