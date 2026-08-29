from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Annonce
from .forms import AnnonceForm
from main.seo import (
    ACADEMY_NAME,
    absolute_static_url,
    absolute_url,
    breadcrumb_node,
    organization_node,
    schema_json,
    seo_text,
)


def announcement_list(request):
    announcements = Annonce.objects.all()
    canonical_url = absolute_url(request, '/news/')
    item_list = {
        "@type": "ItemList",
        "name": "Actualités et sessions de basket à Kinshasa",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index + 1,
                "url": request.build_absolute_uri(announcement.get_absolute_url()),
                "name": announcement.titre,
            }
            for index, announcement in enumerate(announcements[:12])
        ],
    }
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            organization_node(request),
            {
                "@type": "CollectionPage",
                "name": "Actualités Magic Hoops Academy",
                "description": "Annonces, sessions de basket, événements et parcours de Magic Hoops Academy à Kinshasa.",
                "url": canonical_url,
                "isPartOf": {"@id": f"{absolute_url(request, '/')}#website"},
            },
            breadcrumb_node(request, [
                ('Accueil', '/'),
                ('Actualités', '/news/'),
            ]),
            item_list,
        ],
    }

    return render(request, 'announcements/announcement_list.html', {
        'announcements': announcements,
        'seo_title': 'Actualités basket à Kinshasa | Sessions Magic Hoops Academy',
        'seo_description': (
            "Retrouvez les annonces, sessions d'entraînement, événements et parcours de formation "
            "basketball de Magic Hoops Academy à Kinshasa."
        ),
        'canonical_url': canonical_url,
        'og_type': 'website',
        'og_image': absolute_static_url(request, 'images/basketball.jpeg'),
        'collection_schema': schema_json(schema),
    })


def announcement_detail(request, slug):
    announcement = get_object_or_404(Annonce, slug=slug)
    return _render_announcement_detail(request, announcement)


def announcement_detail_legacy(request, pk):
    announcement = get_object_or_404(Annonce, pk=pk)
    return redirect(announcement.get_absolute_url(), permanent=True)


def _render_announcement_detail(request, announcement):
    canonical_url = request.build_absolute_uri(announcement.get_absolute_url())
    description = announcement.resume_seo or seo_text(announcement.message)
    image_url = (
        request.build_absolute_uri(announcement.image.url)
        if announcement.image
        else absolute_static_url(request, 'images/basketball.jpeg')
    )
    author_name = (
        announcement.auteur.get_full_name() or announcement.auteur.username
        if announcement.auteur
        else ACADEMY_NAME
    )
    article_node = {
        "@type": "Article",
        "headline": announcement.titre,
        "description": description,
        "datePublished": announcement.date_publication.isoformat(),
        "dateModified": announcement.date_publication.isoformat(),
        "inLanguage": "fr-CD",
        "mainEntityOfPage": canonical_url,
        "image": image_url,
        "author": {
            "@type": "Person" if announcement.auteur else "Organization",
            "name": author_name,
        },
        "publisher": {
            "@id": f"{absolute_url(request, '/')}#organization",
        },
    }
    graph = [
        organization_node(request),
        article_node,
        breadcrumb_node(request, [
            ('Accueil', '/'),
            ('Actualités', '/news/'),
            (announcement.titre, announcement.get_absolute_url()),
        ]),
    ]

    if announcement.is_event_like and announcement.date_debut:
        event_node = {
            "@type": "SportsEvent",
            "name": announcement.titre,
            "description": description,
            "startDate": announcement.date_debut.isoformat(),
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "url": canonical_url,
            "image": image_url,
            "organizer": {
                "@id": f"{absolute_url(request, '/')}#organization",
            },
            "location": {
                "@type": "Place",
                "name": announcement.lieu or "Terrain principal, Gombe, Kinshasa",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "Kinshasa",
                    "addressCountry": "CD",
                },
            },
        }
        if announcement.date_fin:
            event_node["endDate"] = announcement.date_fin.isoformat()
        graph.append(event_node)

    schema = {
        "@context": "https://schema.org",
        "@graph": graph,
    }

    return render(request, 'announcements/announcement_detail.html', {
        'announcement': announcement,
        'seo_title': f'{announcement.titre} | Magic Hoops Academy Kinshasa',
        'seo_description': description,
        'canonical_url': canonical_url,
        'og_type': 'article',
        'og_image': image_url,
        'announcement_schema': schema_json(schema),
    })

@staff_member_required
def announcement_create(request):
    if request.method == 'POST':
        form = AnnonceForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.auteur = request.user
            announcement.save()
            return redirect(announcement.get_absolute_url())
    else:
        form = AnnonceForm()
    return render(request, 'announcements/announcement_form.html', {
        'form': form,
        'title': 'Nouvelle Annonce',
        'seo_title': 'Nouvelle annonce | Magic Hoops Academy',
        'seo_description': "Créer une annonce publique pour Magic Hoops Academy Kinshasa.",
    })

@staff_member_required
def announcement_update(request, pk):
    announcement = get_object_or_404(Annonce, pk=pk)
    data = dict()
    
    if request.method == 'POST':
        form = AnnonceForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            data['html_announcement_list'] = render_to_string('announcements/partials/announcement_item.html', {
                'announcement': announcement,
                'request': request # pass request to check perms in partial
            })
            # Also return the updated detail html if we are on detail page? 
            # For now the user asked for list page with action buttons.
        else:
            data['form_is_valid'] = False
    else:
        form = AnnonceForm(instance=announcement)
        
    context = {'form': form, 'announcement': announcement}
    data['html_form'] = render_to_string('announcements/partials/announcement_form_modal.html',
        context,
        request=request
    )
    return JsonResponse(data)

@staff_member_required
def announcement_delete(request, pk):
    announcement = get_object_or_404(Annonce, pk=pk)
    data = dict()
    if request.method == 'POST':
        announcement.delete()
        data['form_is_valid'] = True
    else:
        context = {'announcement': announcement}
        data['html_form'] = render_to_string('announcements/partials/announcement_confirm_delete_modal.html',
            context,
            request=request
        )
    return JsonResponse(data)
