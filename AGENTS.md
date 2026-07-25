# AGENTS.md

## Objectif
Ce projet est une marketplace Django destinée au marché tunisien. L'agent doit aider à améliorer, corriger et étendre le code sans réécrire inutilement l'architecture existante.

## Contexte projet
- Projet Django 6.0 avec application principale `annonces`.
- Base de données SQLite (`db.sqlite3`) pour le développement local.
- Environnement virtuel Python présent dans `env/`.
- Langue et conventions métier en français.
- Les exposants métier sont ciblés sur l'anonymat des coordonnées vendeur/acheteur et le workflow de réservation.

## Architecture clé
- `manage.py` : point d'entrée Django.
- `core/settings.py` : configuration principale, notamment `MEDIA_ROOT`, `LOGIN_URL` et intégration de `PAYMEE` / `KONNECT`.
- `core/urls.py` : routes publiques et statiques.
- `annonces/models.py` : modèles métier, y compris `Profil`, `Produit`, `Reservation`, `Livraison`, `Transporteur`, `Categorie`, `SousCategorie`, `PhoneVerification`, `EmailVerification`.
- `annonces/views.py` : logique de catalogue, inscription, connexion, dépôt d'annonce, réservation, paiement et livraison.
- `annonces/forms.py` : formulaires d'inscription et de dépôt.
- `annonces/templates/annonces/` : vues HTML.

## Règles métier importantes
- Les coordonnées (`telephone`, `email`) du vendeur sont stockées dans `Profil` et ne doivent pas être exposées dans le catalogue public.
- Une réservation change le statut du produit en `reserve` et le retire du catalogue public.
- Seul l'administrateur peut consulter les réservations en détail et accéder aux informations de contact nécessaires.
- L'analyse IA des images est optionnelle et repose sur `google.cloud.vision` si `GOOGLE_APPLICATION_CREDENTIALS` est configuré.
- Vérification d'inscription : SMS ou email via `PhoneVerification` / `EmailVerification`.

## Environnement & exécution
- Utiliser l'environnement virtuel local `env/`.
- Commandes usuelles :
  - `python manage.py runserver`
  - `python manage.py makemigrations`
  - `python manage.py migrate`
  - `python manage.py createsuperuser`
- Variables d'environnement importantes :
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG`
  - `GOOGLE_APPLICATION_CREDENTIALS`
  - `PAYMEE_API_KEY`, `PAYMEE_API_SECRET`, `PAYMEE_BASE_URL`
  - `KONNECT_API_KEY`, `KONNECT_BASE_URL`, `KONNECT_RECEIVER_ID`

## Conventions de l'agent
- Répondre en français.
- Prioriser les modifications directes sur le code plutôt que des explications théoriques.
- Préserver l'architecture existante et les noms de fichiers actuels.
- Respecter les workflows de réservation et de confidentialité des données.
- Si un changement implique une nouvelle dépendance, vérifier d'abord l'impact sur l'environnement existant.

## Points de vigilance
- Le projet ne contient pas actuellement de documentation technique dédiée autre que `prompt.TXT`.
- `core/settings.py` utilise un secret codé en dur par défaut : ne pas exposer cela en production.
- L'analyse IA doit rester silencieuse si la configuration Google n'est pas disponible.
- Les routes doivent rester compatibles avec les noms existants (`accueil`, `inscription`, `connexion`, `deposer`, `reserver_produit`).

## Fichiers à vérifier en priorité
- `AGENTS.md` (instructions pour les agents)
- `prompt.TXT` (présentation métier existante)
- `core/settings.py`
- `annonces/models.py`
- `annonces/views.py`
- `annonces/forms.py`
- `annonces/admin.py`
- `annonces/templates/annonces/`
