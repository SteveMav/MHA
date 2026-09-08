---
name: Magic Hoops Academy Kinshasa - Charte graphique et refonte UX
status: Specification pour implementation, non implementee
updated: 2026-09-07
scope: Landing page publique et composants partages concernes
---

# DESIGN.md : Magic Hoops Academy

## 1. Statut et source de vérité

Ce document définit la direction visuelle, le diagnostic de l'interface actuelle et les changements UX à réaliser. Il remplace les anciennes prescriptions de ce fichier sur les dégradés, les ombres orange, les boutons pilules et les grands arrondis.

**Statut : spécification de refonte, pas compte rendu de changements déjà réalisés.** La rédaction de ce document ne modifie pas l'interface.

- `PRODUCT.md` décrit les utilisateurs et les objectifs du produit. Sa référence historique au rouge actif devra être harmonisée avec l'orange retenu ici.
- `DESIGN.md` constitue la référence pour cette refonte et ses critères de validation.
- Les prescriptions contradictoires de l'ancien `DESIGN_SPEC.md` sont remplacées par ce document pour la landing. Les autres parcours nécessitent une vérification avant propagation.
- Sources examinées : rendu local de `/` sur ordinateur et à 390 px de large, `main/templates/main/index.html`, `navbar.html`, `footer.html`, `base_site.html`, `static/css/styles.css`, ancienne charte et spécification.
- Les contenus observés proviennent de la base locale ; leur présence en production n'a pas été vérifiée.
- Les décisions ci-dessous sont des recommandations de design issues de l'audit, pas des résultats de recherche utilisateur ou des mesures de conversion.

## 2. Objectif UX et direction artistique

**Permettre à un parent de comprendre rapidement pour qui est l'académie, où et quand ont lieu les séances, qui encadre les jeunes et comment commencer une inscription.**

Scène d'usage retenue : un parent à Kinshasa ouvre un lien reçu sur WhatsApp, sur téléphone, souvent en journée et avec peu de temps. Les surfaces claires, les informations pratiques et une photographie lisible soutiennent cette situation. Les jeunes et les partenaires restent des publics secondaires.

Direction : **franche, humaine et disciplinée**. Montrer les entraînements et les personnes de Magic Hoops, avec une composition précise et peu d'effets. L'identité repose sur le terrain de la Gombe, l'encadrement, les photographies réelles et la progression des joueurs.

Conserver le logo, l'orange, le bleu nuit, les noms des programmes et les valeurs : travail, respect, solidarité, persévérance. Le slogan « Formons les champions de demain ! » reste disponible comme signature, une seule fois dans la landing, sans police manuscrite imposée.

Éviter de remplacer le style actuel par un autre modèle générique : page entièrement beige, faux magazine de luxe, interface néon ou décor de tableau de bord. Une composition asymétrique ne se justifie que si elle améliore la présentation du contenu.

## 3. Diagnostic : pourquoi l'interface évoque du « AI slop »

Le terme désigne ici une accumulation de recettes graphiques génériques et peu justifiées. Il ne prouve pas qu'une interface a été générée par une IA. Une carte, une ombre ou un dégradé n'est pas intrinsèquement mauvais ; leur répétition et l'absence de fonction claire créent le problème observé.

