from decimal import Decimal
from .models import Product, ProductVariant, TAUX_CONVERSION_CDF

CART_SESSION_ID = 'mha_cart_session'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, variant=None, quantity=1, override_quantity=False):
        """Ajoute un produit ou met à jour sa quantité dans le panier."""
        variant_id = variant.id if variant else 0
        variant_name = variant.nom_variante if variant else ""
        item_key = f"{product.id}_{variant_id}"
        
        base_price = product.prix_usd
        if variant and variant.prix_supplementaire:
            base_price += variant.prix_supplementaire

        if item_key not in self.cart:
            self.cart[item_key] = {
                'product_id': product.id,
                'variant_id': variant_id,
                'variant_name': variant_name,
                'quantity': 0,
                'price': str(base_price),
            }

        if override_quantity:
            self.cart[item_key]['quantity'] = max(1, int(quantity))
        else:
            self.cart[item_key]['quantity'] += int(quantity)

        self.save()

    def remove(self, product_id, variant_id=0):
        """Supprime un article du panier."""
        item_key = f"{product_id}_{variant_id}"
        if item_key in self.cart:
            del self.cart[item_key]
            self.save()

    def clear(self):
        """Vide le panier de session."""
        del self.session[CART_SESSION_ID]
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        """Itère sur les éléments du panier et charge les objets produits depuis la base."""
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {p.id: p for p in products}

        for item_key, item in list(self.cart.items()):
            prod = product_map.get(item['product_id'])
            if not prod:
                continue
            item_copy = item.copy()
            item_copy['item_key'] = item_key
            item_copy['product'] = prod
            item_copy['unit_price'] = Decimal(item['price'])
            item_copy['total_price'] = item_copy['unit_price'] * item['quantity']
            item_copy['total_price_cdf'] = int(item_copy['total_price'] * TAUX_CONVERSION_CDF)
            yield item_copy

    def __len__(self):
        """Retourne le nombre total d'articles dans le panier."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Retourne le montant total en USD ($)."""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_total_price_cdf(self):
        """Retourne le montant total en Francs Congolais (CDF)."""
        return int(self.get_total_price() * TAUX_CONVERSION_CDF)

    @property
    def formatted_cdf(self):
        return f"{self.get_total_price_cdf(): ,}".replace(',', ' ') + " FC"
