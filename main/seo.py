import json

from django.templatetags.static import static
from django.utils.html import strip_tags
from django.utils.text import Truncator


ACADEMY_NAME = "Magic Hoops Academy Kinshasa"
ACADEMY_EMAIL = "info@magichoops.cd"
ACADEMY_ADDRESS = "De la science numéro 5, Commune de la Gombe, Kinshasa"
ACADEMY_DESCRIPTION = (
    "Magic Hoops Academy Kinshasa est l'académie de basketball de référence en RDC "
    "pour enfants, filles et garçons de 8 à 18+ ans (Gombe, Kinshasa). Formation technique, "
    "discipline, esprit d'équipe et accompagnement vers l'excellence."
)


def absolute_static_url(request, path):
    return request.build_absolute_uri(static(path))


def absolute_url(request, path):
    return request.build_absolute_uri(path)


def seo_text(value, length=160):
    cleaned = " ".join(strip_tags(value or "").split())
    return Truncator(cleaned).chars(length)


def schema_json(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def organization_node(request):
    return {
        "@type": ["SportsClub", "SportsActivityLocation", "EducationalOrganization"],
        "@id": absolute_url(request, "/#organization"),
        "name": ACADEMY_NAME,
        "alternateName": ["MHA", "Magic Hoops", "Magic Hoops Academy", "MHA Kinshasa"],
        "description": ACADEMY_DESCRIPTION,
        "url": absolute_url(request, "/"),
        "logo": absolute_static_url(request, "images/mha_logo.jpeg"),
        "image": [
            absolute_static_url(request, "images/basketball.jpeg"),
            absolute_static_url(request, "images/mha_logo.jpeg"),
        ],
        "email": ACADEMY_EMAIL,
        "telephone": "+243900824429",
        "priceRange": "$$",
        "currenciesAccepted": "USD, CDF",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Avenue de la Science numéro 5",
            "addressLocality": "Gombe",
            "addressRegion": "Kinshasa",
            "addressCountry": "CD",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": -4.3162,
            "longitude": 15.2952,
        },
        "areaServed": [
            {
                "@type": "City",
                "name": "Kinshasa",
            },
            {
                "@type": "Country",
                "name": "République Démocratique du Congo",
            },
        ],
        "sport": "Basketball",
        "slogan": "Là où le talent rencontre la discipline",
        "founder": {
            "@type": "Person",
            "name": "Bruno Lobaya Nkoy",
            "alternateName": "Coach Magic",
            "jobTitle": "Fondateur & Directeur Technique",
        },
        "audience": {
            "@type": "Audience",
            "audienceType": "Enfants, adolescents, filles et garçons de 8 à 18 ans et jeunes talents",
            "geographicArea": {
                "@type": "City",
                "name": "Kinshasa",
            },
        },
        "knowsAbout": [
            "Basketball en RDC",
            "Académie de basket Kinshasa",
            "Formation basket pour enfants et adolescents",
            "Basketball féminin et masculin",
            "Mini-basket U10 à U13",
            "Perfectionnement basketball Gombe",
            "Stages et détection basketball",
        ],
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Wednesday"],
                "opens": "15:00",
                "closes": "18:00",
            },
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Saturday"],
                "opens": "08:00",
                "closes": "12:00",
            },
        ],
    }


def breadcrumb_node(request, items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index + 1,
                "name": name,
                "item": absolute_url(request, url),
            }
            for index, (name, url) in enumerate(items)
        ],
    }
