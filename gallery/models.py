from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class GalleryCategory(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    ordre = models.IntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Catégorie d'événement"
        verbose_name_plural = "Catégories d'événements"
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom) or 'categorie'
        super().save(*args, **kwargs)


class GalleryAlbum(models.Model):
    titre = models.CharField(max_length=200, verbose_name="Titre de l'événement / album")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    categorie = models.ForeignKey(
        GalleryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='albums',
        verbose_name="Catégorie"
    )
    description = models.TextField(blank=True, verbose_name="Description de l'événement")
    date_evenement = models.DateField(null=True, blank=True, verbose_name="Date de l'événement")
    lieu = models.CharField(
        max_length=255,
        blank=True,
        default="Terrain principal, Gombe, Kinshasa",
        verbose_name="Lieu"
    )
    couverture = models.ImageField(
        upload_to='gallery/covers/',
        blank=True,
        null=True,
        verbose_name="Image de couverture"
    )
    est_publie = models.BooleanField(default=True, verbose_name="Publié en ligne")
    est_en_vedette = models.BooleanField(default=False, verbose_name="Mettre en vedette (Accueil & Tête de liste)")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Album / Événement"
        verbose_name_plural = "Albums / Événements"
        ordering = ['-est_en_vedette', '-date_evenement', '-date_creation']

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.titre) or 'album'
        slug = base_slug
        counter = 2
        while GalleryAlbum.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def get_absolute_url(self):
        return reverse('gallery:album_detail', kwargs={'slug': self.slug})

    @property
    def photos_count(self):
        return self.photos.count()

    @property
    def first_photo(self):
        return self.photos.first()


class GalleryPhoto(models.Model):
    album = models.ForeignKey(
        GalleryAlbum,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="Album"
    )
    image = models.ImageField(upload_to='gallery/photos/', verbose_name="Fichier image")
    titre = models.CharField(max_length=200, blank=True, verbose_name="Titre / Légende courte")
    legende = models.TextField(blank=True, verbose_name="Description détaillée")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Photo d'événement"
        verbose_name_plural = "Photos d'événements"
        ordering = ['ordre', 'date_ajout']

    def __str__(self):
        return self.titre or f"Photo #{self.pk} - {self.album.titre}"
