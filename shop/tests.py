from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from .models import ProductCategory, Product, ProductVariant, Order, OrderItem
from .cart import Cart


class ShopTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = ProductCategory.objects.create(
            nom="Maillots",
            description="Maillots officiels"
        )
        self.product = Product.objects.create(
            nom="Maillot Domicile Orange",
            categorie=self.category,
            prix_usd=Decimal('35.00'),
            description="Maillot de match officiel",
            details_matiere="Polyester Dri-FIT",
            est_actif=True,
            est_en_vedette=True
        )
        self.variant = ProductVariant.objects.create(
            produit=self.product,
            nom_variante="Taille L",
            stock=10
        )

    def test_product_models_str_and_slug(self):
        self.assertEqual(str(self.category), "Maillots")
        self.assertIn("Maillot Domicile Orange", str(self.product))
        self.assertTrue(self.product.slug.startswith("maillot-domicile-orange"))
        self.assertGreater(self.product.prix_cdf, 0)

    def test_product_list_view(self):
        response = self.client.get(reverse('shop:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maillot Domicile Orange")
        self.assertContains(response, "35")

    def test_product_detail_view(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maillot Domicile Orange")
        self.assertContains(response, "Taille L")

    def test_cart_operations(self):
        # 1. Ajouter au panier
        add_url = reverse('shop:cart_add', kwargs={'product_id': self.product.id})
        response = self.client.post(add_url, {
            'variant_id': self.variant.id,
            'quantity': 2,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maillot Domicile Orange")

        # 2. Modifier la quantité
        update_url = reverse('shop:cart_update')
        response = self.client.post(update_url, {
            'product_id': self.product.id,
            'variant_id': self.variant.id,
            'quantity': 3,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "105")

        # 3. Supprimer du panier
        remove_url = reverse('shop:cart_remove', kwargs={'product_id': self.product.id, 'variant_id': self.variant.id})
        response = self.client.post(remove_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Votre panier est actuellement vide")

    def test_checkout_and_order_creation(self):
        # Ajouter d'abord un article au panier
        add_url = reverse('shop:cart_add', kwargs={'product_id': self.product.id})
        self.client.post(add_url, {'variant_id': self.variant.id, 'quantity': 1})

        # Passer commande
        checkout_url = reverse('shop:checkout')
        checkout_data = {
            'client_nom': 'Nkoy',
            'client_prenom': 'Junior',
            'client_telephone': '+243810000000',
            'client_email': 'junior@email.com',
            'mode_retrait': 'retrait_terrain',
            'mode_paiement': 'mpesa',
            'reference_paiement': 'MP123456789',
            'notes_client': 'Merci de préparer pour samedi',
        }
        response = self.client.post(checkout_url, checkout_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Commande Enregistrée avec Succès")

        # Vérifier en base de données
        order = Order.objects.filter(client_nom='Nkoy', client_prenom='Junior').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.total_usd, Decimal('35.00'))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().variante_label, "Taille L")

        # Vérifier la vue de confirmation
        conf_url = reverse('shop:order_confirmation', kwargs={'numero_commande': order.numero_commande})
        conf_response = self.client.get(conf_url)
        self.assertEqual(conf_response.status_code, 200)
        self.assertContains(conf_response, order.numero_commande)
        self.assertContains(conf_response, "Junior Nkoy")