| Observation | Pourquoi elle dégrade le résultat | Changement requis | Priorité |
| --- | --- | --- | --- |
| Le premier écran empile localisation, sous-titre en capitales, slogan manuscrit, grand titre, paragraphe, quatre encarts, deux boutons et carte d'inscription | Trop de points d'attention ; le visiteur doit trier avant de comprendre | Une accroche, une phrase pratique, une photo, une action principale et un lien secondaire | P1 |
| Gombe, les catégories et l'inscription sont répétés dans le même écran | Allongement sans information supplémentaire | Attribuer une place principale à chaque information ; autoriser seulement les rappels utiles en fin de parcours | P1 |
| Quatre repères sont placés dans une grille de trois colonnes (`.home-proof-strip`) | Le dernier reste isolé ; la composition paraît accidentelle, surtout sur mobile | Supprimer les mini-cartes au profit d'informations pratiques sans boîtes | P1 |
| Une grande carte blanche flotte à droite sur le fond sombre (`.next-session-card`) | Elle concurrence le titre et masque la photographie tout en répétant le CTA | La remplacer par une ligne de prochaine séance après l'introduction, uniquement si la donnée est réelle et à jour | P1 |
| L'orange colore boutons, halos, badges, icônes, labels et slogan | L'accent ne distingue plus les priorités | Réserver l'orange principalement à l'inscription ; rendre les métadonnées neutres | P1 |
| Ombres colorées, dégradés, blur et anneaux décoratifs se superposent | Profondeur artificielle, bruit visuel et contenu photographique assombri | Retirer les effets décoratifs ; réserver l'élévation aux éléments réellement superposés | P1 |
| Cartes et pilules reviennent dans presque toutes les sections | Les contenus perdent leur spécificité et donnent une impression de composants assemblés | Tableau d'horaires, lignes de programmes, liste d'actualités, photo et texte pour la méthode | P1 |
| Junior Hoops est plus large, sombre et surélevé (`.journey-card:nth-child(2)`) | Le traitement évoque une offre tarifaire recommandée alors que le choix dépend de l'âge | Donner la même importance aux trois parcours ; aucun « favori » graphique | P1 |
| La méthode contient des cartes à l'intérieur d'un grand panneau arrondi | Chaque niveau ajoute une frontière sans faciliter la lecture | Photo réelle, texte explicatif et liste de trois ou quatre points sans conteneurs individuels | P2 |
| Montserrat, Outfit, Caveat, capitales et petits surtitres se concurrencent | Plusieurs voix graphiques et un rythme répétitif | Garder deux familles existantes ; titres en casse phrase ; supprimer les surtitres redondants | P2 |
| La photo principale montre surtout un panier fortement assombri | Elle indique le sport, mais ne prouve rien sur MHA ou son encadrement | Choisir une vraie scène d'entraînement avec jeunes, coach et contexte local visibles | P1 |
| La navigation rassemble de nombreux liens, le panier, la connexion et l'inscription | La découverte de l'académie et l'achat de produits ont une importance similaire | Quatre entrées principales ; accès secondaires regroupés et panier limité au contexte boutique | P1 |
| Galerie et actualités précèdent les programmes et les horaires | Le parent traverse du contenu secondaire avant les réponses pratiques | Faire remonter public, programmes, créneaux et accès | P1 |
| Les boutons d'inscription emploient plusieurs formulations | « Rejoindre », « Rejoindre une session » et « Préparer mon inscription » peuvent suggérer des parcours différents | Employer « Inscrire mon enfant » pour la même destination ; adapter seulement lorsqu'une action diffère réellement | P1 |
| Les descriptions reposent sur « excellence », « référence », « champions » ou « encadrement pro » | Des promesses génériques remplacent les preuves | Donner noms, rôles, activités, créneaux et modalités vérifiés ; conserver l'ambition dans une accroche courte | P1 |
| Des contenus locaux s'appellent « Q », « q », « s » et certaines descriptions ne contiennent qu'une lettre | Impression de site inachevé ; les vraies informations deviennent suspectes | Exclure les contenus de test de la publication et mettre en place une sélection éditoriale | P0 |
| Le planning local indique lundi, mercredi, vendredi ; le footer indique mercredi, samedi | Contradiction directement nuisible à une inscription | Une source unique de planning ; supprimer les copies statiques contradictoires | P0 |
| Une icône WhatsApp accompagne un lien `tel:` | L'action ne correspond pas à l'attente créée | Téléphone : icône téléphone et « Appeler ». WhatsApp : lien WhatsApp vérifié et libellé explicite | P0 |
| La charte précédente interdit le « AI slop » mais prescrit pilules, dégradés et ombres orange | Les futures retouches reproduisent les mêmes défauts | Appliquer les règles observables du présent document, au lieu de simples intentions esthétiques | P0 |

