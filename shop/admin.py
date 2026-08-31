from django.contrib import admin
from django.utils.html import format_html
from .models import ProductCategory, Product, ProductImage, ProductVariant, Order, OrderItem


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ('apercu_image', 'image', 'legende', 'ordre')
    readonly_fields = ('apercu_image',)

    def apercu_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 6px;" />',
                obj.image.url
            )
        return "-"
    apercu_image.short_description = "Aperçu"


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 3
    fields = ('nom_variante', 'stock', 'prix_supplementaire')


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'icone_css', 'total_produits', 'ordre')
    prepopulated_fields = {'slug': ('nom',)}
    search_fields = ('nom', 'description')
    ordering = ('ordre', 'nom')

    def total_produits(self, obj):
        return obj.products.count()
    total_produits.short_description = "Nombre d'articles"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'apercu_vignette',
        'nom',
        'categorie',
        'prix_usd',
        'prix_cdf_format',
        'quantite_stock',
        'badge_display',
        'est_actif',
        'est_en_vedette',
    )
    list_filter = ('categorie', 'est_actif', 'est_en_vedette', 'badge')
    search_fields = ('nom', 'description', 'details_matiere')
    prepopulated_fields = {'slug': ('nom',)}
    inlines = [ProductVariantInline, ProductImageInline]
    list_editable = ('prix_usd', 'quantite_stock', 'est_actif', 'est_en_vedette')

    def apercu_vignette(self, obj):
        if obj.image_principale:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px; border: 1px solid #e0e0e0;" />',
                obj.image_principale.url
            )
        return "Sans photo"
    apercu_vignette.short_description = "Photo"

    def prix_cdf_format(self, obj):
        return obj.formatted_cdf
    prix_cdf_format.short_description = "Prix (FC)"

    def badge_display(self, obj):
        if obj.badge:
            colors = {
                'nouveau': '#28a745',
                'populaire': '#ffc107',
                'officiel': '#FF5E14',
                'limite': '#6f42c1',
                'promo': '#dc3545',
            }
            color = colors.get(obj.badge, '#6c757d')
            text_color = '#000' if obj.badge == 'populaire' else '#fff'
            return format_html(
                '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
                color, text_color, obj.get_badge_display()
            )
        return "-"
    badge_display.short_description = "Badge"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('produit', 'variante_label', 'prix_unitaire_usd', 'quantite', 'total_ligne')
    readonly_fields = ('produit', 'variante_label', 'prix_unitaire_usd', 'quantite', 'total_ligne')

    def total_ligne(self, obj):
        return f"{obj.total_ligne_usd} $ (~{obj.total_ligne_cdf:,} FC)"
    total_ligne.short_description = "Total ligne"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'numero_commande',
        'nom_complet',
        'client_telephone',
        'total_usd_display',
        'mode_paiement_court',
        'badge_statut_paiement',
        'badge_statut_commande',
        'date_creation',
    )
    list_filter = ('statut_paiement', 'statut_commande', 'mode_paiement', 'mode_retrait', 'date_creation')
    search_fields = ('numero_commande', 'client_nom', 'client_prenom', 'client_telephone', 'client_email', 'reference_paiement')
    readonly_fields = ('numero_commande', 'date_creation', 'date_mise_a_jour', 'total_usd', 'formatted_cdf_display')
    inlines = [OrderItemInline]
    date_hierarchy = 'date_creation'
    actions = ['marquer_comme_payee', 'marquer_comme_prete', 'marquer_comme_livree']

    def formatted_cdf_display(self, obj):
        return obj.formatted_cdf
    formatted_cdf_display.short_description = "Total en Francs Congolais"

    def total_usd_display(self, obj):
        return format_html('<strong style="color: #FF5E14; font-size: 14px;">{} $</strong>', obj.total_usd)
    total_usd_display.short_description = "Total ($)"

    def mode_paiement_court(self, obj):
        return obj.get_mode_paiement_display().split(' - ')[0]
    mode_paiement_court.short_description = "Paiement"

    def badge_statut_paiement(self, obj):
        colors = {
            'en_attente': '#ffc107',
            'valide': '#28a745',
            'rembourse': '#dc3545',
        }
        color = colors.get(obj.statut_paiement, '#6c757d')
        text_color = '#000' if obj.statut_paiement == 'en_attente' else '#fff'
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color, text_color, obj.get_statut_paiement_display()
        )
    badge_statut_paiement.short_description = "Paiement"

    def badge_statut_commande(self, obj):
        colors = {
            'nouvelle': '#17a2b8',
            'en_preparation': '#007bff',
            'prete': '#fd7e14',
            'livree': '#28a745',
            'annulee': '#6c757d',
        }
        color = colors.get(obj.statut_commande, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color, obj.get_statut_commande_display()
        )
    badge_statut_commande.short_description = "Statut Commande"

    @admin.action(description="Valider le paiement (Marquer comme payé)")
    def marquer_comme_payee(self, request, queryset):
        queryset.update(statut_paiement='valide')
        self.message_user(request, f"{queryset.count()} commande(s) marquée(s) comme payée(s).")

    @admin.action(description="Marquer comme prête pour retrait")
    def marquer_comme_prete(self, request, queryset):
        queryset.update(statut_commande='prete')
        self.message_user(request, f"{queryset.count()} commande(s) marquée(s) comme prête(s) pour retrait.")

    @admin.action(description="Marquer comme livrée / remise au client")
    def marquer_comme_livree(self, request, queryset):
        queryset.update(statut_commande='livree')
        self.message_user(request, f"{queryset.count()} commande(s) marquée(s) comme livrée(s).")
