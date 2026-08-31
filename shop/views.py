from decimal import Decimal
import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.db.models import Count, Q
from django.views.decorators.http import require_POST

from .models import ProductCategory, Product, ProductVariant, Order, OrderItem, TAUX_CONVERSION_CDF
from .cart import Cart
from .forms import CheckoutForm, OrderTrackingForm
from main.seo import absolute_url, absolute_static_url, organization_node, breadcrumb_node, schema_json


def product_list(request):
    selected_cat_slug = request.GET.get('cat', '').strip()
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'default').strip()

    categories = ProductCategory.objects.annotate(
        active_products_count=Count('products', filter=Q(products__est_actif=True))
    ).filter(active_products_count__gt=0)

    products_qs = Product.objects.filter(est_actif=True).select_related('categorie').prefetch_related('images', 'variants')

    selected_category = None
    if selected_cat_slug:
        selected_category = ProductCategory.objects.filter(slug=selected_cat_slug).first()
        if selected_category:
            products_qs = products_qs.filter(categorie=selected_category)

    if search_query:
        products_qs = products_qs.filter(
            Q(nom__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(details_matiere__icontains=search_query)
        )

    if sort_by == 'prix_asc':
        products_qs = products_qs.order_by('prix_usd')
    elif sort_by == 'prix_desc':
        products_qs = products_qs.order_by('-prix_usd')
    elif sort_by == 'nouveau':
        products_qs = products_qs.order_by('-date_creation')
    else:
        products_qs = products_qs.order_by('-est_en_vedette', '-date_creation')

    featured_products = Product.objects.filter(est_actif=True, est_en_vedette=True)[:4]

    canonical_url = absolute_url(request, '/boutique/')

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            organization_node(request),
            breadcrumb_node(request, [
                ('Accueil', '/'),
                ('Boutique MHA', '/boutique/'),
            ]),
            {
                "@type": "CollectionPage",
                "name": "Boutique Officielle Magic Hoops Academy Kinshasa",
                "description": "Achetez les équipements, maillots officiels, t-shirts, ballons et accessoires Magic Hoops Academy à Kinshasa.",
                "url": canonical_url,
            }
        ]
    }

    return render(request, 'shop/product_list.html', {
        'categories': categories,
        'selected_category': selected_category,
        'products': products_qs,
        'featured_products': featured_products,
        'search_query': search_query,
        'sort_by': sort_by,
        'seo_title': "Boutique Officielle MHA | Maillots, T-shirts et Accessoires Basket",
        'seo_description': "Commandez les tenues officielles de basketball Magic Hoops Academy Kinshasa : maillots, t-shirts d'entraînement, ballons et casquettes.",
        'canonical_url': canonical_url,
        'og_type': 'website',
        'og_image': absolute_static_url(request, 'images/basketball.jpeg'),
        'page_schema': schema_json(schema),
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('categorie').prefetch_related('images', 'variants'),
        slug=slug,
        est_actif=True
    )

    related_products = Product.objects.filter(
        est_actif=True,
        categorie=product.categorie
    ).exclude(pk=product.pk)[:4]

    canonical_url = absolute_url(request, product.get_absolute_url())
    img_url = product.image_principale.url if product.image_principale else absolute_static_url(request, 'images/basketball.jpeg')

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            organization_node(request),
            breadcrumb_node(request, [
                ('Accueil', '/'),
                ('Boutique', '/boutique/'),
                (product.nom, product.get_absolute_url()),
            ]),
            {
                "@type": "Product",
                "name": product.nom,
                "description": product.description,
                "image": img_url,
                "offers": {
                    "@type": "Offer",
                    "priceCurrency": "USD",
                    "price": str(product.prix_usd),
                    "availability": "https://schema.org/InStock" if product.en_stock else "https://schema.org/OutOfStock",
                    "seller": {"@id": f"{absolute_url(request, '/')}#organization"}
                }
            }
        ]
    }

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'seo_title': f"{product.nom} | Boutique Magic Hoops Academy Kinshasa",
        'seo_description': product.description[:160],
        'canonical_url': canonical_url,
        'og_type': 'product',
        'og_image': img_url,
        'page_schema': schema_json(schema),
    })


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, est_actif=True)
    cart = Cart(request)
    
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))
    
    variant = None
    if variant_id:
        try:
            variant = ProductVariant.objects.get(id=int(variant_id), produit=product)
        except (ProductVariant.DoesNotExist, ValueError):
            pass

    cart.add(product=product, variant=variant, quantity=quantity)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'cart_total_usd': float(cart.get_total_price()),
            'cart_total_cdf': cart.formatted_cdf,
            'message': f"{product.nom} a été ajouté à votre panier !"
        })

    messages.success(request, f"« {product.nom} » a été ajouté à votre panier.")
    return redirect('shop:cart_detail')


