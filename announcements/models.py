from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Annonce(models.Model):
    titre = models.CharField(max_length=200)
    message = models.TextField()
    date_publication = models.DateTimeField(auto_now_add=True)
    cible = models.CharField(
        max_length=50,
        choices=[('tous', 'Tous les membres'), ('categorie', 'Par catégorie'), ('individuel', 'Membres sélectionnés')],
        default='tous'
    )
    membres_cibles = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.titre
        
