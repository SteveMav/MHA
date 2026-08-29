from django.contrib import admin
from .models import Annonce


@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_annonce', 'date_publication', 'date_debut', 'cible')
    list_filter = ('type_annonce', 'cible', 'date_publication')
    search_fields = ('titre', 'message', 'resume_seo', 'lieu')
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ('date_publication',)