@require_POST
def cart_update(request):
    cart = Cart(request)
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id', 0)
    quantity = int(request.POST.get('quantity', 1))

    try:
        product = Product.objects.get(id=int(product_id))
        variant = None
        if variant_id and int(variant_id) > 0:
            variant = ProductVariant.objects.get(id=int(variant_id))

        if quantity > 0:
            cart.add(product=product, variant=variant, quantity=quantity, override_quantity=True)
        else:
            cart.remove(product_id=product.id, variant_id=int(variant_id or 0))

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': len(cart),
                'cart_total_usd': float(cart.get_total_price()),
                'cart_total_cdf': cart.formatted_cdf,
            })
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return redirect('shop:cart_detail')


@require_POST
def cart_remove(request, product_id, variant_id=0):
    cart = Cart(request)
    cart.remove(product_id=product_id, variant_id=variant_id)
    messages.info(request, "Article retiré du panier.")
    return redirect('shop:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart_detail.html', {
        'cart': cart,
        'seo_title': "Votre Panier d'Achat | Boutique Magic Hoops Academy",
        'seo_description': "Vérifiez vos articles et procédez au règlement de votre commande d'équipements Magic Hoops Academy.",
    })


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Votre panier est vide. Ajoutez des articles avant de passer commande.")
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total_usd = cart.get_total_price()
            order.save()

            # Enregistrement des lignes d'articles commandés
            for item in cart:
                OrderItem.objects.create(
                    commande=order,
                    produit=item['product'],
                    variante_label=item['variant_name'],
                    prix_unitaire_usd=item['unit_price'],
                    quantite=item['quantity'],
                )

            # Vider le panier
            cart.clear()
            messages.success(request, f"Votre commande #{order.numero_commande} a été enregistrée avec succès !")
            return redirect('shop:order_confirmation', numero_commande=order.numero_commande)
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['client_nom'] = request.user.last_name
            initial_data['client_prenom'] = request.user.first_name
            initial_data['client_email'] = request.user.email
            if hasattr(request.user, 'profile'):
                initial_data['client_telephone'] = request.user.profile.telephone
        form = CheckoutForm(initial=initial_data)

    return render(request, 'shop/checkout.html', {
        'form': form,
        'cart': cart,
        'seo_title': "Finaliser la commande | Boutique Magic Hoops Academy",
        'seo_description': "Renseignez vos coordonnées pour la récupération de vos articles Magic Hoops Academy.",
    })


def order_confirmation(request, numero_commande):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__produit'),
        numero_commande=numero_commande
    )

    # Préparation du message WhatsApp pré-rempli pour le secrétariat
    items_summary = ", ".join([f"{it.quantite}x {it.produit.nom if it.produit else 'Article'} ({it.variante_label})" for it in order.items.all()])
    whatsapp_msg = (
        f"Bonjour Magic Hoops Academy ! Je viens de passer la commande *{order.numero_commande}* sur le site MHA.\n"
        f"👤 Nom: {order.nom_complet}\n"
        f"📞 Tél: {order.client_telephone}\n"
        f"📦 Articles: {items_summary}\n"
        f"💰 Total: {order.total_usd} $ ({order.formatted_cdf})\n"
        f"💳 Paiement: {order.get_mode_paiement_display().split(' - ')[0]}\n"
        f"📍 Réception: {order.get_mode_retrait_display()}"
    )
    if order.reference_paiement:
        whatsapp_msg += f"\n🔖 Réf Transaction: {order.reference_paiement}"

    whatsapp_url = f"https://wa.me/243900824429?text={urllib.parse.quote(whatsapp_msg)}"

    return render(request, 'shop/order_confirmation.html', {
        'order': order,
        'whatsapp_url': whatsapp_url,
        'seo_title': f"Commande {order.numero_commande} Confirmée | Magic Hoops Academy",
        'seo_description': f"Récapitulatif de votre commande {order.numero_commande} à l'académie Magic Hoops.",
    })


def order_tracking(request):
    order = None
    searched = False
    form = OrderTrackingForm(request.GET or None)

    if form.is_valid():
        searched = True
        num = form.cleaned_data['numero_commande'].strip()
        tel = form.cleaned_data['telephone'].strip()
        order = Order.objects.filter(
            numero_commande__iexact=num,
            client_telephone__icontains=tel[-7:]
        ).first()

    return render(request, 'shop/order_tracking.html', {
        'form': form,
        'order': order,
        'searched': searched,
        'seo_title': "Suivi de Commande | Boutique Magic Hoops Academy",
        'seo_description': "Vérifiez l'état de préparation et de retrait de votre commande Magic Hoops Academy.",
    })
