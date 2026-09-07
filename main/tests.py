from django.test import TestCase, Client
from django.urls import reverse


class MainAppTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_renders_successfully(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        # Verify consolidated sections on the homepage
        self.assertContains(response, 'id="programmes"')
        self.assertContains(response, 'id="methode"')
        self.assertContains(response, 'id="schedule"')
        self.assertContains(response, 'id="coach"')
        self.assertContains(response, 'id="galerie"')
        self.assertContains(response, 'id="mhaLightbox"')
        # Verify method content
        self.assertContains(response, "Former le joueur complet, pas seulement le scoreur.")
        self.assertContains(response, "Le cadre fait la différence")
        self.assertContains(response, "Technique")
        self.assertContains(response, "Physique")
        self.assertContains(response, "Lecture du jeu")
        self.assertContains(response, "Mentalité")
        # Verify staff content
        self.assertContains(response, "Bruno Lobaya Nkoy, alias Coach Magic.")
        # Verify programs
        self.assertContains(response, "Mini Hoops")
        self.assertContains(response, "Junior Hoops")
        self.assertContains(response, "Elite Hoops")

    def test_homepage_shows_announcement_spotlight_when_announcement_exists(self):
        from announcements.models import Annonce
        Annonce.objects.create(
            titre="Session Spéciale Découverte",
            message="Venez nombreux pour le test des nouveaux talents."
        )
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "announcement-spotlight-bar")
        self.assertContains(response, "Session Spéciale Découverte")

    def test_homepage_shows_gallery_photos_when_photos_exist(self):
        from gallery.models import GalleryAlbum, GalleryPhoto
        from django.core.files.uploadedfile import SimpleUploadedFile
        album = GalleryAlbum.objects.create(
            titre="Tournoi Test",
            est_publie=True
        )
        dummy_img = SimpleUploadedFile("test.jpg", b"dummy content", content_type="image/jpeg")
        GalleryPhoto.objects.create(
            album=album,
            image=dummy_img,
            titre="Photo Test Match"
        )
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "mha-lightbox-trigger")
        self.assertContains(response, "Photo Test Match")

    def test_methode_redirects_to_homepage_anchor(self):
        response = self.client.get(reverse('methode'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/#methode')

    def test_staff_redirects_to_homepage_anchor(self):
        response = self.client.get(reverse('staff'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/#coach')

    def test_programmes_page(self):
        response = self.client.get(reverse('programmes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mini Hoops")

    def test_robots_txt_and_llms_txt(self):
        resp_robots = self.client.get(reverse('robots_txt'))
        self.assertEqual(resp_robots.status_code, 200)
        self.assertIn("Sitemap:", resp_robots.content.decode('utf-8'))

        resp_llms = self.client.get(reverse('llms_txt'))
        self.assertEqual(resp_llms.status_code, 200)
        self.assertIn("# Magic Hoops Academy Kinshasa", resp_llms.content.decode('utf-8'))
        self.assertIn("#methode", resp_llms.content.decode('utf-8'))
        self.assertIn("Gombe", resp_llms.content.decode('utf-8'))
        self.assertIn("filles et garcons", resp_llms.content.decode('utf-8'))

    def test_seo_and_geo_meta_tags(self):
        with self.settings(
            GOOGLE_SITE_VERIFICATION="TEST_VERIFICATION_TOKEN_123",
            GOOGLE_ANALYTICS_ID="G-TESTANALYTICS123",
        ):
            response = self.client.get(reverse('index'))
            self.assertEqual(response.status_code, 200)
            content = response.content.decode('utf-8')
            # Geo tags
            self.assertIn('name="geo.region" content="CD-KN"', content)
            self.assertIn('name="geo.placename" content="Kinshasa, Gombe"', content)
            self.assertIn('name="geo.position" content="-4.3162;15.2952"', content)
            self.assertIn('name="ICBM" content="-4.3162, 15.2952"', content)
            # Google site verification
            self.assertIn('name="google-site-verification" content="TEST_VERIFICATION_TOKEN_123"', content)
            # Google Analytics
            self.assertIn('gtag/js?id=G-TESTANALYTICS123', content)
            # Keywords and title
            self.assertIn('name="keywords"', content)
            self.assertIn("Filles &amp; Garçons", content)

    def test_schema_json_ld_structure(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # Check structured schema elements
        self.assertIn('"SportsClub"', content)
        self.assertIn('"GeoCoordinates"', content)
        self.assertIn('"Kinshasa"', content)
        self.assertIn('"Audience"', content)
        self.assertIn('"Bruno Lobaya Nkoy"', content)
        self.assertIn('"FAQPage"', content)

    def test_sitemap_xml(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('https://', content)
        self.assertIn('/programmes/', content)
        self.assertIn('/inscription/', content)


class AdminPortalTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        from django.utils import timezone
        from datetime import timedelta
        from main.models import AcademyInfo, MethodPillar, Schedule
        from accounts.models import Profile, Abonnement

        self.today = timezone.localdate()

        # Regular non-staff user
        self.user = User.objects.create_user(
            username='player1',
            email='player1@magichoops.cd',
            password='password123',
            first_name='Jonathan',
            last_name='Kamba'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            telephone='+243810000001',
            poste_prefer='Meneur'
        )

        # Staff user
        self.staff_user = User.objects.create_user(
            username='staff_coach',
            email='staff@magichoops.cd',
            password='password123',
            is_staff=True,
            first_name='Coach',
            last_name='Bruno'
        )

    def test_admin_portal_access_restricted_for_anonymous_user(self):
        urls = [
            reverse('admin_dashboard'),
            reverse('admin_users_list'),
            reverse('admin_user_detail', args=[self.user.id]),
            reverse('admin_schedules'),
            reverse('admin_site_content'),
            reverse('admin_gallery'),
            reverse('admin_announcements'),
        ]
        for url in urls:
            resp = self.client.get(url)
            # Must redirect to login
            self.assertEqual(resp.status_code, 302, f"Expected 302 redirect for {url}")
            self.assertIn('/accounts/login/', resp.url)

    def test_admin_portal_access_forbidden_for_non_staff_user(self):
        self.client.login(username='player1', password='password123')
        urls = [
            reverse('admin_dashboard'),
            reverse('admin_users_list'),
            reverse('admin_user_detail', args=[self.user.id]),
            reverse('admin_schedules'),
            reverse('admin_site_content'),
            reverse('admin_gallery'),
            reverse('admin_announcements'),
        ]
        for url in urls:
            resp = self.client.get(url)
            # Must return 403 Forbidden
            self.assertEqual(resp.status_code, 403, f"Expected 403 for non-staff on {url}")

    def test_admin_portal_access_granted_for_staff_user(self):
        self.client.login(username='staff_coach', password='password123')
        urls = [
            reverse('admin_dashboard'),
            reverse('admin_users_list'),
            reverse('admin_user_detail', args=[self.user.id]),
            reverse('admin_schedules'),
            reverse('admin_site_content'),
            reverse('admin_gallery'),
            reverse('admin_announcements'),
        ]
        for url in urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Expected 200 for staff on {url}")

    def test_subscription_status_calculation(self):
        from main.admin_portal_views import compute_user_subscription_status
        from accounts.models import Abonnement
        from datetime import timedelta

        # 1. No subscription -> 'aucun'
        status = compute_user_subscription_status(self.user, self.today)
        self.assertEqual(status['code'], 'aucun')

        # 2. Pending subscription -> 'en_attente'
        sub_pending = Abonnement.objects.create(
            membre=self.user,
            montant=25.00,
            date_debut=self.today,
            date_fin=self.today + timedelta(days=30),
            statut='en_attente',
            moyen_paiement='mpesa'
        )
        status = compute_user_subscription_status(self.user, self.today)
        self.assertEqual(status['code'], 'en_attente')

        # 3. Active paid subscription -> 'paye'
        sub_pending.statut = 'payé'
        sub_pending.save()
        status = compute_user_subscription_status(self.user, self.today)
        self.assertEqual(status['code'], 'paye')

        # 4. Expired subscription (date in past) -> 'expire'
        sub_pending.date_fin = self.today - timedelta(days=1)
        sub_pending.save()
        status = compute_user_subscription_status(self.user, self.today)
        self.assertEqual(status['code'], 'expire')

        # 5. Staff user -> 'staff' (exempté d'abonnement)
        status_staff = compute_user_subscription_status(self.staff_user, self.today)
        self.assertEqual(status_staff['code'], 'staff')
        self.assertEqual(status_staff['label'], 'Staff / Exempté')

    def test_admin_user_detail_add_subscription(self):
        from accounts.models import Abonnement
        self.client.login(username='staff_coach', password='password123')

        post_data = {
            'action': 'add_subscription',
            'montant': '35.00',
            'duree': '3_mois',
            'date_debut': str(self.today),
            'moyen_paiement': 'cash',
            'statut': 'payé',
            'telephone_paiement': '+243999999999',
            'transaction_id': 'CASH-001',
        }
        resp = self.client.post(reverse('admin_user_detail', args=[self.user.id]), post_data)
        self.assertEqual(resp.status_code, 302)

        sub = Abonnement.objects.filter(membre=self.user).first()
        self.assertIsNotNone(sub)
        self.assertEqual(sub.montant, 35.00)
        self.assertEqual(sub.statut, 'payé')
        self.assertEqual(sub.moyen_paiement, 'cash')
        self.assertEqual(sub.date_debut, self.today)

    def test_admin_subscription_quick_actions(self):
        from accounts.models import Abonnement
        from datetime import timedelta
        self.client.login(username='staff_coach', password='password123')

        sub = Abonnement.objects.create(
            membre=self.user,
            montant=20.00,
            date_debut=self.today,
            date_fin=self.today + timedelta(days=30),
            statut='en_attente'
        )

        # Quick action: valider
        resp = self.client.post(reverse('admin_subscription_quick_action', args=[sub.id]), {'action': 'valider'})
        self.assertEqual(resp.status_code, 302)
        sub.refresh_from_db()
        self.assertEqual(sub.statut, 'payé')

        # Quick action: expirer
        resp = self.client.post(reverse('admin_subscription_quick_action', args=[sub.id]), {'action': 'expirer'})
        self.assertEqual(resp.status_code, 302)
        sub.refresh_from_db()
        self.assertEqual(sub.statut, 'expiré')

        # Quick action: supprimer
        resp = self.client.post(reverse('admin_subscription_quick_action', args=[sub.id]), {'action': 'supprimer'})
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Abonnement.objects.filter(id=sub.id).exists())

    def test_schedule_crud(self):
        from main.models import Schedule
        self.client.login(username='staff_coach', password='password123')

        # Create
        create_data = {
            'action': 'create',
            'day': 'Samedi',
            'start_time': '08:00',
            'end_time': '10:00',
            'description': 'Entraînement Mini Hoops U10'
        }
        resp = self.client.post(reverse('admin_schedules'), create_data)
        self.assertEqual(resp.status_code, 302)

        sched = Schedule.objects.filter(day='Samedi', description='Entraînement Mini Hoops U10').first()
        self.assertIsNotNone(sched)

        # Update
        update_data = {
            'action': 'update',
            'pk': sched.id,
            'day': 'Samedi',
            'start_time': '08:30',
            'end_time': '10:30',
            'description': 'Séance U10 Modifiée'
        }
        resp = self.client.post(reverse('admin_schedules'), update_data)
        self.assertEqual(resp.status_code, 302)
        sched.refresh_from_db()
        self.assertEqual(sched.description, 'Séance U10 Modifiée')

        # Delete
        resp = self.client.get(reverse('admin_schedule_delete', args=[sched.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Schedule.objects.filter(id=sched.id).exists())

    def test_site_content_and_method_pillars_dynamic(self):
        from main.models import AcademyInfo, MethodPillar
        self.client.login(username='staff_coach', password='password123')

        # Update AcademyInfo
        info_data = {
            'action': 'update_info',
            'hero_title': 'Former les légendes de Kinshasa !',
            'hero_subtitle': 'Nouveau sous-titre dynamique.',
            'slogan_badge': 'Elite Basketball CD',
            'telephone': '+243888888888',
            'email': 'contact@magichoops.cd',
            'adresse_terrain': 'Stade des Martyrs Kinshasa',
            'methode_titre': 'La rigueur absolue sur le terrain.',
            'methode_description': 'Description de la méthode mise à jour.',
            'methode_cadre_texte': 'Le respect avant le score.',
            'coach_magic_titre': 'Coach Bruno Lobaya Nkoy (Le Stratège)',
            'coach_magic_quote': '« Travailler chaque jour comme si c\'était la finale. »',
            'coach_magic_bio': 'Bio complète du coach mise à jour.',
        }
        resp = self.client.post(reverse('admin_site_content'), info_data)
        self.assertEqual(resp.status_code, 302)

        # Add new method pillar
        pillar_data = {
            'action': 'create_pillar',
            'titre': 'Défense Agressive',
            'description': 'Pression continue sur le porteur de balle.',
            'ordre': '5',
            'icone': 'bi-shield-shaded',
            'est_actif': 'on',
        }
        resp = self.client.post(reverse('admin_site_content'), pillar_data)
        self.assertEqual(resp.status_code, 302)

        # Verify on homepage
        home_resp = self.client.get(reverse('index'))
        self.assertEqual(home_resp.status_code, 200)
        self.assertContains(home_resp, 'Former les légendes de Kinshasa !')
        self.assertContains(home_resp, 'Elite Basketball CD')
        self.assertContains(home_resp, 'Stade des Martyrs Kinshasa')
        self.assertContains(home_resp, 'Coach Bruno Lobaya Nkoy (Le Stratège)')
        self.assertContains(home_resp, 'Défense Agressive')

    def _create_test_image(self):
        import io
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        buffer = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='blue')
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return SimpleUploadedFile("test_photo.jpg", buffer.getvalue(), content_type="image/jpeg")

    def test_admin_async_photo_upload_permissions(self):
        from gallery.models import GalleryAlbum
        album = GalleryAlbum.objects.create(titre="Album Test Permissions")
        url = reverse('admin_async_photo_upload', args=[album.id])

        # Non authentifié -> redirection login
        resp = self.client.post(url, {})
        self.assertEqual(resp.status_code, 302)

        # Authentifié non staff -> 403 Forbidden
        self.client.force_login(self.user)
        resp = self.client.post(url, {})
        self.assertEqual(resp.status_code, 403)

    def test_admin_async_photo_upload_success(self):
        from gallery.models import GalleryAlbum, GalleryPhoto
        self.client.force_login(self.staff_user)
        album = GalleryAlbum.objects.create(titre="Album Test Upload Async")
        url = reverse('admin_async_photo_upload', args=[album.id])

        test_img = self._create_test_image()
        resp = self.client.post(url, {'photo': test_img})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['album']['total_photos'], 1)
        self.assertEqual(data['photo']['ordre'], 1)

        # Deuxième photo -> incrémentation de l'ordre
        test_img2 = self._create_test_image()
        resp2 = self.client.post(url, {'photo': test_img2})
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertEqual(data2['album']['total_photos'], 2)
        self.assertEqual(data2['photo']['ordre'], 2)

    def test_admin_async_photo_upload_invalid_file(self):
        from gallery.models import GalleryAlbum
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username='staff_coach', password='password123')
        album = GalleryAlbum.objects.create(titre="Album Test Corrupt")
        url = reverse('admin_async_photo_upload', args=[album.id])

        # Envoi d'un fichier corrompu
        fake_file = SimpleUploadedFile("fake.jpg", b"not an image data", content_type="image/jpeg")
        resp = self.client.post(url, {'photo': fake_file})
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data['success'])

    def test_admin_async_photo_upload_exceeds_2mb(self):
        from gallery.models import GalleryAlbum
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username='staff_coach', password='password123')
        album = GalleryAlbum.objects.create(titre="Album Test Limit 2MB")
        url = reverse('admin_async_photo_upload', args=[album.id])

        # Créer un fichier de 2.5 Mo
        oversized_content = b'x' * (int(2.5 * 1024 * 1024))
        oversized_file = SimpleUploadedFile("too_heavy.jpg", oversized_content, content_type="image/jpeg")
        resp = self.client.post(url, {'photo': oversized_file})
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data['success'])
        self.assertIn("2 Mo", data['error'])

    def test_admin_gallery_create_album_ajax(self):
        from gallery.models import GalleryAlbum
        self.client.login(username='staff_coach', password='password123')
        resp = self.client.post(
            reverse('admin_gallery'),
            {
                'action': 'create_album',
                'titre': 'Album Ajax Tournoi',
                'is_ajax': '1',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertTrue(GalleryAlbum.objects.filter(titre='Album Ajax Tournoi').exists())

    def test_staff_profile_displays_exempt_and_no_subscription_payment(self):
        self.client.force_login(self.staff_user)
        resp = self.client.get(reverse('profile'))
        self.assertEqual(resp.status_code, 200)
        # Staff badge visible and exempt text
        self.assertContains(resp, 'Membre du Staff')
        self.assertContains(resp, "Exempté d'abonnement")
        self.assertContains(resp, 'Espace Administration')
        # Payment buttons and modals must NOT appear
        self.assertNotContains(resp, 'Payer mon abonnement')
        self.assertNotContains(resp, 'id="subscriptionModal"')
        self.assertNotContains(resp, 'Abonnement Inactif/Expiré')
        # Youth player fields must NOT appear for staff
        self.assertNotContains(resp, 'Contact Parent/Tuteur')

    def test_player_profile_displays_subscription_options(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('profile'))
        self.assertEqual(resp.status_code, 200)
        # Player should see subscription options
        self.assertContains(resp, 'Payer mon abonnement')
        self.assertContains(resp, 'id="subscriptionModal"')
        self.assertContains(resp, 'Contact Parent/Tuteur')

    def test_admin_user_detail_for_staff_member(self):
        from accounts.models import Abonnement
        self.client.force_login(self.staff_user)
        # 1. View staff member in admin user detail
        resp = self.client.get(reverse('admin_user_detail', args=[self.staff_user.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Staff / Exempté d'abonnement")
        self.assertContains(resp, "Statut & Privilèges Staff")
        self.assertNotContains(resp, "Enregistrer ou Renouveler un Abonnement")

        # 2. Attempting to add a subscription for staff is blocked
        post_data = {
            'action': 'add_subscription',
            'montant': '25.00',
            'duree': '1_mois',
            'moyen_paiement': 'cash',
            'statut': 'payé',
        }
        resp = self.client.post(reverse('admin_user_detail', args=[self.staff_user.id]), post_data, follow=True)
        self.assertRedirects(resp, reverse('admin_user_detail', args=[self.staff_user.id]))
        self.assertContains(resp, "Coach Bruno est membre du personnel (Staff)")
        self.assertFalse(Abonnement.objects.filter(membre=self.staff_user).exists())


class ErrorPagesTests(TestCase):
    def setUp(self):
        from django.test import RequestFactory
        self.factory = RequestFactory()
        self.client = Client()

    def test_custom_404_view(self):
        from main.views import custom_404
        request = self.factory.get('/page-inconnue/')
        response = custom_404(request)
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, '404', status_code=404)
        self.assertContains(response, 'Balle Hors-Limites', status_code=404)
        self.assertContains(response, 'Retour au terrain', status_code=404)

    def test_custom_403_view(self):
        from main.views import custom_403
        request = self.factory.get('/zone-interdite/')
        response = custom_403(request)
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, '403', status_code=403)
        self.assertContains(response, 'Zone Restreinte', status_code=403)
        self.assertContains(response, 'Se connecter à mon compte', status_code=403)

    def test_custom_500_view(self):
        from main.views import custom_500
        request = self.factory.get('/erreur-serveur/')
        response = custom_500(request)
        self.assertEqual(response.status_code, 500)
        self.assertContains(response, '500', status_code=500)
        self.assertContains(response, 'Temps-Mort Technique', status_code=500)
        self.assertContains(response, 'Recharger la page', status_code=500)
        self.assertContains(response, '+243 900 824 429', status_code=500)

    def test_custom_400_view(self):
        from main.views import custom_400
        request = self.factory.get('/mauvaise-requete/')
        response = custom_400(request)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, '400', status_code=400)
        self.assertContains(response, 'Violation de Règle', status_code=400)
        self.assertContains(response, 'Requête invalide', status_code=400)

    def test_preview_error_views(self):
        # Test direct preview URLs
        urls = [
            reverse('preview_404'),
            reverse('preview_500'),
            reverse('preview_403'),
            reverse('preview_400'),
        ]
        for url in urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Preview URL {url} failed with status {resp.status_code}")

    def test_handler404_in_production_mode(self):
        from django.test import override_settings
        with override_settings(DEBUG=False):
            resp = self.client.get('/page-totalement-inexistante/')
            self.assertEqual(resp.status_code, 404)
            self.assertContains(resp, 'Balle Hors-Limites', status_code=404)
            self.assertContains(resp, '404', status_code=404)
            self.assertContains(resp, 'Retour au terrain', status_code=404)



