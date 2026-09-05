# Connexion et diagnostic sur Railway

La page `/accounts/login/` accepte le nom d’utilisateur ou l’adresse e-mail,
avec le mot de passe. Un nom d’utilisateur exact est prioritaire. Si plusieurs
comptes partagent la même adresse e-mail (sans distinction de casse), utiliser
le nom d’utilisateur. Les comptes inactifs ne peuvent pas se connecter.

Le profil membre manquant d’un compte créé avec `createsuperuser` ou depuis
l’administration est créé lors de l’accès à `/accounts/profile/`. Les profils
existants sont conservés. L’administration reste accessible à `/admin/` avec
les permissions Django habituelles.

## Mise en service du correctif

1. Déployer la révision contenant le correctif sur le service Railway.
2. Vérifier la réussite des migrations et de `collectstatic` dans les journaux
   de démarrage. Le `Procfile` du dépôt exécute déjà ces deux commandes.
3. Garder `DEBUG=False` et vérifier que `DATABASE_URL` pointe vers la base
   persistante du service et que `USE_SQLITE` n’est pas activé en production.
4. Tester la connexion avec le nom d’utilisateur, puis avec l’e-mail unique
   du superadmin. Vérifier l’affichage du profil et l’accès à `/admin/`.

Le changement de backend d’authentification demande aux utilisateurs déjà
connectés de se reconnecter après le déploiement ; leurs comptes sont conservés.

Les erreurs Django sont envoyées sur stderr, avec leur traceback, même avec
`DEBUG=False`. En cas de nouvelle erreur 500, consulter les journaux du service
à l’heure de la requête. Ne pas activer le débogage public pour obtenir le
diagnostic et ne pas partager les secrets de configuration.

## Tests locaux

Après installation de `requirements.txt`, lancer les tests avec `USE_SQLITE=True`
pour isoler les vérifications de la base de production :

```powershell
$env:USE_SQLITE = 'True'
$env:DEBUG = 'False'
python manage.py test accounts --noinput
```

Les tests utilisent une base de test temporaire, sans modifier les comptes réels.
