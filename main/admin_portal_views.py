import os
from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.models import Abonnement, Profile
from announcements.models import Annonce
from gallery.models import GalleryAlbum, GalleryCategory, GalleryPhoto
from main.models import AcademyInfo, MethodPillar, Schedule


def staff_required(view_func):
    """
    Sécurise l'accès aux vues d'administration.
    Redirige vers login si non authentifié, lève une PermissionDenied (403) si non staff.
    """
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Accès réservé aux administrateurs de Magic Hoops Academy.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def compute_user_subscription_status(user, today=None):
    """
    Calcule le statut d'abonnement pour un utilisateur :
    - 'paye' (Actif) si abonnement avec statut 'payé' et date_fin >= aujourd'hui
    - 'en_attente' si abonnement avec statut 'en_attente'
    - 'expire' si abonnement avec statut 'expiré' ou date_fin passée
    - 'aucun' si aucun abonnement enregistré
    """
    if today is None:
        today = timezone.localdate()

    subs = list(user.abonnements.all())
    if not subs:
        return {
            'code': 'aucun',
            'label': 'Aucun abonnement',
            'badge_class': 'bg-secondary',
            'color': 'secondary',
            'active_sub': None,
            'latest_sub': None,
        }

    # Trier par date de fin décroissante, puis identifiant
    subs.sort(key=lambda s: (s.date_fin, s.id), reverse=True)
    latest_sub = subs[0]

    # 1. Vérifier si abonnement actif et payé
    active_sub = next((s for s in subs if s.statut == 'payé' and s.date_fin >= today), None)
    if active_sub:
        return {
            'code': 'paye',
            'label': 'Payé (Actif)',
            'badge_class': 'bg-success',
            'color': 'success',
            'active_sub': active_sub,
            'latest_sub': latest_sub,
        }

    # 2. Vérifier si abonnement en attente
    pending_sub = next((s for s in subs if s.statut == 'en_attente'), None)
    if pending_sub:
        return {
            'code': 'en_attente',
            'label': 'En attente',
            'badge_class': 'bg-warning text-dark',
            'color': 'warning',
            'active_sub': None,
            'latest_sub': pending_sub,
        }

    # 3. Sinon expiré
    return {
        'code': 'expire',
        'label': 'Expiré',
        'badge_class': 'bg-danger',
        'color': 'danger',
        'active_sub': None,
        'latest_sub': latest_sub,
    }


# ==============================================================================
# 1. TABLEAU DE BORD (DASHBOARD)
# ==============================================================================

@staff_required
def admin_dashboard(request):
    today = timezone.localdate()

    all_users = list(User.objects.select_related('profile').prefetch_related('abonnements').all())
    total_users_count = len(all_users)
    total_members_count = sum(1 for u in all_users if not u.is_staff)

    # Calcul des compteurs par statut
    count_paye = 0
    count_en_attente = 0
    count_expire = 0
    count_aucun = 0

    for u in all_users:
        st = compute_user_subscription_status(u, today)
        code = st['code']
        if code == 'paye':
            count_paye += 1
        elif code == 'en_attente':
            count_en_attente += 1
        elif code == 'expire':
            count_expire += 1
        else:
            count_aucun += 1

    count_expire_ou_sans = count_expire + count_aucun

    # Métriques générales
    total_photos = GalleryPhoto.objects.count()
    total_albums = GalleryAlbum.objects.count()
    total_annonces = Annonce.objects.count()
    total_schedules = Schedule.objects.count()

    # Données récentes
    recent_users = User.objects.select_related('profile').prefetch_related('abonnements').order_by('-date_joined')[:6]
    for u in recent_users:
        u.sub_status = compute_user_subscription_status(u, today)

    recent_abonnements = Abonnement.objects.select_related('membre').order_by('-id')[:6]
    recent_annonces = Annonce.objects.order_by('-date_publication')[:5]

    context = {
        'total_users': total_users_count,
        'total_members': total_members_count,
        'count_paye': count_paye,
        'count_en_attente': count_en_attente,
        'count_expire': count_expire,
        'count_aucun': count_aucun,
        'count_expire_ou_sans': count_expire_ou_sans,
        'total_photos': total_photos,
        'total_albums': total_albums,
        'total_annonces': total_annonces,
        'total_schedules': total_schedules,
        'recent_users': recent_users,
        'recent_abonnements': recent_abonnements,
        'recent_annonces': recent_annonces,
    }
    return render(request, 'admin_portal/dashboard.html', context)


