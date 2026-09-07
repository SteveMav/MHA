from django.conf import settings


def seo_context(request):
    """
    Fournit les variables globales SEO et d'authentification Google Search Console
    à tous les gabarits du site.
    """
    return {
        'google_site_verification': getattr(settings, 'GOOGLE_SITE_VERIFICATION', ''),
    }
