from .models import Schedule, AcademyInfo, MethodPillar
from announcements.models import Annonce
from gallery.models import GalleryAlbum, GalleryPhoto
from shop.models import Product
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .seo import (
    ACADEMY_ADDRESS,
    ACADEMY_DESCRIPTION,
    ACADEMY_EMAIL,
    ACADEMY_NAME,
    absolute_static_url,
    absolute_url,
    breadcrumb_node,
    organization_node,
    schema_json,
)


PROGRAMS = [
    {
        "slug": "mini-hoops",
        "name": "Mini Hoops",
        "age": "U10 à U13",
        "short": "Découvrir le basketball dans un cadre joyeux, discipliné et sécurisé.",
        "description": "Initiation au basketball, coordination, bases techniques et plaisir du jeu.",
        "promise": "Installer les fondamentaux sans brûler les étapes.",
        "focus": ["Coordination", "Dribble et tir", "Confiance", "Règles du jeu"],
        "outcomes": [
            "Comprendre les règles essentielles du basketball.",
            "Développer l'équilibre, la coordination et l'écoute.",
            "Prendre plaisir à s'entraîner en groupe.",
        ],
        "cta": "Inscrire un jeune U10-U13",
    },
    {
        "slug": "junior-hoops",
        "name": "Junior Hoops",
        "age": "U14 à U17",
        "short": "Passer des bases au vrai jeu collectif avec exigence et régularité.",
        "description": "Perfectionnement technique, tactique de base, compétition et discipline d'équipe.",
        "promise": "Transformer l'envie en progression mesurable.",
        "focus": ["Technique individuelle", "Lecture du jeu", "Défense", "Compétition"],
        "outcomes": [
            "Progresser techniquement sur les gestes clés.",
            "Comprendre les placements et les responsabilités collectives.",
            "Construire une discipline d'entraînement régulière.",
        ],
        "cta": "Rejoindre Junior Hoops",
    },
    {
        "slug": "elite-hoops",
        "name": "Elite Hoops",
        "age": "U18 et plus",
        "short": "Travailler avec intensité pour préparer le basket compétitif.",
        "description": "Haute performance, préparation physique et accompagnement vers le basket compétitif.",
        "promise": "Préparer des profils capables de tenir l'intensité.",
        "focus": ["Haute intensité", "Préparation physique", "Projet sportif", "Leadership"],
        "outcomes": [
            "S'entraîner avec une exigence proche de la compétition.",
            "Améliorer la condition physique et la prise de décision.",
            "Structurer un projet sportif personnel.",
        ],
        "cta": "Candidater pour Elite Hoops",
    },
]

PROGRAMS_BY_SLUG = {program["slug"]: program for program in PROGRAMS}

METHOD_PILLARS = [
    {
        "title": "Technique",
        "text": "Dribble, tir, passes, appuis, défense et finition. Les gestes sont répétés jusqu'à devenir fiables.",
    },
    {
        "title": "Physique",
        "text": "Coordination, vitesse, mobilité et endurance selon l'âge. On construit un corps prêt pour le jeu.",
    },
    {
        "title": "Lecture du jeu",
        "text": "Comprendre l'espace, les décisions, le timing et le rôle de chaque joueur dans le collectif.",
    },
    {
        "title": "Mentalité",
        "text": "Discipline, respect, ponctualité, résilience et ambition. Le cadre compte autant que le talent.",
    },
]

STAFF_MEMBERS = [
    {
        "name": "Bruno Lobaya Nkoy",
        "role": "Fondateur, alias Magic",
        "bio": "Porte le projet Magic Hoops Academy avec une vision simple: former des basketteurs solides et des jeunes capables de grandir dans un cadre exigeant.",
    },
    {
        "name": "Encadrement MHA",
        "role": "Coachs et accompagnateurs",
        "bio": "Une équipe orientée terrain, progression et discipline quotidienne. Les profils détaillés pourront être ajoutés au fur et à mesure.",
    },
]

REGISTRATION_STEPS = [
    "Choisir le programme adapté à l'âge et au niveau.",
    "Consulter les prochaines sessions dans les actualités.",
    "Créer un compte membre ou contacter l'académie.",
    "Se présenter au terrain 15 minutes avant l'entraînement.",
]

