from django.db import models

class AcademyInfo(models.Model):
    nom = models.CharField(max_length=200, default="Magic Hoops Academy Kinshasa (MHA)")
    slogan = models.CharField(max_length=255, default="Là où le talent rencontre la discipline")
    fondateur = models.CharField(max_length=200, default="Bruno Lobaya Nkoy (alias Magic)")
    description = models.TextField(help_text="Présentation générale de l'académie")
    mission = models.TextField()
    vision = models.TextField()
    objectifs = models.TextField()
    valeurs = models.TextField()
    infrastructures = models.TextField()
    localisation = models.CharField(max_length=255)
    philosophie = models.TextField()
    date_creation = models.DateField(null=True, blank=True)
    logo = models.ImageField(upload_to='academy/', null=True, blank=True)
    image_principale = models.ImageField(upload_to='academy/', null=True, blank=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Informations de l'académie"
        verbose_name_plural = "Informations de l'académie"





class Schedule(models.Model):
    DAYS_OF_WEEK = (
        ('Lundi', 'Lundi'),
        ('Mardi', 'Mardi'),
        ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'),
        ('Vendredi', 'Vendredi'),
        ('Samedi', 'Samedi'),
        ('Dimanche', 'Dimanche'),
    )

    day = models.CharField(max_length=20, choices=DAYS_OF_WEEK, verbose_name="Jour")
    start_time = models.TimeField(verbose_name="Heure de début")
    end_time = models.TimeField(verbose_name="Heure de fin")
    description = models.CharField(max_length=200, verbose_name="Description", default="Entraînement régulier")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Horaire"
        verbose_name_plural = "Horaires"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.day} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
