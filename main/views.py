from .models import Schedule
from announcements.models import Annonce
from django.http import Http404, HttpResponse
from django.shortcuts import render
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
        "question": "Où se trouve Magic Hoops Academy à Kinshasa ?",
        "answer": "Magic Hoops Academy s'entraîne à la Gombe, à Kinshasa, à l'adresse De la science numéro 5.",
    },
    {
        "question": "Quels âges peuvent rejoindre l'académie ?",
        "answer": "L'académie accueille les jeunes basketteurs avec des programmes U10 à U13, U14 à U17 et U18 et plus.",
    },
    {
        "question": "Que travaille-t-on pendant les entraînements ?",
        "answer": "Les séances couvrent les fondamentaux du basketball, la coordination, la technique individuelle, le jeu collectif, la discipline et la préparation physique selon le niveau.",
    },
    {
        "question": "Comment suivre les nouvelles sessions de basket ?",
        "answer": "Les nouvelles sessions, parcours et événements sont publiés dans la rubrique Actualités du site.",
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
    recent_announcements = Annonce.objects.all()[:3]
    featured_session = get_featured_session()
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
            for item in FAQS
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
        'featured_session': featured_session,
        'programs': PROGRAMS,
        'method_pillars': METHOD_PILLARS,
        'staff_members': STAFF_MEMBERS,
        'faqs': FAQS,
        'seo_title': "Magic Hoops Academy Kinshasa | Académie de basket pour jeunes à Gombe",
        'seo_description': (
            "Académie de basketball à Kinshasa pour jeunes U10 à U18+: entraînements à la Gombe, "
            "programmes Mini, Junior et Elite Hoops, discipline et formation humaine."
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
    canonical_url = absolute_url(request, '/methode/')
    return render(request, 'main/methode.html', {
        'method_pillars': METHOD_PILLARS,
        'seo_title': "Méthode MHA | Formation basket, discipline et progression",
        'seo_description': "La méthode Magic Hoops Academy combine technique, physique, lecture du jeu et mentalité pour former les jeunes basketteurs à Kinshasa.",
        'canonical_url': canonical_url,
        'og_type': 'website',
        'og_image': absolute_static_url(request, 'images/basketball.jpeg'),
        'page_schema': schema_json({
            "@context": "https://schema.org",
            "@graph": [
                organization_node(request),
                breadcrumb_node(request, [('Accueil', '/'), ('Méthode MHA', '/methode/')]),
            ],
        }),
    })


def staff(request):
    canonical_url = absolute_url(request, '/staff/')
    return render(request, 'main/staff.html', {
        'staff_members': STAFF_MEMBERS,
        'seo_title': "Coach et staff | Magic Hoops Academy Kinshasa",
        'seo_description': "Découvrez le fondateur Bruno Lobaya Nkoy, alias Magic, et l'encadrement Magic Hoops Academy à Kinshasa.",
        'canonical_url': canonical_url,
        'og_type': 'website',
        'og_image': absolute_static_url(request, 'images/mha_logo.jpeg'),
        'page_schema': schema_json({
            "@context": "https://schema.org",
            "@graph": [
                organization_node(request),
                breadcrumb_node(request, [('Accueil', '/'), ('Staff', '/staff/')]),
            ],
        }),
    })


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
    content = f"""User-agent: *
Disallow: /admin/
Disallow: /accounts/
Allow: /static/
Allow: /media/
Allow: /

User-agent: OAI-SearchBot
Disallow: /admin/
Disallow: /accounts/
Allow: /

User-agent: ChatGPT-User
Disallow: /admin/
Disallow: /accounts/
Allow: /

User-agent: GPTBot
Disallow: /admin/
Disallow: /accounts/
Allow: /

User-agent: Googlebot
Disallow: /admin/
Disallow: /accounts/
Allow: /

User-agent: Google-Extended
Disallow: /admin/
Disallow: /accounts/
Allow: /

Sitemap: {sitemap_url}
"""
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


def llms_txt(request):
    base_url = absolute_url(request, '/')
    content = f"""# {ACADEMY_NAME}

Magic Hoops Academy Kinshasa est une academie de basketball jeunesse situee a la Gombe, Kinshasa. Sa mission est de former des jeunes basketteurs avec discipline, respect, travail, cohesion et ambition.

## Informations cles

- Nom: {ACADEMY_NAME}
- Slogan: La ou le talent rencontre la discipline
- Fondateur: Bruno Lobaya Nkoy, alias Magic
- Sport: Basketball
- Public: jeunes basketteurs U10, U14, U18 et plus
- Adresse: {ACADEMY_ADDRESS}
- Email: {ACADEMY_EMAIL}
- Ville: Kinshasa, Republique democratique du Congo

## Pages importantes

- Accueil: {base_url}
- Programmes: {absolute_url(request, '/programmes/')}
- Methode MHA: {absolute_url(request, '/methode/')}
- Coach et staff: {absolute_url(request, '/staff/')}
- Inscription: {absolute_url(request, '/inscription/')}
- Actualites et sessions: {absolute_url(request, '/news/')}
- Sitemap XML: {absolute_url(request, '/sitemap.xml')}

## Description

{ACADEMY_DESCRIPTION}

Les annonces publiees dans la rubrique Actualites peuvent concerner des sessions de basket, des parcours de formation, des evenements et des informations importantes pour les familles.
"""
    return HttpResponse(content, content_type='text/plain; charset=utf-8')
