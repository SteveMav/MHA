import os
import django
from decimal import Decimal
from datetime import date
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MHA.settings')
django.setup()

from gallery.models import GalleryCategory, GalleryAlbum, GalleryPhoto
from shop.models import ProductCategory, Product, ProductVariant, ProductImage


def populate():
    print("🏀 Initialisation des données pour la Galerie et la Boutique MHA...")

    # 1. Catégories Galerie
    cat_ceremonie, _ = GalleryCategory.objects.get_or_create(
        nom="Cérémonies & Remises de Brevets",
        defaults={'ordre': 1, 'description': "Moments solennels de remise des attestations et reconnaissance du travail accompli."}
    )
    cat_tournoi, _ = GalleryCategory.objects.get_or_create(
        nom="Matchs & Tournois Kinshasa",
        defaults={'ordre': 2, 'description': "Rencontres compétitives et tournois amicaux inter-académies à Kinshasa."}
    )
    cat_entrainement, _ = GalleryCategory.objects.get_or_create(
        nom="Entraînements & Camps Intensifs",
        defaults={'ordre': 3, 'description': "Séances d'apprentissage technique, travail physique et ateliers tactiques sur le terrain."}
    )
    cat_stages, _ = GalleryCategory.objects.get_or_create(
        nom="Stages de Perfectionnement & Vie du Club",
        defaults={'ordre': 4, 'description': "Stages de vacances, cohésion d'équipe et moments forts de l'académie."}
    )

    # 2. Albums Galerie
    album1, created = GalleryAlbum.objects.get_or_create(
        titre="Cérémonie de Remise de Brevets 2026",
        defaults={
            'categorie': cat_ceremonie,
            'description': "Cérémonie solennelle récompensant la persévérance, la discipline et les progrès techniques des jeunes basketteurs de Magic Hoops Academy.",
            'date_evenement': date(2026, 6, 28),
            'lieu': "Terrain principal, Avenue de la Science n°5, Gombe",
            'est_publie': True,
            'est_en_vedette': True,
        }
    )

    album2, created = GalleryAlbum.objects.get_or_create(
        titre="Tournoi Inter-Académies de Kinshasa",
        defaults={
            'categorie': cat_tournoi,
            'description': "Confrontations de haut niveau pour nos catégories Junior et Elite Hoops face aux meilleures équipes de jeunes de la capitale.",
            'date_evenement': date(2026, 7, 15),
            'lieu': "Complexe Sportif de Kinshasa",
            'est_publie': True,
            'est_en_vedette': False,
        }
    )

    album3, created = GalleryAlbum.objects.get_or_create(
        titre="Camp d'Entraînement Intensif des Vacances",
        defaults={
            'categorie': cat_entrainement,
            'description': "Travail acharné sur les fondamentaux : maniement de balle, tirs sous pression, appuis défensifs et conditionnement athlétique.",
            'date_evenement': date(2026, 8, 10),
            'lieu': "Terrain Magic Hoops, Gombe",
            'est_publie': True,
            'est_en_vedette': True,
        }
    )

    album4, created = GalleryAlbum.objects.get_or_create(
        titre="Sessions Découverte Mini Hoops (U10-U13)",
        defaults={
            'categorie': cat_stages,
            'description': "Les plus jeunes découvrent les règles du jeu, le plaisir de la passe et l'esprit d'équipe dans la joie et la rigueur.",
            'date_evenement': date(2026, 8, 20),
            'lieu': "Terrain principal, Gombe",
            'est_publie': True,
            'est_en_vedette': False,
        }
    )

    # Associer des images disponibles si présentes
    basketball_img_path = 'static/images/basketball.jpeg'
    if os.path.exists(basketball_img_path):
        for album in [album1, album2, album3, album4]:
            if not album.couverture:
                with open(basketball_img_path, 'rb') as f:
                    album.couverture.save(f"cover_{album.slug}.jpg", File(f), save=True)

            if album.photos.count() == 0:
                for i in range(1, 4):
                    with open(basketball_img_path, 'rb') as f:
                        p = GalleryPhoto(
                            album=album,
                            titre=f"Action de jeu #{i} - {album.titre}",
                            legende="Exercice d'intensité et application des consignes de jeu sur le terrain.",
                            ordre=i
                        )
                        p.image.save(f"photo_{album.slug}_{i}.jpg", File(f), save=True)

    print("✅ Albums et photos de la galerie initialisés avec succès.")

    # 3. Catégories Boutique
    scat_tenues, _ = ProductCategory.objects.get_or_create(
        nom="Maillots & Tenues Officielles",
        defaults={'icone_css': 'bi-shield-shaded', 'ordre': 1, 'description': "Maillots de match officiels domicile et extérieur Magic Hoops Academy."}
    )
    scat_tshirts, _ = ProductCategory.objects.get_or_create(
        nom="T-Shirts & Polos d'Entraînement",
        defaults={'icone_css': 'bi-tshirt', 'ordre': 2, 'description': "Hauts d'entraînement légers et respirants pour les séances quotidiennes."}
    )
    scat_sweats, _ = ProductCategory.objects.get_or_create(
        nom="Sweats & Hoodies",
        defaults={'icone_css': 'bi-snow', 'ordre': 3, 'description': "Sweats à capuche confortables pour les échauffements et le quotidien."}
    )
    scat_ballons, _ = ProductCategory.objects.get_or_create(
        nom="Ballons & Équipements",
        defaults={'icone_css': 'bi-dribbble', 'ordre': 4, 'description': "Ballons officiels en cuir composite grip toutes surfaces."}
    )
    scat_accessoires, _ = ProductCategory.objects.get_or_create(
        nom="Casquettes & Accessoires",
        defaults={'icone_css': 'bi-trophy', 'ordre': 5, 'description': "Casquettes brodées, gourdes isothermes, sacs de sport et chaussettes."}
    )

    # 4. Produits Boutique
    produits_data = [
        {
            'nom': "Maillot Officiel MHA Domicile (Orange Passion)",
            'categorie': scat_tenues,
            'prix_usd': Decimal('35.00'),
            'badge': 'officiel',
            'est_en_vedette': True,
            'details_matiere': "100% Polyester respirant Dri-FIT, numéro personnalisé possible, flocage thermo-collé haute durabilité.",
            'description': "Le maillot officiel de match porté par les joueurs de Magic Hoops Academy lors des compétitions et tournois. Coupe athlétique ergonomique garantissant une liberté totale de mouvement.",
            'guide_tailles': "Tailles Juniors : U10 (8-10 ans), U12 (10-12 ans), U14 (12-14 ans).\nTailles Adultes : S, M, L, XL, XXL.",
            'variants': ["U10", "U12", "U14", "Taille S", "Taille M", "Taille L", "Taille XL"],
        },
        {
            'nom': "Maillot Officiel MHA Extérieur (Bleu Nuit)",
            'categorie': scat_tenues,
            'prix_usd': Decimal('35.00'),
            'badge': 'officiel',
            'est_en_vedette': True,
            'details_matiere': "100% Polyester micro-aéré, liserés orange signature MHA, séchage rapide.",
            'description': "La version extérieure prestigieuse en bleu marine nuit avec détails orange vif. Idéal pour les matchs à l'extérieur et les entraînements de gala.",
            'guide_tailles': "Tailles Juniors : U10, U12, U14. Tailles Adultes : S, M, L, XL.",
            'variants': ["U10", "U12", "U14", "Taille S", "Taille M", "Taille L", "Taille XL"],
        },
        {
            'nom': "T-Shirt d'Entraînement MHA Performance",
            'categorie': scat_tshirts,
            'prix_usd': Decimal('20.00'),
            'badge': 'populaire',
            'est_en_vedette': True,
            'details_matiere': "Textile technique ultra-léger 140g, traitement anti-odeur et évacuation optimale de la transpiration.",
            'description': "Le t-shirt essentiel pour chaque entraînement à la Gombe. Confort absolu lors des séances intenses de dribble et de tir.",
            'guide_tailles': "Coupe standard unisexe. Tailles : S, M, L, XL, XXL.",
            'variants': ["Taille S", "Taille M", "Taille L", "Taille XL", "Taille XXL"],
        },
        {
            'nom': "Sweat à Capuche MHA Championship Kinshasa",
            'categorie': scat_sweats,
            'prix_usd': Decimal('45.00'),
            'badge': 'nouveau',
            'est_en_vedette': True,
            'details_matiere': "80% Coton peigné / 20% Polyester épais 320g, intérieur molletonné doux, poche kangourou renforcée.",
            'description': "Sweat à capuche premium avec logo Magic Hoops Academy brodé en relief sur la poitrine et slogan au dos. Parfait pour les matins frais et les déplacements.",
            'guide_tailles': "Coupe décontractée athlétique. Prendre sa taille habituelle.",
            'variants': ["Taille S", "Taille M", "Taille L", "Taille XL"],
        },
        {
            'nom': "Ballon de Basket MHA Composite Grip",
            'categorie': scat_ballons,
            'prix_usd': Decimal('30.00'),
            'badge': 'populaire',
            'est_en_vedette': True,
            'details_matiere': "Cuir synthétique composite avec canaux profonds pour un contrôle de dribble supérieur intérieur/extérieur.",
            'description': "Ballon officiel d'entraînement et de match Magic Hoops Academy. Résistance exceptionnelle sur le bitume et le parquet de Kinshasa.",
            'guide_tailles': "Taille 5 (Enfants U10-U12), Taille 6 (U14 & Féminines), Taille 7 (U16+ et Adultes).",
            'variants': ["Taille 5 (Junior)", "Taille 6 (Intermédiaire)", "Taille 7 (Officiel Hommes)"],
        },
        {
            'nom': "Casquette Snapback MHA Édition Limitée",
            'categorie': scat_accessoires,
            'prix_usd': Decimal('18.00'),
            'badge': 'limite',
            'est_en_vedette': False,
            'details_matiere': "100% Coton sergé, visière plate avec sous-visière contrastée, fermeture snapback arrière réglable.",
            'description': "Style streetwear athlétique aux couleurs de Magic Hoops Academy. Broderie 3D haute précision du logo.",
            'guide_tailles': "Taille unique réglable adaptée à tous les tours de tête.",
            'variants': ["Taille Unique Réglable"],
        },
        {
            'nom': "Gourde Sportive Isotherme MHA (750ml)",
            'categorie': scat_accessoires,
            'prix_usd': Decimal('15.00'),
            'badge': 'nouveau',
            'est_en_vedette': False,
            'details_matiere': "Acier inoxydable double paroi sans BPA, conserve au frais pendant 24h, bouchon sport anti-fuite.",
            'description': "Restez hydraté tout au long de la séance avec la gourde officielle isotherme Magic Hoops Academy.",
            'guide_tailles': "Capacité : 750 ml.",
            'variants': ["Orange Basketball", "Bleu Marine"],
        },
    ]

    for p_data in produits_data:
        variants = p_data.pop('variants')
        product, _ = Product.objects.get_or_create(
            nom=p_data['nom'],
            defaults=p_data
        )

        if not product.image_principale and os.path.exists(basketball_img_path):
            with open(basketball_img_path, 'rb') as f:
                product.image_principale.save(f"prod_{product.slug}.jpg", File(f), save=True)

        for v_name in variants:
            ProductVariant.objects.get_or_create(
                produit=product,
                nom_variante=v_name,
                defaults={'stock': 15, 'prix_supplementaire': Decimal('0.00')}
            )

    print("✅ Catalogue de produits et variantes initialisé avec succès.")
    print("🏀 Initialisation globale terminée avec succès !")


if __name__ == '__main__':
    populate()