FAQS = [
    {
        "question": "Comment inscrire son enfant (fille ou garçon) à l'académie de basket à Kinshasa ?",
        "answer": "L'inscription à Magic Hoops Academy se fait facilement en ligne via notre formulaire d'inscription ou directement sur notre terrain à la Gombe. Les parents choisissent la tranche d'âge de leur enfant (Mini, Junior ou Elite) pour préparer sa première séance d'évaluation.",
    },
    {
        "question": "L'académie accueille-t-elle aussi bien les filles que les garçons ?",
        "answer": "Absolument. Magic Hoops Academy promeut activement le basketball féminin et masculin en RDC. Nos programmes sont parfaitement adaptés aux filles et garçons de 8 à 18+ ans, avec un encadrement bienveillant, sécurisé et exigeant.",
    },
    {
        "question": "À partir de quel âge les enfants peuvent-ils débuter le basketball ?",
        "answer": "Les enfants peuvent débuter dès l'âge de 8 ans dans le programme Mini Hoops (U10 à U13). Les séances sont axées sur la motricité, la coordination, les règles fondamentales et le plaisir de jouer en équipe.",
    },
    {
        "question": "Où se trouve le terrain d'entraînement de basketball à Kinshasa ?",
        "answer": "Magic Hoops Academy s'entraîne au cœur de Kinshasa, dans la commune de la Gombe, à l'adresse Avenue de la Science numéro 5. Le terrain est sécurisé et facilement accessible pour les familles.",
    },
    {
        "question": "Faut-il déjà avoir un bon niveau pour rejoindre Magic Hoops Academy ?",
        "answer": "Non, tous les niveaux sont les bienvenus. Nos coachs évaluent chaque jeune pour l'intégrer dans le groupe adéquat : initiation pour les débutants complets, perfectionnement pour les joueurs réguliers, et filière performance pour l'élite compétitive.",
    },
    {
        "question": "Quels sont les jours et horaires des entraînements de basket ?",
        "answer": "Les séances régulières se déroulent chaque semaine, notamment le mercredi après-midi et le samedi matin selon les catégories d'âge. Le calendrier détaillé des sessions est mis à jour dans la rubrique Horaires et Actualités.",
    },
]


def get_featured_session():
    future_session = (
        Annonce.objects
        .filter(type_annonce__in=[Annonce.TYPE_SESSION, Annonce.TYPE_EVENEMENT], date_debut__gte=timezone.now())
        .order_by('date_debut')
        .first()
    )
    if future_session:
        return future_session

    return (
        Annonce.objects
        .filter(type_annonce__in=[Annonce.TYPE_SESSION, Annonce.TYPE_EVENEMENT])
        .order_by('-date_publication')
        .first()
    )