P0 : exactitude et cohérence indispensables. P1 : structure et lisibilité prioritaires. P2 : finition après stabilisation de la composition.

Les positions observées sur ordinateur plaçaient les programmes vers 2 500 px et les horaires vers 4 000 px du haut de page. Ce sont des observations du rendu local, pas des constantes à coder ni des mesures de comportement utilisateur.

## 4. Palette et règle 60/30/10

La règle 60/30/10 sert de **repère approximatif de composition**, sans quota de pixels. Elle s'applique aux surfaces graphiques contrôlées sur l'ensemble de la landing, pas à chaque écran ni aux couleurs naturelles des photographies.

| Rôle | Token proposé | Valeur | Utilisation |
| --- | --- | --- | --- |
| Dominante, environ 60 % | `--paper` | `#F8F9FA` | Fonds principaux et espaces de lecture |
| Surface discrète | `--surface-alt` | `#F1F4F8` | Regroupement pratique exceptionnel ; pas d'alternance automatique à chaque section |
| Structure, environ 30 % | `--secondary-color` | `#0C1829` | Titres, footer, éventuelle grande zone de marque |
| Accent, jusqu'à environ 10 % | `--primary-color` | `#FF5E14` | Action principale et rares repères de marque |
| Texte principal | `--ink` | `#0C1829` | Corps, titres, texte du bouton orange |
| Texte secondaire | `--muted` | `#5A6B82` | Dates, explications et métadonnées sur fond clair |
| Accent textuel accessible | `--accent-text` | `#B83F0B` | Lien ou texte court sur fond clair lorsqu'un accent est justifié |
| Survol du CTA | `--action-hover` | `#FF762F` | Variation solide du bouton, texte bleu nuit |
| Bordure de séparation | `--line` | `rgba(12, 24, 41, 0.14)` | Séparateurs non interactifs |
| Bordure de contrôle | `--control-border` | `#5A6B82` | Contours nécessaires à l'identification d'un champ |

Ne pas chercher à atteindre 30 % de bleu nuit en ajoutant des panneaux sombres inutiles. Le rôle des couleurs et la qualité de lecture priment sur la proportion exacte.

### Contrastes

Calculs sRGB sur aplats lors de l'audit :

- Blanc `#FFFFFF` sur orange `#FF5E14` : environ **3,06:1**. Insuffisant pour du texte courant ; ce couple n'est plus autorisé pour les petits libellés.
- Bleu nuit `#0C1829` sur orange `#FF5E14` : environ **5,82:1**. Couple retenu pour le bouton principal.
- Orange sombre `#B83F0B` sur fond `#F8F9FA` : environ **5,31:1**.

Cible WCAG 2.2 AA : au moins 4,5:1 pour le texte courant, 3:1 pour le grand texte selon la définition WCAG et pour les éléments graphiques fonctionnels concernés. Vérifier les états de survol, focus et les textes sur photo séparément ; les calculs ci-dessus ne certifient pas toute l'interface.

Les liens dans les paragraphes sont soulignés. Les erreurs, sélections et statuts ne sont jamais indiqués par la seule couleur.

## 5. Typographie, grille et rythme

Conserver Montserrat pour les titres et Outfit pour les paragraphes et contrôles afin de préserver la continuité de marque. La qualité vient de leur emploi cohérent ; changer de police ne résoudrait pas la composition.

