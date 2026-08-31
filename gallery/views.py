from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import GalleryCategory, GalleryAlbum, GalleryPhoto
from main.seo import absolute_url, absolute_static_url, organization_node, breadcrumb_node, schema_json


def gallery_list(request):
    selected_category_slug = request.GET.get('cat', '').strip()
    
    categories = GalleryCategory.objects.annotate(
        published_albums_count=Count('albums')
    ).filter(published_albums_count__gt=0)
    
    albums_qs = GalleryAlbum.objects.filter(est_publie=True).select_related('categorie').prefetch_related('photos')
    
    selected_category = None
    if selected_category_slug:
        selected_category = GalleryCategory.objects.filter(slug=selected_category_slug).first()
        if selected_category:
            albums_qs = albums_qs.filter(categorie=selected_category)
            
    featured_album = GalleryAlbum.objects.filter(est_publie=True, est_en_vedette=True).first()
    
    # Photos récentes pour la vue flux visuel
    recent_photos = GalleryPhoto.objects.filter(
        album__est_publie=True
    ).select_related('album').order_by('-album__date_evenement', 'ordre', '-date_ajout')[:24]
    
    canonical_url = absolute_url(request, '/galerie/')
    
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            organization_node(request),
            breadcrumb_node(request, [
                ('Accueil', '/'),
                ('Galerie & Événements', '/galerie/'),
            ]),
            {
                "@type": "CollectionPage",
                "name": "Galerie Photos et Événements - Magic Hoops Academy",
                "description": "Retrouvez les photos des tournois, entraînements, cérémonies et événements officiels de Magic Hoops Academy à Kinshasa.",
                "url": canonical_url,
            }
        ]
    }

    return render(request, 'gallery/gallery_list.html', {
        'categories': categories,
        'selected_category': selected_category,
        'albums': albums_qs,
        'featured_album': featured_album,
        'recent_photos': recent_photos,
        'seo_title': "Galerie Photos & Événements | Magic Hoops Academy Kinshasa",
        'seo_description': "Découvrez en images la vie de Magic Hoops Academy Kinshasa : tournois, remises de brevets, entraînements intensifs et événements jeunesse.",
        'canonical_url': canonical_url,
        'og_type': 'website',
        'og_image': absolute_static_url(request, 'images/basketball.jpeg'),
        'page_schema': schema_json(schema),
    })


def album_detail(request, slug):
    album = get_object_or_404(
        GalleryAlbum.objects.select_related('categorie').prefetch_related('photos'),
        slug=slug,
        est_publie=True
    )
    
    photos = album.photos.all()
    related_albums = GalleryAlbum.objects.filter(
        est_publie=True
    ).exclude(pk=album.pk).order_by('-date_evenement', '-date_creation')[:3]
    
    canonical_url = absolute_url(request, album.get_absolute_url())
    cover_image_url = album.couverture.url if album.couverture else absolute_static_url(request, 'images/basketball.jpeg')
    
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            organization_node(request),
            breadcrumb_node(request, [
                ('Accueil', '/'),
                ('Galerie', '/galerie/'),
                (album.titre, album.get_absolute_url()),
            ]),
            {
                "@type": "ImageGallery",
                "name": album.titre,
                "description": album.description or f"Album photo de l'événement {album.titre} à Magic Hoops Academy",
                "url": canonical_url,
                "image": cover_image_url,
                "dateCreated": album.date_evenement.isoformat() if album.date_evenement else album.date_creation.isoformat(),
            }
        ]
    }

    return render(request, 'gallery/album_detail.html', {
        'album': album,
        'photos': photos,
        'related_albums': related_albums,
        'seo_title': f"{album.titre} | Galerie Magic Hoops Academy Kinshasa",
        'seo_description': album.description[:160] if album.description else f"Photos de l'événement {album.titre} à Magic Hoops Academy Kinshasa.",
        'canonical_url': canonical_url,
        'og_type': 'article',
        'og_image': cover_image_url,
        'page_schema': schema_json(schema),
    })