def index(request):
    schedules = Schedule.objects.all()
    # Keep the homepage FAQ and its structured data aligned with the live timetable.
    home_faqs = [dict(item) for item in FAQS]
    home_faqs[-1]['answer'] = (
        "Consultez les créneaux dans la rubrique Horaires et accès de cette page. "
        "Contactez l'équipe pour confirmer le groupe adapté à votre enfant."
    )
    recent_announcements = Annonce.objects.all()[:4]
    latest_announcement = Annonce.objects.order_by('-date_publication').first()
    featured_session = get_featured_session()
    featured_albums = GalleryAlbum.objects.filter(est_publie=True).select_related('categorie').prefetch_related('photos')[:3]
    recent_photos = GalleryPhoto.objects.filter(album__est_publie=True).select_related('album').order_by('-date_ajout')[:6]
    total_photos_count = GalleryPhoto.objects.filter(album__est_publie=True).count()
    featured_products = Product.objects.filter(est_actif=True, est_en_vedette=True).select_related('categorie')[:4]
    if not featured_products.exists():
        featured_products = Product.objects.filter(est_actif=True).select_related('categorie')[:4]

    # Données dynamiques AcademyInfo & MethodPillar avec repli gracieux
    academy_info = AcademyInfo.objects.first()
    db_pillars = list(MethodPillar.objects.filter(est_actif=True).order_by('ordre', 'id'))
    if db_pillars:
        active_method_pillars = [
            {
                "title": p.titre,
                "text": p.description,
                "icone": p.icone,
            }
            for p in db_pillars
        ]
    else:
        active_method_pillars = METHOD_PILLARS

    canonical_url = absolute_url(request, '/')
    hero_image_url = absolute_static_url(request, 'images/basketball.jpeg')
    logo_url = absolute_static_url(request, 'images/mha_logo.jpeg')

    course_nodes = [
        {
            "@type": "Course",
            "name": program["name"],
            "description": f'{program["description"]} Programme {program["age"]} à Kinshasa.',
            "provider": {
                "@id": f"{canonical_url}#organization",
            },
        }
        for program in PROGRAMS
    ]

    faq_node = {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"],
                },
            }
            for item in home_faqs
        ],
    }

    website_node = {
        "@type": "WebSite",
        "@id": f"{canonical_url}#website",
        "name": ACADEMY_NAME,
        "url": canonical_url,
        "inLanguage": "fr-CD",
        "publisher": {
            "@id": f"{canonical_url}#organization",
        },
    }

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            organization_node(request),
            website_node,
            faq_node,
            {
                "@type": "ItemList",
                "name": "Programmes de formation basket Magic Hoops Academy",
                "itemListElement": [
                    {"@type": "ListItem", "position": index + 1, "item": node}
                    for index, node in enumerate(course_nodes)
                ],
            },
        ],
    }

    return render(request, 'main/index.html', {
        'schedules': schedules,
        'recent_announcements': recent_announcements,
        'latest_announcement': latest_announcement,
        'featured_session': featured_session,
        'featured_albums': featured_albums,
        'recent_photos': recent_photos,
        'total_photos_count': total_photos_count,
        'featured_products': featured_products,
        'programs': PROGRAMS,
        'method_pillars': active_method_pillars,
        'academy_info': academy_info,
        'home_custom_title': (
            academy_info.hero_title if academy_info and academy_info.hero_title !=
            AcademyInfo._meta.get_field('hero_title').get_default() else ''
        ),
        'home_custom_subtitle': (
            academy_info.hero_subtitle if academy_info and academy_info.hero_subtitle !=
            AcademyInfo._meta.get_field('hero_subtitle').get_default() else ''
        ),
        'staff_members': STAFF_MEMBERS,
        'faqs': home_faqs,
        'seo_title': "Magic Hoops Academy | Académie de Basket à Kinshasa (RDC) • Filles & Garçons",
        'seo_description': (
            "Académie de basketball de référence à Kinshasa (Gombe) pour enfants, filles et garçons "
            "de 8 à 18+ ans. Entraînements techniques, discipline, stages et formation humaine en RDC."
        ),
        'canonical_url': canonical_url,
        'og_type': 'website',
        'og_image': hero_image_url,
        'site_logo_url': logo_url,
        'organization_schema': schema_json(schema),
    })


def programmes(request):
    canonical_url = absolute_url(request, '/programmes/')
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            organization_node(request),
            breadcrumb_node(request, [
                ('Accueil', '/'),
                ('Programmes', '/programmes/'),
            ]),
            {
                "@type": "ItemList",
                "name": "Programmes Magic Hoops Academy",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": index + 1,
                        "url": absolute_url(request, f"/programmes/{program['slug']}/"),
                        "name": program["name"],
                    }
                    for index, program in enumerate(PROGRAMS)
                ],
            },
        ],
    }
    return render(request, 'main/programmes.html', {
        'programs': PROGRAMS,
        'seo_title': "Programmes basket à Kinshasa | Mini, Junior et Elite Hoops",
        'seo_description': "Découvrez les programmes de formation basketball Magic Hoops Academy à Kinshasa pour les jeunes U10 à U18+.",
        'canonical_url': canonical_url,
        'og_type': 'website',
        'og_image': absolute_static_url(request, 'images/basketball.jpeg'),
        'page_schema': schema_json(schema),
    })


