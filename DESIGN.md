---
name: Magic Hoops Academy Kinshasa - Charte Graphique & Design System
description: Charte graphique officielle de Magic Hoops Academy Kinshasa extraite de l'affiche et de l'identité de marque.
colors:
  basketball-orange: "#FF5E14"
  basketball-orange-deep: "#E04800"
  basketball-orange-light: "#FFF4ED"
  midnight-navy: "#0C1829"
  midnight-navy-deep: "#060D17"
  midnight-navy-light: "#182B46"
  court-sand: "#FFF5EE"
  paper: "#F8F9FA"
  surface: "#FFFFFF"
  surface-alt: "#F1F4F8"
  ink: "#0C1829"
  muted: "#5A6B82"
  line: "rgba(12, 24, 41, 0.10)"
typography:
  display:
    fontFamily: "'Montserrat', 'Outfit', system-ui, sans-serif"
    fontWeight: 900
    letterSpacing: "-0.035em"
    textTransform: "uppercase"
  headline:
    fontFamily: "'Montserrat', 'Outfit', system-ui, sans-serif"
    fontWeight: 800
    letterSpacing: "-0.025em"
  body:
    fontFamily: "'Outfit', system-ui, -apple-system, sans-serif"
    fontWeight: 400
    lineHeight: 1.68
  script:
    fontFamily: "'Caveat', cursive"
    fontWeight: 700
values:
  - "TRAVAIL"
  - "RESPECT"
  - "SOLIDARITÉ"
  - "PERSÉVÉRANCE"
slogan: "Formons les champions de demain !"
---

# Charte Graphique : Magic Hoops Academy Kinshasa

## 1. Direction Artistique & Vision

**Concept central : « L'Énergie du Terrain & L'Excellence de la Formation »**

L'identité visuelle de Magic Hoops Academy puise directement dans son affiche officielle et son emblème :
1. **L'Orange Basketball (#FF5E14 / #E04800)** : Énergie, dynamisme sportif, action, passion et chaleur du terrain.
2. **Le Bleu Marine Nuit (#0C1829 / #060D17)** : Rigueur, autorité pédagogique, discipline, sécurité et professionnalisme.
3. **Le Pêche / Blanc Chaud (#FFF4ED / #FFFFFF)** : Surfaces aérées et lumineuses pour une lisibilité irréprochable.

**Refus absolu du "AI Slop" :**
- Pas de dégradés néon violet/pourpre artificiels.
- Pas de bento boxes surchargées d'icônes inutiles.
- Pas de fausses cartes transparentes illisibles.
- Hiérarchie typographique stricte, contrastes élevés (WCAG 2.2 AA), micro-interactions tactiles et sportives.

---

## 2. Palette Chromatique

| Rôle | Nom du Token | Valeur Hex / CSS | Usage |
| :--- | :--- | :--- | :--- |
| **Action Primaire** | `--primary-color` | `#FF5E14` (rgb(255, 94, 20)) | Boutons CTA, badges phares, accents, icônes d'action |
| **Action Active/Hover**| `--primary-deep` | `#E04800` (rgb(224, 72, 0)) | Survol boutons, focus borders, états pressés |
| **Fond Tinté Orange** | `--primary-light` | `#FFF4ED` | Badges légers, tags de dates, alertes douces |
| **Autorité / Structure**| `--secondary-color`| `#0C1829` (rgb(12, 24, 41)) | En-têtes sombres, barres d'action, typographie forte |
| **Nuit Profonde** | `--secondary-deep` | `#060D17` (rgb(6, 13, 23)) | Footers, hero overlays, contrastes profonds |
| **Fond Global** | `--paper` | `#F8F9FA` | Arrière-plan du site (propre, net, non agressif) |
| **Surface Carte** | `--surface` | `#FFFFFF` | Cartes de programmes, formulaires, encarts |
| **Texte Principal** | `--ink` | `#0C1829` | Corps de texte et titres (contraste maximal > 12:1) |
| **Texte Secondaire** | `--muted` | `#5A6B82` | Métadonnées, descriptions courtes, labels neutres |
| **Ligne de Terrain** | `--line` | `rgba(12, 24, 41, 0.10)` | Délimiteurs et bordures subtiles |

---

## 3. Système Typographique

### A. Titres & Impact Athlétique (Display / Headline)
- **Police** : `Montserrat` (Google Fonts, graisses 700, 800, 900) avec fallback `Outfit`.
- **Rôle** : Donne l'impact compact et percutant de l'affiche (*« CÉRÉMONIE DE REMISE DE BREVETS »*, *« MAGIC HOOPS ACADEMY »*).
- **Caractéristiques** : `letter-spacing: -0.035em`, `text-wrap: balance`, `line-height: 0.95 - 1.05`.

### B. Police Manuscrite & Signature Expressive (Accent Script)
- **Police** : `Caveat` (Google Fonts, graisses 600, 700, cursive).
- **Rôle** : Reproduit la calligraphie expressive de l'affiche (*« de Remise »*, *« Formons les champions de demain ! »*).
- **Usage** : Slogans, annotations manuscrites, accroches inspirantes.

### C. Corps de Texte & Interface (Body & UI)
- **Police** : `Outfit` (Google Fonts, graisses 400, 500, 600, 700).
- **Rôle** : Lecture fluide, claire et moderne sur tous les écrans (mobile, tablette, desktop).

---

## 4. Valeurs et Slogan de l'Académie

- **Slogan officiel** : *« Formons les champions de demain ! »*
- **Ruban des valeurs fondamentales** :
  `★ TRAVAIL ★ RESPECT ★ SOLIDARITÉ ★ PERSÉVÉRANCE`
- **Lieu officiel** : Avenue de la Science n°5, Gombe, Kinshasa
- **Contact officiel** : `+243 900 824 429` | `info@magichoops.cd`

---

## 5. Composants UI & Micro-Interactions

1. **Boutons Pilule Athlétiques (`.btn-primary`)** :
   - Fond : Orange `#FF5E14` dégradé vers `#E04800`.
   - Forme : `border-radius: 999px` (pilule sportive).
   - Interaction : Micro-translation au survol (`translateY(-2px)`), ombre portée orange douce (`rgba(255, 94, 20, 0.28)`), appui tactile net (`translateY(1px) scale(0.99)`).

2. **Cartes & Conteneurs (`.journey-card`, `.program-card`, `.schedule-card`)** :
   - Fond : Blanc pur `#FFFFFF` sur fond `#F8F9FA`.
   - Bordure : 1px délimitée par `var(--line)`.
   - Rayon : 24px à 30px pour une esthétique moderne et soignée.

3. **Ruban des Valeurs (`.motto-strip`)** :
   - Pilule sombre ou claire avec étoiles orange et espacement équilibré.

4. **Accessibilité & Ergonomie Mobile** :
   - Tous les textes respectent la norme **WCAG 2.2 AA**.
   - Cible tactile minimale de 44px sur mobile.
   - Barre d'action rapide flottante pour mobile (`.mobile-cta-bar`).
