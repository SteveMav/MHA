from .cart import Cart


def cart_context(request):
    """Context processor pour injecter le panier dans tous les templates du site."""
    try:
        cart = Cart(request)
        return {
            'cart': cart,
            'cart_count': len(cart),
            'cart_total_usd': cart.get_total_price(),
        }
    except Exception:
        return {
            'cart': None,
            'cart_count': 0,
            'cart_total_usd': 0,
        }
