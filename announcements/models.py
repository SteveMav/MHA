from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Annonce(models.Model):
    TYPE_ACTUALITE = 'actualite'
    TYPE_SESSION = 'session'
    TYPE_EVENEMENT = 'evenement'
    TYPE_PARCOURS = 'parcours'

    TYPES_ANNONCE = [
        (TYPE_ACTUALITE, 'Actualité'),
        (TYPE_SESSION, 'Session de basket'),
        (TYPE_EVENEMENT, 'Événement'),
        (TYPE_PARCOURS, 'Parcours / programme'),
    ]

    titre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True)
    message = models.TextField()
    resume_seo = models.CharField(
        max_length=180,
        blank=True,
        help_text="Résumé court utilisé par Google, ChatGPT et les partages sociaux."
    )
    type_annonce = models.CharField(max_length=20, choices=TYPES_ANNONCE, default=TYPE_ACTUALITE)
    date_debut = models.DateTimeField(null=True, blank=True, help_text="À remplir pour une session ou un événement.")
    date_fin = models.DateTimeField(null=True, blank=True)
    lieu = models.CharField(max_length=255, blank=True, default="Terrain principal, Gombe, Kinshasa")
    inscription_url = models.URLField(blank=True, help_text="Lien d'inscription ou de contact si disponible.")
    date_publication = models.DateTimeField(auto_now_add=True)
    cible = models.CharField(
        max_length=50,
        choices=[('tous', 'Tous les membres'), ('categorie', 'Par catégorie'), ('individuel', 'Membres sélectionnés')],
        default='tous'
    )
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    membres_cibles = models.ManyToManyField(User, blank=True, related_name='annonces_ciblees')

    class Meta:
        ordering = ['-date_publication']

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.titre) or 'annonce'
        slug = base_slug
        counter = 2

        while Annonce.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1

        return slug

    def get_absolute_url(self):
        if self.slug:
            return reverse('announcements:announcement_detail', kwargs={'slug': self.slug})
        return reverse('announcements:announcement_detail_legacy', kwargs={'pk': self.pk})

    @property
    def is_event_like(self):
        return self.type_annonce in {self.TYPE_SESSION, self.TYPE_EVENEMENT}