# ==============================================================================
# 2. GESTION DES UTILISATEURS & ABONNEMENTS
# ==============================================================================

@staff_required
def admin_users_list(request):
    today = timezone.localdate()
    query = request.GET.get('q', '').strip()
    statut_filter = request.GET.get('statut', 'tous').strip().lower()
    role_filter = request.GET.get('role', 'tous').strip().lower()

    users_qs = User.objects.select_related('profile').prefetch_related('abonnements').order_by('-date_joined')

    # Filtre recherche textuelle
    if query:
        users_qs = users_qs.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(profile__telephone__icontains=query)
        )

    # Filtre rôle
    if role_filter == 'staff':
        users_qs = users_qs.filter(is_staff=True)
    elif role_filter == 'membre':
        users_qs = users_qs.filter(is_staff=False)

    users_list = list(users_qs)

    # Calcul des statuts pour chaque utilisateur
    filtered_users = []
    for u in users_list:
        u.sub_status = compute_user_subscription_status(u, today)
        if statut_filter == 'tous' or not statut_filter:
            filtered_users.append(u)
        elif statut_filter == u.sub_status['code']:
            filtered_users.append(u)

    # Pagination
    paginator = Paginator(filtered_users, 15)
    page = request.GET.get('page', 1)
    try:
        users_page = paginator.page(page)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)

    # Statistiques globales pour les compteurs d'onglets
    all_users_for_stats = list(User.objects.prefetch_related('abonnements').all())
    stats_counts = {'tous': len(all_users_for_stats), 'paye': 0, 'en_attente': 0, 'expire': 0, 'aucun': 0}
    for u in all_users_for_stats:
        code = compute_user_subscription_status(u, today)['code']
        stats_counts[code] = stats_counts.get(code, 0) + 1

    context = {
        'users_page': users_page,
        'total_count': len(filtered_users),
        'query': query,
        'statut_filter': statut_filter,
        'role_filter': role_filter,
        'stats_counts': stats_counts,
    }
    return render(request, 'admin_portal/users_list.html', context)


