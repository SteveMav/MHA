from django.db import models

class AcademyInfo(models.Model):
    nom = models.CharField(max_length=200, default="Magic Hoops Academy Kinshasa (MHA)")
    slogan = models.CharField(max_length=255, default="Là où le talent rencontre la discipline")
    fondateur = models.CharField(max_length=200, default="Bruno Lobaya Nkoy (alias Magic)")
    description = models.TextField(help_text="Présentation générale de l'académie", blank=True, default="")
    mission = models.TextField(blank=True, default="")
    vision = models.TextField(blank=True, default="")
    objectifs = models.TextField(blank=True, default="")
    valeurs = models.TextField(blank=True, default="")
    infrastructures = models.TextField(blank=True, default="")
    localisation = models.CharField(max_length=255, blank=True, default="Avenue de la Science numéro 5, Gombe, Kinshasa")
    philosophie = models.TextField(blank=True, default="")
    date_creation = models.DateField(null=True, blank=True)
    logo = models.ImageField(upload_to='academy/', null=True, blank=True)
    image_principale = models.ImageField(upload_to='academy/', null=True, blank=True)

    # Nouveaux champs éditables pour la page d'accueil & l'administration
    hero_title = models.CharField(max_length=255, default="Former les jeunes joueurs, forger les champions.", verbose_name="Titre Hero")
    hero_subtitle = models.TextField(default="L'académie de référence à Kinshasa (Gombe) pour développer les fondamentaux techniques, la discipline sportive et l'esprit d'équipe des U10 à U18+.", verbose_name="Sous-titre Hero")
    slogan_badge = models.CharField(max_length=200, default="Formons les champions de demain !", verbose_name="Badge Slogan")
    telephone = models.CharField(max_length=50, default="+243 900 824 429", verbose_name="Téléphone de contact")
    email = models.EmailField(default="info@magichoops.cd", verbose_name="Email de contact")
    adresse_terrain = models.CharField(max_length=255, default="Avenue de la Science numéro 5, Gombe, Kinshasa", verbose_name="Adresse du terrain")
    methode_titre = models.CharField(max_length=255, default="Former le joueur complet, pas seulement le scoreur.", verbose_name="Titre Méthode")
    methode_description = models.TextField(default="Une pédagogie sportive complète qui allie rigueur technique, motricité athlétique, intelligence tactique et mental d'acier.", verbose_name="Description Méthode")
    methode_cadre_texte = models.TextField(default="Au-delà du basketball, nous inculquons la ponctualité, le respect, l'effort collectif et le dépassement de soi.", verbose_name="Texte Le Cadre Fait la Différence")
    coach_magic_titre = models.CharField(max_length=255, default="Bruno Lobaya Nkoy, alias Coach Magic.", verbose_name="Titre Coach Magic")
    coach_magic_quote = models.TextField(default="« Le talent ouvre la voie, mais seule la discipline forge les champions. »", verbose_name="Citation Coach Magic")
    coach_magic_bio = models.TextField(default="À Magic Hoops Academy, l'exigence sur le parquet s'accompagne d'une transmission sans compromis du respect et du dépassement de soi.", verbose_name="Bio Coach Magic")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Informations de l'académie"
        verbose_name_plural = "Informations de l'académie"


class MethodPillar(models.Model):
    titre = models.CharField(max_length=150, verbose_name="Titre du pilier")
    description = models.TextField(verbose_name="Description")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    icone = models.CharField(max_length=50, default="bi-dribbble", verbose_name="Classe icône Bootstrap")
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")

    class Meta:
        verbose_name = "Pilier de la méthode"
        verbose_name_plural = "Piliers de la méthode"
        ordering = ['ordre', 'id']

    def __str__(self):
        return self.titre





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