| Usage | Ordinateur | Mobile | Graisse et interligne |
| --- | --- | --- | --- |
| H1 | 48 à 64 px | 34 à 40 px | 700 ou 800 ; 1,08 à 1,15 |
| H2 | 32 à 40 px | 26 à 30 px | 700 ; 1,2 |
| H3 | 22 à 26 px | 20 à 22 px | 700 ; 1,3 |
| Texte | 16 à 18 px | 16 px minimum | 400 ; 1,55 à 1,65 |
| Bouton | 16 px | 16 px | 600 ; 1,3 |
| Métadonnée | 14 px | 14 px | 400 ou 500 ; 1,45 |

- Retirer Caveat de la landing et de ses dépendances lorsqu'aucun autre élément de cette page ne l'utilise.
- Casse phrase par défaut. Capitales réservées au sigle MHA et à de très courts repères, sans répétition systématique au-dessus des titres.
- Un seul H1. H2 pour les sections ; H3 pour les éléments de section. Éviter les sauts H2 vers H4 pour obtenir une taille visuelle.
- Paragraphes de 60 à 70 caractères par ligne au maximum. H1 sur deux ou trois lignes lorsque le contenu et la largeur le permettent, sans retours forcés qui casseraient le mobile.
- Largeur de contenu maximale : 1 200 px. Gouttières : 24 à 32 px sur ordinateur, 16 px sur mobile.
- Échelle d'espacement : 8, 16, 24, 32, 48, 72, 96 px. Espacement entre sections : 72 à 96 px sur ordinateur, 48 à 64 px sur mobile.
- Titre et introduction : 16 px ; introduction et contenu : 24 à 32 px. Grouper les informations liées plus étroitement que les blocs indépendants.
- Aligner les sections sur les mêmes axes. Réserver le centrage à une composition explicitement justifiée.

## 6. Formes, effets, images et icônes

### Formes et élévation

- Bouton : rayon 6 px, hauteur minimale 48 px, padding horizontal 20 à 24 px.
- Image et carte réellement nécessaire : rayon 8 px maximum.
- Cercles : portraits, logo ou contrôle qui le justifie ; aucune pilule pour les informations ordinaires.
- Aucune ombre sur les photos, programmes, horaires, actualités ou boutons.
- Menu déroulant ou panneau superposé : ombre neutre autorisée, par exemple `0 8px 24px rgba(12,24,41,.12)`.
- Aucun halo coloré, texte en dégradé, anneau décoratif, glassmorphism ou dégradé de bouton.
- Un voile sur photo est autorisé seulement pour un texte superposé dont le contraste serait insuffisant. Préférer le texte hors de la photographie dans le hero.
- Une bordure sert à séparer ou à identifier un contrôle. Ne pas ajouter simultanément fond teinté, bordure, ombre et accent latéral à un simple bloc de texte.

### Photographie

Choisir une photographie réelle et autorisée à la publication montrant une interaction entre coach et joueurs. Préserver les visages, les gestes et le contexte dans le recadrage mobile. L'image principale doit rester compréhensible sans filtre sombre.

- Hero : cadrage 4:3 par défaut, sujet ajusté au contenu de l'image.
- Galerie : trois images sélectionnées, ratios cohérents et légendes utiles.
- Ne pas présenter une image générée ou générique comme un entraînement réel de MHA.
- Si aucun visuel adapté n'est disponible, le signaler comme contenu à fournir ; ne pas prétendre que la sélection est terminée.
- Définir largeur et hauteur pour éviter les déplacements de contenu. Charger l'image principale sans lazy loading ; différer les images plus bas dans la page.
- Texte alternatif descriptif pour les images informatives ; attribut alternatif vide pour une image purement décorative.

### Icônes

Conserver une seule famille cohérente. Utiliser les icônes lorsqu'elles facilitent la reconnaissance : téléphone, lieu, ouverture de menu, fermeture, agrandissement. Supprimer les ballons et pictogrammes répétés au-dessus de tous les titres. Une icône informative possède un libellé ; une icône décorative est masquée aux technologies d'assistance.

## 7. Nouvelle architecture de la landing

Ordre principal : **comprendre → identifier son parcours → vérifier l'encadrement et les modalités → commencer l'inscription**.