@staff_required
def admin_user_detail(request, user_id):
    today = timezone.localdate()
    member = get_object_or_404(User.objects.select_related('profile').prefetch_related('abonnements'), pk=user_id)
    profile, _ = Profile.objects.get_or_create(user=member)
    sub_status = compute_user_subscription_status(member, today)
    abonnements = member.abonnements.order_by('-date_debut', '-id')

    # Traitement de l'enregistrement / renouvellement manuel d'abonnement
    if request.method == 'POST':
        action = request.POST.get('action', 'add_subscription')
        if action == 'add_subscription':
            montant = request.POST.get('montant', '25.00')
            duree = request.POST.get('duree', '1_mois')
            date_debut_str = request.POST.get('date_debut')
            moyen_paiement = request.POST.get('moyen_paiement', 'cash')
            telephone_paiement = request.POST.get('telephone_paiement', '').strip()
            transaction_id = request.POST.get('transaction_id', '').strip()
            statut = request.POST.get('statut', 'payé')

            # Détermination de la date de début
            if date_debut_str:
                try:
                    date_debut = timezone.datetime.strptime(date_debut_str, '%Y-%m-%d').date()
                except ValueError:
                    date_debut = today
            else:
                # Si l'utilisateur a un abonnement actif qui expire dans le futur, commencer après
                if sub_status['active_sub'] and sub_status['active_sub'].date_fin >= today:
                    date_debut = sub_status['active_sub'].date_fin + timedelta(days=1)
                else:
                    date_debut = today

            # Détermination de la date de fin selon la durée
            if duree == '1_mois':
                date_fin = date_debut + timedelta(days=30)
            elif duree == '3_mois':
                date_fin = date_debut + timedelta(days=90)
            elif duree == '6_mois':
                date_fin = date_debut + timedelta(days=180)
            elif duree == '1_an':
                date_fin = date_debut + timedelta(days=365)
            else:
                # Custom date_fin si spécifiée
                custom_date_fin = request.POST.get('date_fin')
                if custom_date_fin:
                    try:
                        date_fin = timezone.datetime.strptime(custom_date_fin, '%Y-%m-%d').date()
                    except ValueError:
                        date_fin = date_debut + timedelta(days=30)
                else:
                    date_fin = date_debut + timedelta(days=30)

            try:
                montant_dec = float(montant)
            except (ValueError, TypeError):
                montant_dec = 25.00

            Abonnement.objects.create(
                membre=member,
                montant=montant_dec,
                date_debut=date_debut,
                date_fin=date_fin,
                statut=statut,
                moyen_paiement=moyen_paiement,
                telephone_paiement=telephone_paiement,
                transaction_id=transaction_id or f"MANUAL-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            )
            messages.success(request, f"Abonnement de {member.get_full_name() or member.username} enregistré avec succès !")
            return redirect('admin_user_detail', user_id=member.id)

        elif action == 'update_profile':
            # Mise à jour rapide des coordonnées
            member.first_name = request.POST.get('first_name', member.first_name).strip()
            member.last_name = request.POST.get('last_name', member.last_name).strip()
            member.email = request.POST.get('email', member.email).strip()
            member.save()

            profile.telephone = request.POST.get('telephone', profile.telephone).strip()
            profile.adresse = request.POST.get('adresse', profile.adresse).strip()
            profile.ecole_frequente = request.POST.get('ecole_frequente', profile.ecole_frequente).strip()
            profile.niveau = request.POST.get('niveau', profile.niveau).strip()
            profile.poste_prefer = request.POST.get('poste_prefer', profile.poste_prefer).strip()
            profile.contact_parent = request.POST.get('contact_parent', profile.contact_parent).strip()

            date_naissance_str = request.POST.get('date_naissance')
            if date_naissance_str:
                try:
                    profile.date_naissance = timezone.datetime.strptime(date_naissance_str, '%Y-%m-%d').date()
                except ValueError:
                    pass

            taille = request.POST.get('taille')
            if taille:
                try:
                    profile.taille = float(taille)
                except ValueError:
                    pass

            poids = request.POST.get('poids')
            if poids:
                try:
                    profile.poids = float(poids)
                except ValueError:
                    pass

            profile.save()
            messages.success(request, f"Profil de {member.get_full_name() or member.username} mis à jour avec succès.")
            return redirect('admin_user_detail', user_id=member.id)

    # Calcul de l'âge si date de naissance renseignée
    age = None
    if profile.date_naissance:
        age = today.year - profile.date_naissance.year - (
            (today.month, today.day) < (profile.date_naissance.month, profile.date_naissance.day)
        )

    context = {
        'member': member,
        'profile': profile,
        'sub_status': sub_status,
        'abonnements': abonnements,
        'age': age,
        'today': today,
    }
    return render(request, 'admin_portal/user_detail.html', context)


@staff_required
def admin_subscription_quick_action(request, sub_id):
    sub = get_object_or_404(Abonnement, pk=sub_id)
    action = request.POST.get('action') or request.GET.get('action')
    next_url = request.POST.get('next') or request.GET.get('next') or reverse('admin_user_detail', args=[sub.membre_id])

    if action == 'valider':
        sub.statut = 'payé'
        sub.save()
        messages.success(request, f"Abonnement #{sub.id} de {sub.membre.username} validé avec succès (statut : Payé).")
    elif action == 'expirer':
        sub.statut = 'expiré'
        sub.save()
        messages.info(request, f"Abonnement #{sub.id} marqué comme expiré.")
    elif action == 'supprimer':
        sub.delete()
        messages.warning(request, f"Abonnement #{sub_id} supprimé.")
    else:
        messages.error(request, "Action non reconnue.")

    return redirect(next_url)


# ==============================================================================
# 3. GESTION DES HORAIRES (SCHEDULES)
# ==============================================================================

@staff_required
def admin_schedules(request):
    DAYS_ORDER = {
        'Lundi': 1, 'Mardi': 2, 'Mercredi': 3, 'Jeudi': 4,
        'Vendredi': 5, 'Samedi': 6, 'Dimanche': 7
    }

    if request.method == 'POST':
        action = request.POST.get('action', 'create')
        if action == 'create':
            day = request.POST.get('day')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            description = request.POST.get('description', 'Entraînement régulier').strip()

            if day and start_time and end_time:
                Schedule.objects.create(
                    day=day,
                    start_time=start_time,
                    end_time=end_time,
                    description=description or 'Entraînement régulier'
                )
                messages.success(request, f"Créneau du {day} ({start_time} - {end_time}) créé avec succès !")
            else:
                messages.error(request, "Veuillez renseigner le jour et les heures de début et fin.")
            return redirect('admin_schedules')

        elif action == 'update':
            pk = request.POST.get('pk')
            schedule = get_object_or_404(Schedule, pk=pk)
            schedule.day = request.POST.get('day', schedule.day)
            schedule.start_time = request.POST.get('start_time', schedule.start_time)
            schedule.end_time = request.POST.get('end_time', schedule.end_time)
            schedule.description = request.POST.get('description', schedule.description).strip()
            schedule.save()
            messages.success(request, f"Créneau du {schedule.day} mis à jour.")
            return redirect('admin_schedules')

    schedules = list(Schedule.objects.all())
    schedules.sort(key=lambda s: (DAYS_ORDER.get(s.day, 99), s.start_time))

    context = {
        'schedules': schedules,
        'days_choices': Schedule.DAYS_OF_WEEK,
    }
    return render(request, 'admin_portal/schedules.html', context)


@staff_required
def admin_schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    day_desc = f"{schedule.day} ({schedule.start_time} - {schedule.end_time})"
    schedule.delete()
    messages.warning(request, f"Créneau {day_desc} supprimé avec succès.")
    return redirect('admin_schedules')


# ==============================================================================
# 4. GESTION DU CONTENU DU SITE & MÉTHODE (ACADEMYINFO & METHODPILLAR)
# ==============================================================================

@staff_required
def admin_site_content(request):
    academy_info, _ = AcademyInfo.objects.get_or_create(
        nom='Magic Hoops Academy Kinshasa (MHA)'
    )
    pillars = MethodPillar.objects.all().order_by('ordre', 'id')

    if request.method == 'POST':
        action = request.POST.get('action', 'update_info')

        if action == 'update_info':
            academy_info.nom = request.POST.get('nom', academy_info.nom).strip()
            academy_info.slogan = request.POST.get('slogan', academy_info.slogan).strip()
            academy_info.slogan_badge = request.POST.get('slogan_badge', academy_info.slogan_badge).strip()
            academy_info.hero_title = request.POST.get('hero_title', academy_info.hero_title).strip()
            academy_info.hero_subtitle = request.POST.get('hero_subtitle', academy_info.hero_subtitle).strip()
            academy_info.telephone = request.POST.get('telephone', academy_info.telephone).strip()
            academy_info.email = request.POST.get('email', academy_info.email).strip()
            academy_info.adresse_terrain = request.POST.get('adresse_terrain', academy_info.adresse_terrain).strip()
            academy_info.methode_titre = request.POST.get('methode_titre', academy_info.methode_titre).strip()
            academy_info.methode_description = request.POST.get('methode_description', academy_info.methode_description).strip()
            academy_info.methode_cadre_texte = request.POST.get('methode_cadre_texte', academy_info.methode_cadre_texte).strip()
            academy_info.coach_magic_titre = request.POST.get('coach_magic_titre', academy_info.coach_magic_titre).strip()
            academy_info.coach_magic_quote = request.POST.get('coach_magic_quote', academy_info.coach_magic_quote).strip()
            academy_info.coach_magic_bio = request.POST.get('coach_magic_bio', academy_info.coach_magic_bio).strip()
            academy_info.save()

            messages.success(request, "Informations et textes du site mis à jour avec succès !")
            return redirect('admin_site_content')

        elif action == 'create_pillar':
            titre = request.POST.get('titre', '').strip()
            description = request.POST.get('description', '').strip()
            ordre = request.POST.get('ordre', 0)
            icone = request.POST.get('icone', 'bi-dribbble').strip()
            est_actif = request.POST.get('est_actif') == 'on'

            if titre and description:
                try:
                    ordre_int = int(ordre)
                except ValueError:
                    ordre_int = 0

                MethodPillar.objects.create(
                    titre=titre,
                    description=description,
                    ordre=ordre_int,
                    icone=icone or 'bi-dribbble',
                    est_actif=est_actif
                )
                messages.success(request, f"Pilier '{titre}' ajouté avec succès !")
            else:
                messages.error(request, "Le titre et la description du pilier sont obligatoires.")
            return redirect('admin_site_content')

        elif action == 'update_pillar':
            pk = request.POST.get('pk')
            pillar = get_object_or_404(MethodPillar, pk=pk)
            pillar.titre = request.POST.get('titre', pillar.titre).strip()
            pillar.description = request.POST.get('description', pillar.description).strip()
            pillar.icone = request.POST.get('icone', pillar.icone).strip()
            try:
                pillar.ordre = int(request.POST.get('ordre', pillar.ordre))
            except ValueError:
                pass
            pillar.est_actif = request.POST.get('est_actif') == 'on'
            pillar.save()
            messages.success(request, f"Pilier '{pillar.titre}' mis à jour !")
            return redirect('admin_site_content')

    context = {
        'info': academy_info,
        'pillars': pillars,
    }
    return render(request, 'admin_portal/site_content.html', context)


@staff_required
def admin_pillar_delete(request, pk):
    pillar = get_object_or_404(MethodPillar, pk=pk)
    titre = pillar.titre
    pillar.delete()
    messages.warning(request, f"Pilier '{titre}' supprimé.")
    return redirect('admin_site_content')


# ==============================================================================
# 5. GESTION DE LA GALERIE & PHOTOS
# ==============================================================================

@staff_required
def admin_gallery(request):
    categories = GalleryCategory.objects.all().order_by('ordre', 'nom')

    if request.method == 'POST':
        action = request.POST.get('action', 'create_album')

        if action == 'create_album':
            titre = request.POST.get('titre', '').strip()
            categorie_id = request.POST.get('categorie')
            description = request.POST.get('description', '').strip()
            date_evenement_str = request.POST.get('date_evenement')
            lieu = request.POST.get('lieu', 'Terrain principal, Gombe, Kinshasa').strip()
            est_publie = request.POST.get('est_publie') == 'on'
            est_en_vedette = request.POST.get('est_en_vedette') == 'on'
            couverture = request.FILES.get('couverture')

            date_evenement = None
            if date_evenement_str:
                try:
                    date_evenement = timezone.datetime.strptime(date_evenement_str, '%Y-%m-%d').date()
                except ValueError:
                    date_evenement = None

            categorie = None
            if categorie_id:
                categorie = GalleryCategory.objects.filter(pk=categorie_id).first()

            if titre:
                album = GalleryAlbum.objects.create(
                    titre=titre,
                    categorie=categorie,
                    description=description,
                    date_evenement=date_evenement,
                    lieu=lieu or 'Terrain principal, Gombe, Kinshasa',
                    est_publie=est_publie,
                    est_en_vedette=est_en_vedette,
                    couverture=couverture
                )

                # Gestion d'éventuelles photos initiales uploadées en multi-fichiers
                photos = request.FILES.getlist('photos')
                for i, photo_file in enumerate(photos):
                    GalleryPhoto.objects.create(
                        album=album,
                        image=photo_file,
                        titre=f"{album.titre} - Cliché #{i+1}",
                        ordre=i+1
                    )

                messages.success(request, f"Album '{album.titre}' créé avec succès ({len(photos)} photos téléversées) !")
            else:
                messages.error(request, "Le titre de l'album est obligatoire.")
            return redirect('admin_gallery')

        elif action == 'upload_photos':
            album_id = request.POST.get('album_id')
            album = get_object_or_404(GalleryAlbum, pk=album_id)
            photos = request.FILES.getlist('photos')

            if photos:
                current_max_order = album.photos.count()
                for i, photo_file in enumerate(photos):
                    GalleryPhoto.objects.create(
                        album=album,
                        image=photo_file,
                        titre=f"{album.titre} - Cliché #{current_max_order + i + 1}",
                        ordre=current_max_order + i + 1
                    )
                messages.success(request, f"{len(photos)} photo(s) ajoutée(s) avec succès à l'album '{album.titre}'.")
            else:
                messages.warning(request, "Aucune photo sélectionnée.")
            return redirect('admin_gallery')

        elif action == 'update_album':
            album_id = request.POST.get('album_id')
            album = get_object_or_404(GalleryAlbum, pk=album_id)
            album.titre = request.POST.get('titre', album.titre).strip()
            album.description = request.POST.get('description', album.description).strip()
            album.lieu = request.POST.get('lieu', album.lieu).strip()
            album.est_publie = request.POST.get('est_publie') == 'on'
            album.est_en_vedette = request.POST.get('est_en_vedette') == 'on'

            categorie_id = request.POST.get('categorie')
            if categorie_id:
                album.categorie = GalleryCategory.objects.filter(pk=categorie_id).first()
            else:
                album.categorie = None

            date_evenement_str = request.POST.get('date_evenement')
            if date_evenement_str:
                try:
                    album.date_evenement = timezone.datetime.strptime(date_evenement_str, '%Y-%m-%d').date()
                except ValueError:
                    pass

            if 'couverture' in request.FILES:
                album.couverture = request.FILES['couverture']

            album.save()
            messages.success(request, f"Album '{album.titre}' mis à jour !")
            return redirect('admin_gallery')

    albums = GalleryAlbum.objects.annotate(nb_photos=Count('photos')).select_related('categorie').order_by('-est_en_vedette', '-date_creation')
    recent_photos = GalleryPhoto.objects.select_related('album').order_by('-date_ajout')[:12]

    context = {
        'albums': albums,
        'categories': categories,
        'recent_photos': recent_photos,
    }
    return render(request, 'admin_portal/gallery_manage.html', context)


@staff_required
def admin_album_delete(request, pk):
    album = get_object_or_404(GalleryAlbum, pk=pk)
    titre = album.titre
    album.delete()
    messages.warning(request, f"Album '{titre}' et ses photos ont été supprimés.")
    return redirect('admin_gallery')


@staff_required
def admin_photo_delete(request, pk):
    photo = get_object_or_404(GalleryPhoto, pk=pk)
    album_title = photo.album.titre
    photo.delete()
    messages.info(request, f"Photo supprimée de l'album '{album_title}'.")
    return redirect(request.META.get('HTTP_REFERER') or 'admin_gallery')


# ==============================================================================
# 6. GESTION DES ANNONCES & SESSIONS
# ==============================================================================

@staff_required
def admin_announcements(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'create')

        if action == 'create':
            titre = request.POST.get('titre', '').strip()
            type_annonce = request.POST.get('type_annonce', Annonce.TYPE_ACTUALITE)
            message = request.POST.get('message', '').strip()
            resume_seo = request.POST.get('resume_seo', '').strip()
            lieu = request.POST.get('lieu', 'Terrain principal, Gombe, Kinshasa').strip()
            inscription_url = request.POST.get('inscription_url', '').strip()
            cible = request.POST.get('cible', 'tous')
            image = request.FILES.get('image')

            date_debut_str = request.POST.get('date_debut')
            date_fin_str = request.POST.get('date_fin')

            date_debut = None
            if date_debut_str:
                try:
                    date_debut = timezone.datetime.fromisoformat(date_debut_str)
                except ValueError:
                    date_debut = None

            date_fin = None
            if date_fin_str:
                try:
                    date_fin = timezone.datetime.fromisoformat(date_fin_str)
                except ValueError:
                    date_fin = None

            if titre and message:
                Annonce.objects.create(
                    titre=titre,
                    type_annonce=type_annonce,
                    message=message,
                    resume_seo=resume_seo,
                    date_debut=date_debut,
                    date_fin=date_fin,
                    lieu=lieu or 'Terrain principal, Gombe, Kinshasa',
                    inscription_url=inscription_url,
                    cible=cible,
                    image=image,
                    auteur=request.user
                )
                messages.success(request, f"Annonce '{titre}' créée avec succès !")
            else:
                messages.error(request, "Le titre et le contenu du message sont obligatoires.")
            return redirect('admin_announcements')

        elif action == 'update':
            pk = request.POST.get('pk')
            annonce = get_object_or_404(Annonce, pk=pk)
            annonce.titre = request.POST.get('titre', annonce.titre).strip()
            annonce.type_annonce = request.POST.get('type_annonce', annonce.type_annonce)
            annonce.message = request.POST.get('message', annonce.message).strip()
            annonce.resume_seo = request.POST.get('resume_seo', annonce.resume_seo).strip()
            annonce.lieu = request.POST.get('lieu', annonce.lieu).strip()
            annonce.inscription_url = request.POST.get('inscription_url', annonce.inscription_url).strip()
            annonce.cible = request.POST.get('cible', annonce.cible)

            date_debut_str = request.POST.get('date_debut')
            if date_debut_str:
                try:
                    annonce.date_debut = timezone.datetime.fromisoformat(date_debut_str)
                except ValueError:
                    pass

            date_fin_str = request.POST.get('date_fin')
            if date_fin_str:
                try:
                    annonce.date_fin = timezone.datetime.fromisoformat(date_fin_str)
                except ValueError:
                    pass

            if 'image' in request.FILES:
                annonce.image = request.FILES['image']

            annonce.save()
            messages.success(request, f"Annonce '{annonce.titre}' mise à jour !")
            return redirect('admin_announcements')

    annonces = Annonce.objects.select_related('auteur').order_by('-date_publication')

    context = {
        'annonces': annonces,
        'types_annonce': Annonce.TYPES_ANNONCE,
    }
    return render(request, 'admin_portal/announcements_manage.html', context)


@staff_required
def admin_announcement_delete(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk)
    titre = annonce.titre
    annonce.delete()
    messages.warning(request, f"Annonce '{titre}' supprimée.")
    return redirect('admin_announcements')
