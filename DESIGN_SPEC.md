# Spécification Design & Implémentation : Magic Hoops Academy Kinshasa

## 1. Contexte & Identité Source
Cette spécification traduit visuellement et techniquement l'affiche officielle de **Magic Hoops Academy** dans le code frontend du projet.
Elle élimine tout "AI slop" (effets superflus, néons incohérents, cartes sans contenu) pour se concentrer sur l'ADN sportif, la lisibilité et l'ergonomie.

---

## 2. Tokens CSS & Variables Système (`styles.css`)

```css
:root {
    /* Action & Énergie (Orange Ballon Officiel) */
    --primary-color: #FF5E14;
    --primary-deep: #E04800;
    --primary-light: #FFF4ED;
    --primary-subtle: rgba(255, 94, 20, 0.10);
    --primary-glow: rgba(255, 94, 20, 0.25);

    /* Autorité & Structure (Bleu Marine Nuit Officiel) */
    --secondary-color: #0C1829;
    --secondary-deep: #060D17;
    --secondary-light: #182B46;
    --secondary-subtle: rgba(12, 24, 41, 0.08);

    /* Fonds & Surfaces */
    --paper: #F8F9FA;
    --surface: #FFFFFF;
    --surface-alt: #F1F4F8;
    --surface-warm: #FFF5EE;
    --ink: #0C1829;
    --muted: #5A6B82;
    --line: rgba(12, 24, 41, 0.10);

    /* Ombres subtiles */
    --shadow-soft: 0 14px 34px rgba(12, 24, 41, 0.07);
    --shadow-hover: 0 22px 50px rgba(12, 24, 41, 0.14);
    --shadow-orange: 0 14px 28px rgba(255, 94, 20, 0.28);

    /* Typographies */
    --font-display: 'Montserrat', 'Outfit', system-ui, sans-serif;
    --font-body: 'Outfit', system-ui, -apple-system, sans-serif;
    --font-script: 'Caveat', cursive, sans-serif;

    /* Rayons & Transitions */
    --radius-sm: 8px;
    --radius-md: 16px;
    --radius-lg: 24px;
    --radius-pill: 999px;
    --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
}
```

---

## 3. Typographie

1. **Titres Display / H1-H3** :
   - `font-family: var(--font-display);`
   - `font-weight: 800` ou `900`;
   - `letter-spacing: -0.03em`;
   - Impact athlétique compact, puissant et clair.

2. **Accroches & Slogans Script** (`.font-script` / `.brand-slogan-script`) :
   - `font-family: var(--font-script);`
   - `font-weight: 700`;
   - `font-size: 1.35rem` à `1.85rem`;
   - Apporte la signature humaine et vivante de l'affiche (*« Formons les champions de demain ! »*).

3. **Corps de texte & Menus** :
   - `font-family: var(--font-body);`
   - `font-weight: 400` / `500` / `700`;
   - Hauteur de ligne aérée : `1.68`.

---

## 4. Composants Clés & Éléments de Marque

1. **Ruban des Valeurs de l'Académie (`.motto-strip`)** :
   - Forme : Pilule étirée ou badge centré.
   - Contenu : `★ TRAVAIL ★ RESPECT ★ SOLIDARITÉ ★ PERSÉVÉRANCE`.
   - Couleurs : Fond `#0C1829` texte `#FFFFFF`, étoiles `#FF5E14` (ou fond blanc bordé).

2. **Boutons (`.btn-primary`, `.btn-outline-primary`)** :
   - `.btn-primary` : Dégradé `#FF5E14` -> `#E04800`, texte blanc, ombre douce orange.
   - `.btn-outline-primary` : Bordure `rgba(12, 24, 41, 0.20)`, hover avec fond `#0C1829`.

3. **Hero & En-têtes** :
   - Overlay dynamique combinant le bleu marine profond `#0C1829` et une touche chaude basketball sans écraser le visuel.
   - Hiérarchie claire : Kicker > Titre H1 > Paragraphe court > CTA Rejoindre / Programmes.

4. **Footer Institutionnel** :
   - Fond marine profond `#060D17` / `#0C1829`.
   - Contact officiel : `+243 900 824 429` | `info@magichoops.cd`.
   - Adresse : De la science numéro 5, Gombe, Kinshasa.