| Ordre | Section | Contenu et disposition | Action |
| --- | --- | --- | --- |
| 1 | Navigation | Logo ; Programmes ; L'académie ; Horaires et accès ; CTA. Connexion dans un accès secondaire, boutique dans le menu secondaire et le footer | « Inscrire mon enfant » vers `/inscription/` |
| 2 | Introduction | Texte à gauche, photographie réelle à droite ; environ 5/12 et 7/12 de la grille. Aucun panneau flottant ni mini-cartes | CTA principal et lien « Voir les horaires » vers `/#schedule` |
| 3 | Repères pratiques | Âges validés, lieu et prochains créneaux dans une ligne ouverte, sans badges. Données reprises de la source commune | Lien vers horaires et accès |
| 4 | Programmes | Trois lignes : catégorie, nom, objectif court et lien. Même poids pour Mini, Junior et Elite | Liens vers les pages existantes de programme |
| 5 | Encadrement et méthode | Photo du coach, nom et rôle vérifiés, explication d'une séance, trois ou quatre points pédagogiques | Contact secondaire si nécessaire |
| 6 | Horaires et inscription | Tableau jour / heure / groupe si connu ; adresse ; modalités et tarifs validés à proximité | « Inscrire mon enfant » et lien de contact |
| 7 | Vie de l'académie | Trois photographies choisies et une actualité pertinente. Galerie complète accessible par lien | « Voir la galerie » ; titre de l'actualité cliquable |
| 8 | Questions et contact | Quatre à six réponses aux questions bloquantes ; téléphone et accès | Rappel final du CTA si la distance avec le précédent le justifie |
| 9 | Footer | Coordonnées, liens secondaires et signature. Planning issu de la même source ou simple lien vers les horaires | Boutique, connexion et liens utiles |

Conserver les ancres existantes `#programmes`, `#methode`, `#schedule`, `#coach` lorsque leurs contenus sont déplacés ou fusionnés, pour éviter les liens cassés. L'entrée « L'académie » mène à la section d'encadrement. Réserver le panier au parcours boutique.

### Texte du premier écran

Proposition rédactionnelle, à confirmer avec le contenu réel :

> Le basket s'apprend ensemble.
>
> À la Gombe, Magic Hoops accompagne les filles et les garçons dans l'apprentissage du basketball, avec des séances adaptées à leur âge et à leur progression.
>
> Inscrire mon enfant · Voir les horaires

Le repère pratique adjacent doit préciser l'âge minimum une fois confirmé. Éviter d'affirmer « dès 8 ans » sur une page et une autre condition sur la page d'inscription. Le slogan officiel peut être conservé en signature de footer, sans répéter le titre du hero.

Le CTA ouvre le parcours d'inscription existant : il ne promet ni réservation immédiate ni place garantie. Si l'accueil de joueurs majeurs est confirmé, prévoir à proximité de l'inscription un lien secondaire « M'inscrire » adapté à ce public.

### Programmes et horaires

Ne pas traiter les programmes comme des forfaits commerciaux. Aucun parcours recommandé arbitrairement. L'âge et le niveau expliquent le choix. Afficher « À confirmer avec l'équipe » lorsqu'une affectation de groupe n'est pas connue ; ne pas inventer une correspondance entre programme et créneau.

Pour les horaires, utiliser un tableau sémantique avec en-têtes. Sur mobile, afficher chaque séance en groupe compact avec libellés explicites, sans imposer de défilement horizontal. Conserver les associations jour, heure et groupe pour les lecteurs d'écran.

## 8. Responsive et interactions

| Largeur | Transformation |
| --- | --- |
| 1 024 px et plus | Navigation complète si elle tient ; hero en deux colonnes ; repères en ligne ; programmes alignés par colonnes |
| 768 à 1 023 px | Navigation repliée ; hero empilé si le texte ou l'image devient trop étroit ; repères sur deux colonnes sans boîtes |
| Moins de 768 px | Une colonne : titre, phrase, CTA, lien secondaire, photo, repères ; programmes en lignes empilées ; horaires avec labels visibles |

