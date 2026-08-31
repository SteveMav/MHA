import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


TAUX_CONVERSION_CDF = Decimal('2850.00')


class ProductCategory(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description du rayon")
    icone_css = models.CharField(max_length=50, default="bi-tag", verbose_name="Icône Bootstrap (ex: bi-tshirt, bi-bag)")
    ordre = models.IntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Rayon / Catégorie de produit"
        verbose_name_plural = "Rayons / Catégories de produits"
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom) or 'rayon'
        super().save(*args, **kwargs)


class Product(models.Model):
    BADGE_CHOICES = [
        ('', 'Aucun'),
        ('nouveau', 'Nouveau'),
        ('populaire', 'Bestseller / Populaire'),
        ('officiel', 'Officiel MHA'),
        ('limite', 'Édition Limitée'),
        ('promo', 'Promotion'),
    ]

    nom = models.CharField(max_length=200, verbose_name="Nom de l'article")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    categorie = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Catégorie / Rayon"
    )
    description = models.TextField(verbose_name="Description complète")
    details_matiere = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Matière / Caractéristiques",
        help_text="Ex: 100% Polyester respirant Dri-FIT, Impression sérigraphie haute résistance"
    )
    prix_usd = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix en USD ($)")
    image_principale = models.ImageField(upload_to='shop/products/', verbose_name="Image principale")
    en_stock = models.BooleanField(default=True, verbose_name="Disponible en stock")
    quantite_stock = models.IntegerField(default=20, verbose_name="Quantité globale en stock")
    badge = models.CharField(max_length=20, choices=BADGE_CHOICES, blank=True, verbose_name="Badge visuel")
    est_actif = models.BooleanField(default=True, verbose_name="Visible dans la boutique")
    est_en_vedette = models.BooleanField(default=False, verbose_name="Mettre en avant (Accueil / Top boutique)")
    guide_tailles = models.TextField(
        blank=True,
        verbose_name="Guide des tailles / Informations complémentaires",
        help_text="Tailles juniors : U10, U12, U14. Tailles adultes : S, M, L, XL, XXL."
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Article / Produit"
        verbose_name_plural = "Articles / Produits"
        ordering = ['-est_en_vedette', '-date_creation']

    def __str__(self):
        return f"{self.nom} ({self.prix_usd} $)"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.nom) or 'produit'
        slug = base_slug
        counter = 2
        while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})

    @property
    def prix_cdf(self):
        """Conversion indicative en Francs Congolais (CDF)"""
        return int(self.prix_usd * TAUX_CONVERSION_CDF)

    @property
    def formatted_cdf(self):
        return f"{self.prix_cdf: ,}".replace(',', ' ') + " FC"


class ProductImage(models.Model):
    produit = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Produit"
    )
    image = models.ImageField(upload_to='shop/gallery/', verbose_name="Image additionnelle")
    legende = models.CharField(max_length=150, blank=True, verbose_name="Légende / Vue")
    ordre = models.IntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Image additionnelle"
        verbose_name_plural = "Images additionnelles"
        ordering = ['ordre', 'id']

    def __str__(self):
        return f"Image de {self.produit.nom} ({self.ordre})"


class ProductVariant(models.Model):
    produit = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name="Produit"
    )
    nom_variante = models.CharField(
        max_length=80,
        verbose_name="Déclinaison / Taille",
        help_text="Ex: Taille S, Taille M, Taille L, U12, Ballon T7, etc."
    )
    stock = models.IntegerField(default=10, verbose_name="Stock spécifique")
    prix_supplementaire = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        verbose_name="Supplément de prix ($)"
    )

    class Meta:
        verbose_name = "Variante / Taille"
        verbose_name_plural = "Variantes / Tailles"
        ordering = ['nom_variante']

    def __str__(self):
        if self.prix_supplementaire > 0:
            return f"{self.produit.nom} - {self.nom_variante} (+{self.prix_supplementaire} $)"
        return f"{self.produit.nom} - {self.nom_variante}"


