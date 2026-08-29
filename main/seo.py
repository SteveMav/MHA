import json

from django.templatetags.static import static
from django.utils.html import strip_tags
from django.utils.text import Truncator


ACADEMY_NAME = "Magic Hoops Academy Kinshasa"
ACADEMY_EMAIL = "info@magichoops.cd"
ACADEMY_ADDRESS = "De la science numéro 5, Commune de la Gombe, Kinshasa"
ACADEMY_DESCRIPTION = (
    "Magic Hoops Academy Kinshasa forme les jeunes basketteurs à Kinshasa avec "
    "discipline, respect, travail, cohésion et ambition."
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
        "@type": ["SportsActivityLocation", "EducationalOrganization"],
        "@id": absolute_url(request, "/#organization"),
        "name": ACADEMY_NAME,
        "alternateName": "MHA",
        "description": ACADEMY_DESCRIPTION,
        "url": absolute_url(request, "/"),
        "logo": absolute_static_url(request, "images/mha_logo.jpeg"),
        "image": absolute_static_url(request, "images/basketball.jpeg"),
        "email": ACADEMY_EMAIL,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "De la science numéro 5",
            "addressLocality": "Gombe, Kinshasa",
            "addressCountry": "CD",
        },
        "areaServed": {
            "@type": "City",
            "name": "Kinshasa",
        },
        "sport": "Basketball",
        "slogan": "Là où le talent rencontre la discipline",
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