- Vérifier la navigation à 1 024 px avec les vrais libellés ; la replier plus tôt si elle déborde, sans réduire les textes pour la faire tenir.
- Aucun `100vh` obligatoire pour le hero. Sa hauteur suit le contenu.
- À 390 × 844 px et taille de texte normale, le titre, l'offre et le CTA principal doivent être visibles sans défilement. Ne pas réduire la police pour obtenir ce résultat.
- À 320 px et au zoom, priorité au flux naturel et à la lisibilité ; aucun débordement horizontal de page.
- Zone tactile minimale de projet : 44 × 44 px ; CTA principal : hauteur de 48 px minimum.
- Pas de barre d'inscription flottante ajoutée par défaut : elle ferait doublon et occuperait l'écran.
- Menu mobile : bouton avec nom accessible et `aria-expanded`, fermeture par Échap, focus visible et retour au déclencheur. Si le tiroir est modal, contenir le focus et rendre l'arrière-plan inerte pendant son ouverture.
- Ancres : prévoir un décalage correspondant à la hauteur réelle de la navigation fixe, pour que les titres ne soient pas masqués.
- FAQ : conserver les éléments natifs `details` / `summary`, utilisables au clavier et au toucher.
- Galerie : déclencheur natif bouton ou lien. Dans la lightbox, nom accessible, fermeture par Échap, commandes précédent/suivant accessibles, focus contenu puis restitué à l'image d'origine.

### États des contrôles

| État | Règle |
| --- | --- |
| Normal | CTA orange uni et texte bleu nuit ; lien secondaire bleu nuit souligné sur fond clair |
| Survol | Variation unie du fond ou du soulignement ; aucune élévation ni déplacement |
| Focus clavier | Contour 2 px, décalage 3 px ; bleu nuit sur clair, clair sur sombre, contraste vérifié |
| Appui | Retour immédiat par variation de fond ; dimensions inchangées |
| Désactivé | Réservé aux vrais contrôles indisponibles ; raison indiquée si nécessaire ; pas de faux lien désactivé |
| Chargement réel | Libellé explicite, largeur stable, prévention de la double soumission ; pas de délai simulé |
| Erreur de formulaire | Message près du champ, valeurs conservées, résumé accessible après soumission et possibilité de corriger |

Transitions de 150 à 200 ms sur couleur ou opacité. Aucune animation permanente, aucun défilement détourné, aucune apparition qui conditionne la lecture. Respecter `prefers-reduced-motion`, avec suppression des mouvements et du scroll animé. Le contenu essentiel reste disponible sans JavaScript.

## 9. Qualité éditoriale et états de données

| Situation | Comportement attendu |
| --- | --- |
| Aucune prochaine séance publiée | Pas de fausse date ni de promesse « inscriptions ouvertes » automatique ; afficher le planning vérifié ou le contact |
| Planning absent ou incertain | « Contactez l'équipe pour confirmer les prochains créneaux. » Aucun horaire inventé |
| Pas d'actualité pertinente | Omettre le bloc d'actualité de la landing ; ne pas afficher une grande carte vide |
| Moins de trois bonnes photos | Adapter la composition au nombre disponible, sans dupliquer une photo pour remplir une grille |
| Image indisponible | Préserver un espace stable, fournir le texte utile ; prévoir une image de remplacement éditorialement validée |
| Titre ou lieu long | Retour à la ligne ; lien sur une ligne distincte si nécessaire ; pas de chevauchement ou de troncature d'une information essentielle |
| Tarif non validé | Afficher « Tarifs et modalités : contacter l'équipe » ; aucune gratuité ou séance d'essai supposée |
| Donnée de test | Exclure de la sélection publique par statut éditorial ; corriger la source avant publication, sans supprimer de données dans le cadre de cet audit |
| Session passée | Ne pas la qualifier de prochaine ; conserver l'accès éventuel dans les archives |