class Order(models.Model):
    STATUT_PAIEMENT = [
        ('en_attente', 'En attente de paiement'),
        ('valide', 'Paiement Validé / Payé'),
        ('rembourse', 'Remboursé'),
    ]

    STATUT_COMMANDE = [
        ('nouvelle', 'Nouvelle commande'),
        ('en_preparation', 'En préparation'),
        ('prete', 'Prête pour retrait'),
        ('livree', 'Livrée / Remise au client'),
        ('annulee', 'Annulée'),
    ]

    MODE_RETRAIT = [
        ('retrait_terrain', 'Retrait gratuit au Terrain MHA (Gombe, Av. de la Science n°5)'),
        ('livraison_kinshasa', 'Livraison à domicile (Kinshasa)'),
    ]

    MODE_PAIEMENT = [
        ('mpesa', 'M-Pesa (Vodacom) - +243 810 000 000'),
        ('orange_money', 'Orange Money - +243 890 000 000'),
        ('airtel_money', 'Airtel Money - +243 990 000 000'),
        ('especes_club', 'Paiement en espèces au terrain / secrétariat'),
        ('carte', 'Carte Bancaire / Paiement en ligne'),
    ]

    numero_commande = models.CharField(max_length=50, unique=True, verbose_name="Numéro de commande")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='commandes_shop')
    
    # Informations Client
    client_nom = models.CharField(max_length=100, verbose_name="Nom de famille")
    client_prenom = models.CharField(max_length=100, verbose_name="Prénom")
    client_telephone = models.CharField(
        max_length=30,
        verbose_name="Téléphone / WhatsApp",
        help_text="Numéro utilisé pour la confirmation et le retrait de commande."
    )
    client_email = models.EmailField(blank=True, verbose_name="Adresse Email")
    
    # Livraison & Retrait
    mode_retrait = models.CharField(
        max_length=30,
        choices=MODE_RETRAIT,
        default='retrait_terrain',
        verbose_name="Mode de réception"
    )
    adresse_livraison = models.CharField(max_length=255, blank=True, verbose_name="Adresse exacte (si livraison)")
    commune_kinshasa = models.CharField(
        max_length=100,
        blank=True,
        default="Gombe",
        verbose_name="Commune / Quartier"
    )
    
    # Paiement
    mode_paiement = models.CharField(
        max_length=30,
        choices=MODE_PAIEMENT,
        default='mpesa',
        verbose_name="Moyen de paiement"
    )
    reference_paiement = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID / Référence de transaction Mobile Money",
        help_text="Ex: ID du SMS de confirmation M-Pesa / Orange Money"
    )
    statut_paiement = models.CharField(
        max_length=20,
        choices=STATUT_PAIEMENT,
        default='en_attente',
        verbose_name="Statut du paiement"
    )
    statut_commande = models.CharField(
        max_length=20,
        choices=STATUT_COMMANDE,
        default='nouvelle',
        verbose_name="Statut du traitement"
    )

    # Totaux
    total_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total USD ($)")
    notes_client = models.TextField(blank=True, verbose_name="Notes ou instructions particulières")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de commande")
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Commande de la boutique"
        verbose_name_plural = "Commandes de la boutique"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Commande {self.numero_commande} - {self.client_nom} {self.client_prenom} ({self.total_usd} $)"

    def save(self, *args, **kwargs):
        if not self.numero_commande:
            short_id = uuid.uuid4().hex[:6].upper()
            self.numero_commande = f"MHA-{short_id}"
        super().save(*args, **kwargs)

    @property
    def nom_complet(self):
        return f"{self.client_prenom} {self.client_nom}".strip()

    @property
    def total_cdf(self):
        return int(self.total_usd * TAUX_CONVERSION_CDF)

    @property
    def formatted_cdf(self):
        return f"{self.total_cdf: ,}".replace(',', ' ') + " FC"


class OrderItem(models.Model):
    commande = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Commande"
    )
    produit = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Article"
    )
    variante_label = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Taille / Option choisie"
    )
    prix_unitaire_usd = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire ($)")
    quantite = models.PositiveIntegerField(default=1, verbose_name="Quantité")

    class Meta:
        verbose_name = "Article commandé"
        verbose_name_plural = "Articles commandés"

    def __str__(self):
        nom_prod = self.produit.nom if self.produit else "Article supprimé"
        return f"{self.quantite}x {nom_prod} ({self.variante_label})"

    @property
    def total_ligne_usd(self):
        return self.prix_unitaire_usd * self.quantite

    @property
    def total_ligne_cdf(self):
        return int(self.total_ligne_usd * TAUX_CONVERSION_CDF)
