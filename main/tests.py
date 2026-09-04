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
