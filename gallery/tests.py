from django.test import TestCase, Client
from django.urls import reverse
from .models import GalleryCategory, GalleryAlbum, GalleryPhoto


class GalleryModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = GalleryCategory.objects.create(
            nom="Tournois et Matchs",
            description="Photos des tournois"
        )
        self.album = GalleryAlbum.objects.create(
            titre="Tournoi Kinshasa 2026",
            categorie=self.category,
            description="Tournoi inter-scolaire",
            lieu="Gombe",
            est_publie=True,
            est_en_vedette=True
        )

    def test_gallery_models_str_and_slug(self):
        self.assertEqual(str(self.category), "Tournois et Matchs")
        self.assertEqual(str(self.album), "Tournoi Kinshasa 2026")
        self.assertTrue(self.album.slug.startswith("tournoi-kinshasa-2026"))

    def test_gallery_list_view(self):
        response = self.client.get(reverse('gallery:gallery_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tournoi Kinshasa 2026")
        self.assertContains(response, "Tournois et Matchs")

    def test_gallery_category_filter(self):
        response = self.client.get(reverse('gallery:gallery_list') + f"?cat={self.category.slug}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tournoi Kinshasa 2026")

    def test_album_detail_view(self):
        response = self.client.get(self.album.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tournoi Kinshasa 2026")
        self.assertContains(response, "Gombe")