def programme_detail(request, slug):
    program = PROGRAMS_BY_SLUG.get(slug)
    if program is None:
        raise Http404("Programme introuvable.")
    canonical_url = absolute_url(request, f"/programmes/{program['slug']}/")
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            organization_node(request),
            breadcrumb_node(request, [
                ('Accueil', '/'),
                ('Programmes', '/programmes/'),
                (program['name'], f"/programmes/{program['slug']}/"),
            ]),
            {
                "@type": "Course",
                "name": program["name"],
                "description": f"{program['description']} Programme {program['age']} à Kinshasa.",
                "provider": {"@id": f"{absolute_url(request, '/')}#organization"},
            },
        ],
    }
    return render(request, 'main/programme_detail.html', {
        'program': program,
        'programs': PROGRAMS,
        'seo_title': f"{program['name']} à Kinshasa | Magic Hoops Academy",
        'seo_description': f"{program['name']} est le programme Magic Hoops Academy pour {program['age']}: {program['short']}",
        'canonical_url': canonical_url,
        'og_type': 'article',
        'og_image': absolute_static_url(request, 'images/basketball.jpeg'),
        'page_schema': schema_json(schema),
    })


def methode(request):
    return redirect('/#methode')


def staff(request):
    return redirect('/#coach')


def inscription(request):
    canonical_url = absolute_url(request, '/inscription/')
    featured_session = get_featured_session()
    return render(request, 'main/inscription.html', {
        'programs': PROGRAMS,
        'registration_steps': REGISTRATION_STEPS,
        'featured_session': featured_session,
        'seo_title': "Inscription basket à Kinshasa | Rejoindre Magic Hoops Academy",
        'seo_description': "Rejoignez Magic Hoops Academy à Kinshasa: choisissez votre programme, consultez les sessions et créez un compte membre.",
        'canonical_url': canonical_url,
        'og_type': 'website',
        'og_image': absolute_static_url(request, 'images/basketball.jpeg'),
        'page_schema': schema_json({
            "@context": "https://schema.org",
            "@graph": [
                organization_node(request),
                breadcrumb_node(request, [('Accueil', '/'), ('Inscription', '/inscription/')]),
            ],
        }),
    })


def robots_txt(request):
    sitemap_url = absolute_url(request, '/sitemap.xml')
    llms_url = absolute_url(request, '/llms.txt')
    content = f"""User-agent: *
Disallow: /admin/
Disallow: /gestion/
Disallow: /accounts/
Disallow: /boutique/panier/
Disallow: /boutique/commander/
Allow: /static/
Allow: /media/
Allow: /

User-agent: OAI-SearchBot
Disallow: /admin/
Disallow: /gestion/
Disallow: /accounts/
Allow: /

User-agent: ChatGPT-User
Disallow: /admin/
Disallow: /gestion/
Disallow: /accounts/
Allow: /

User-agent: GPTBot
Disallow: /admin/
Disallow: /gestion/
Disallow: /accounts/
Allow: /

User-agent: Googlebot
Disallow: /admin/
Disallow: /gestion/
Disallow: /accounts/
Allow: /

User-agent: Google-Extended
Disallow: /admin/
Disallow: /gestion/
Disallow: /accounts/
Allow: /

# Directives IA / LLM
# LLM-Context: {llms_url}

Sitemap: {sitemap_url}
"""
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


