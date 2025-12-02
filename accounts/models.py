from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_naissance = models.DateField(null=True, blank=True)
    telephone = models.CharField(max_length=20)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='media/profil/', null=True, blank=True)
    ecole_frequente = models.CharField(max_length=255, null=True, blank=True)
    niveau = models.CharField(max_length=255, null=True, blank=True)
    taille = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    poids = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    poste_prefer = models.CharField(max_length=255, null=True, blank=True)
    contact_parent = models.CharField(max_length=20, null=True, blank=True)
    
    # TODO: Add other fields from info_hoops.pdf when available

    def __str__(self):
        return self.user.username


class Abonnement(models.Model):
    membre = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abonnements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(
        max_length=20,
        choices=[('en_attente', 'En attente'), ('payé', 'Payé'), ('expiré', 'Expiré')],
        default='en_attente'
    )
    moyen_paiement = models.CharField(
        max_length=20,
        choices=[('mpesa', 'M-Pesa'), ('orange', 'Orange Money'), ('airtel', 'Airtel Money')],
        null=True, blank=True
    )
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Abonnement {self.membre.username} ({self.date_debut})"