Règles rédactionnelles : français naturel, phrases courtes, une promesse par paragraphe. Afficher les dates et heures de façon cohérente avec le fuseau du terrain. Bannir les descriptions de test, les faux témoignages, les statistiques non sourcées et les superlatifs non démontrés.

Coordonnées reprises du projet, à confirmer par l'équipe avant publication : Avenue de la Science n°5, Gombe, Kinshasa ; `+243 900 824 429` ; `info@magichoops.cd`. Les afficher depuis une source commune. Normaliser le numéro dans les liens téléphoniques. N'afficher WhatsApp qu'après confirmation que le numéro est utilisable sur ce canal.

## 10. Mise en œuvre et prévention des régressions

| Cible | Travail attendu |
| --- | --- |
| `main/templates/main/index.html` | Recomposer le hero, réordonner les sections, simplifier les programmes et les horaires, retirer les répétitions et les badges décoratifs |
| `main/templates/main/navbar.html` | Réduire les entrées prioritaires et corriger la hiérarchie desktop/mobile |
| `main/templates/main/footer.html` | Retirer les horaires contradictoires, centraliser les coordonnées, simplifier les rappels |
| `main/templates/main/base_site.html` | Ajuster le chargement typographique selon les usages effectifs |
| `static/css/styles.css` | Remplacer les règles concernées, retirer les effets et sélecteurs obsolètes ; éviter une nouvelle couche d'overrides en fin de fichier |
| Sources de contenu et contexte des vues | Unifier planning et coordonnées, sélectionner les publications pertinentes, éliminer les incohérences de présentation |
| `DESIGN_SPEC.md` | Utiliser ce document comme référence de refonte et conserver les contrats des autres parcours tant qu'ils ne sont pas réévalués |

Ordre de réalisation :

1. Corriger les données contradictoires, clarifier l'âge minimum, le planning, les tarifs et les liens de contact.
2. Installer les tokens, la hiérarchie des actions et les règles typographiques.
3. Recomposer navigation, hero et repères pratiques sur mobile et ordinateur.
4. Transformer programmes, encadrement et horaires selon leur rôle.
5. Réduire galerie, actualités, boutique et répétitions sur la landing.
6. Vérifier focus, navigation, états de données, images, contrastes et responsive.
7. Vérifier les autres pages touchées par les composants partagés avant livraison.

Ne pas appliquer une suppression globale de tous les `box-shadow` : elle pourrait supprimer un focus utile ou l'élévation fonctionnelle d'un menu. Ne pas modifier les données utilisateur sans rapport avec la refonte. Les routes existantes et les fonctions d'inscription, de galerie et de boutique doivent continuer à fonctionner.

## 11. Critères d'acceptation

- [ ] Le visiteur identifie le public, le lieu, les créneaux disponibles et la prochaine action sans parcourir la galerie entière.
- [ ] À 390 × 844 px, l'action principale de l'introduction est visible avec l'offre, à taille de texte normale.
- [ ] Le hero ne contient plus de carte flottante, quatre mini-cartes, halos ou slogan répété.
- [ ] Un seul bouton domine chaque zone de décision ; les liens secondaires restent identifiables.
- [ ] Les trois programmes ont la même importance et leur catégorie est compréhensible.
- [ ] Les horaires et coordonnées concordent dans toutes les zones publiques concernées.
- [ ] Aucune donnée de test, date passée présentée comme prochaine, tarif inventé ou promesse non vérifiée n'est publiée.
- [ ] Les photographies représentent réellement MHA, sont autorisées à la publication et gardent leurs sujets visibles sur mobile.
- [ ] Les surfaces ordinaires n'ont ni ombre ni dégradé décoratif ; les rares exceptions fonctionnelles sont justifiées.
- [ ] La palette respecte les rôles définis ; l'orange n'est plus distribué à chaque métadonnée.
- [ ] Les couples de couleurs des textes et contrôles sont vérifiés dans tous leurs états.
- [ ] Aucun débordement horizontal de page à 320, 390, 768, 1 024 et 1 440 px ; lecture possible à 200 % de zoom et reflow vérifié à 320 CSS px.
- [ ] Navigation, FAQ et galerie sont utilisables au clavier ; le focus n'est ni perdu ni masqué.
- [ ] Les cas sans données, titres longs et images manquantes restent compréhensibles.
- [ ] Aucun contenu essentiel n'attend une animation ; la réduction des mouvements est respectée.
- [ ] Les pages utilisant les composants partagés ne subissent pas de régression visuelle ou fonctionnelle.