def llms_txt(request):
    base_url = absolute_url(request, '/')
    content = f"""# {ACADEMY_NAME}

Magic Hoops Academy (MHA) est l'academie de basketball de reference a Kinshasa, en Republique Democratique du Congo (RDC).
Situee dans la commune de la Gombe (Avenue de la Science n°5), elle forme les enfants et les jeunes (filles et garcons de 8 a 18+ ans) aux fondamentaux du basketball, a la motricite athletique et aux valeurs cardinales : travail, respect, solidarite et perseverance.

## Informations cles & Entite

- Nom officiel : {ACADEMY_NAME}
- Diminutif / Sigle : MHA Kinshasa
- Sport : Basketball
- Localisation : Avenue de la Science n°5, Commune de la Gombe, Kinshasa, RDC (Republique Democratique du Congo)
- Fondateur & Directeur Technique : Bruno Lobaya Nkoy (alias Coach Magic)
- Public cible : Enfants, adolescents, filles et garcons dès 8 ans jusqu'a 18+ ans (debutants, intermediaires et competiteurs)
- Contact telephonique / WhatsApp : +243 900 824 429
- Email officiel : {ACADEMY_EMAIL}
- Site officiel : {base_url}

## Programmes de Formation Basket

1. **Mini Hoops (U10 a U13 - Filles et Garcons de 8 a 12 ans)** :
   - Objectif : Initiation joyeuse et securisee, motricite globale, decouverte des regles, premiers dribbles, passes et tirs.
   - Ideal pour : Les parents cherchant une academie ou une ecole de basket pour leur jeune enfant a Kinshasa.

2. **Junior Hoops (U14 a U17 - Filles et Garcons de 13 a 16 ans)** :
   - Objectif : Perfectionnement technique individuel, tactique collective, defense, vision du jeu et esprit de groupe.
   - Ideal pour : Les adolescents souhaitant progresser rapidement et disputer des matchs organises.

3. **Elite Hoops (U18 et plus)** :
   - Objectif : Haute intensite physique, preparation athletique, discipline tactique et orientation vers le basketball competitif.

## Questions Frequentes des Parents (FAQ)

- **Comment inscrire mon enfant ou ma fille au basket a Kinshasa ?**  
  Les inscriptions se font directement sur le site web ({absolute_url(request, '/inscription/')}) ou sur le terrain d'entrainement a la Gombe.
- **Les filles sont-elles acceptees ?**  
  Oui, l'academie encourage activement la pratique feminine et accueille avec enthousiasme les filles et les garcons.
- **Où se deroulent les cours et entrainements ?**  
  Sur le terrain officiel de Magic Hoops Academy, Avenue de la Science n°5, Gombe, Kinshasa.
- **Quels sont les jours d'entrainement ?**  
  Entrainements reguliers les mercredis apres-midi et samedis matin.
- **Existe-t-il une boutique pour les tenues de basket ?**  
  Oui, la boutique officielle MHA ({absolute_url(request, '/boutique/')}) propose maillots, t-shirts, ballons officiels et equipements avec retrait direct au terrain ou livraison a Kinshasa.

## Pages et URLs de Reference

- Accueil & Presentation : {base_url}
- Programmes de basket : {base_url}#programmes
- Methode MHA : {base_url}#methode
- Coach et staff : {base_url}#coach
- Inscription jeune basketteur : {absolute_url(request, '/inscription/')}
- Galerie photos et evenements sportifs : {absolute_url(request, '/galerie/')}
- Boutique officielle d'equipements : {absolute_url(request, '/boutique/')}
- Actualites & Sessions : {absolute_url(request, '/news/')}
- Plan du site XML : {absolute_url(request, '/sitemap.xml')}
"""
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


# ==============================================================================
# Gestionnaires & Prévisualisations des Pages d'Erreur (404, 500, 403, 400)
# ==============================================================================

def custom_404(request, exception=None):
    """Gestionnaire personnalisé pour l'erreur 404 (Balle hors-limites / Page non trouvée)."""
    return render(request, '404.html', status=404)


def custom_403(request, exception=None):
    """Gestionnaire personnalisé pour l'erreur 403 (Faute technique / Zone restreinte)."""
    return render(request, '403.html', status=403)


def custom_500(request):
    """Gestionnaire personnalisé pour l'erreur 500 (Temps-mort technique serveur)."""
    return render(request, '500.html', status=500)


def custom_400(request, exception=None):
    """Gestionnaire personnalisé pour l'erreur 400 (Violation de règle / Requête invalide)."""
    return render(request, '400.html', status=400)


def preview_404(request):
    """Route de test pour prévisualiser la page 404."""
    return render(request, '404.html')


def preview_403(request):
    """Route de test pour prévisualiser la page 403."""
    return render(request, '403.html')


def preview_500(request):
    """Route de test pour prévisualiser la page 500."""
    return render(request, '500.html')


def preview_400(request):
    """Route de test pour prévisualiser la page 400."""
    return render(request, '400.html')
