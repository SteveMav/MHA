from django.contrib import admin
from django.utils.html import format_html
from .models import GalleryCategory, GalleryAlbum, GalleryPhoto


class GalleryPhotoInline(admin.TabularInline):
    model = GalleryPhoto
    extra = 3
    fields = ('apercu_image', 'image', 'titre', 'legende', 'ordre')
    readonly_fields = ('apercu_image',)

    def apercu_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 70px; height: 50px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return "Aucune image"
    apercu_image.short_description = "Aperçu"


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'albums_count', 'ordre')
    prepopulated_fields = {'slug': ('nom',)}
    search_fields = ('nom', 'description')
    ordering = ('ordre', 'nom')

    def albums_count(self, obj):
        return obj.albums.count()
    albums_count.short_description = "Nombre d'albums"


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ('apercu_couverture', 'titre', 'categorie', 'date_evenement', 'photos_total', 'est_en_vedette', 'est_publie')
    list_filter = ('categorie', 'est_publie', 'est_en_vedette', 'date_evenement')
    search_fields = ('titre', 'description', 'lieu')
    prepopulated_fields = {'slug': ('titre',)}
    inlines = [GalleryPhotoInline]
    list_editable = ('est_en_vedette', 'est_publie')
    date_hierarchy = 'date_evenement'

    def apercu_couverture(self, obj):
        if obj.couverture:
            return format_html(
                '<img src="{}" style="width: 60px; height: 45px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />',
                obj.couverture.url
            )
        first_p = obj.photos.first()
        if first_p and first_p.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 45px; object-fit: cover; border-radius: 6px; opacity: 0.8;" title="1ère photo de l\'album" />',
                first_p.image.url
            )
        return "Sans image"
    apercu_couverture.short_description = "Couverture"

    def photos_total(self, obj):
        count = obj.photos.count()
        return format_html('<span style="font-weight:bold; color:#FF5E14;">{} photos</span>', count)
    photos_total.short_description = "Total photos"


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ('apercu_image', 'titre', 'album', 'categorie_album', 'ordre', 'date_ajout')
    list_filter = ('album__categorie', 'album', 'date_ajout')
    search_fields = ('titre', 'legende', 'album__titre')
    list_editable = ('ordre',)

    def apercu_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 55px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return "Aucune image"
    apercu_image.short_description = "Aperçu"

    def categorie_album(self, obj):
        return obj.album.categorie.nom if obj.album.categorie else "-"
    categorie_album.short_description = "Catégorie"