Ces cases doivent être cochées uniquement après implémentation et contrôle. L'audit initial a porté sur le rendu local ordinateur/mobile, le contenu et le code ; il ne constitue pas une recette complète d'accessibilité ou de performance.

## 12. Décisions encore dépendantes du contenu

| Décision | Responsable attendu | Comportement en attendant |
| --- | --- | --- |
| Âge minimum et accueil des majeurs | Direction de l'académie | Ne pas ajouter de nouvelle limite ; faire concorder les informations avant publication |
| Planning officiel et correspondance avec les groupes | Équipe d'encadrement | Afficher une demande de confirmation plutôt que deux plannings contradictoires |
| Tarifs et éventuelle séance d'essai | Direction de l'académie | Aucune promesse de gratuité ou de disponibilité |
| Photo principale et portrait du coach | Responsable de contenu | Sélectionner des images réelles et autorisées, sans faux remplacement |
| Numéro WhatsApp actif | Équipe de contact | Conserver le téléphone correctement identifié |

## 13. Références et historique

- [Hiérarchie visuelle, Nielsen Norman Group](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/) : importance, contraste et organisation du regard.
- [Contraste minimum, W3C](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html) : seuils et définition du grand texte.
- Audit local et fichiers du projet examinés le 7 septembre 2026.

**2026-09-07 :** remplacement de l'ancienne charte par un diagnostic argumenté et un contrat de refonte. Conservation de l'identité orange/bleu nuit et des familles principales ; suppression prescrite des effets décoratifs systématiques ; priorité aux informations pratiques, aux preuves humaines et à l'inscription. Implémentation à réaliser et à vérifier.

## 14. Aperçu de la refonte du 7 septembre 2026

La nouvelle composition est implémentée sur l'accueil uniquement : styles dédiés dans `static/css/home.css`, navigation et footer propres à cette page, hero clair, programmes en lignes de même importance, méthode sans cartes, planning issu des données existantes et FAQ native. Les contenus personnalisés du titre et du sous-titre restent prioritaires sur la nouvelle accroche par défaut. Les autres pages conservent leurs styles.

Adaptations pour cet aperçu : la photo de basket existante sert de repli tant qu'aucune image principale adaptée n'est configurée. Les médias locaux inspectés ne permettent pas de constituer une sélection authentique d'entraînements ; la galerie et les actualités sont accessibles par liens, sans publication automatique de leurs contenus de test sur l'accueil. Aucun portrait de coach n'a été inventé. Sur mobile, le tableau des séances reste compact et sémantique, sans débordement aux largeurs contrôlées.

Vérifications réalisées : contrôle Django sans erreur, 13 tests ciblés de `main.tests.MainAppTests` réussis, syntaxe du script vérifiée, largeurs 320/390/768/1024/1440 px contrôlées sans débordement horizontal. Le menu mobile ferme après sélection et place le focus sur la section cible. Les photographies MHA, la validation éditoriale complète et un audit exhaustif d'accessibilité restent à effectuer ; les critères non vérifiés ci-dessus ne sont pas réputés satisfaits.
