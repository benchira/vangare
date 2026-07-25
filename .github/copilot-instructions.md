## Projet
Marketplace Django ciblant le marché tunisien. Application principale : `annonces`.

## Ce que doit faire l'agent
- Conserver la logique métier existante.
- Masquer les coordonnées des vendeurs dans le catalogue public.
- Préserver le workflow de réservation : produit disponible → réservé → ticket de réservation.
- Ne pas réécrire l'architecture principale sans raison.

## Points importants
- Le projet utilise Django 6.0 et SQLite localement.
- Le code existe déjà pour l'inscription, le dépôt d'annonce, la réservation, le paiement et la livraison.
- L'IA image est optionnelle : `google.cloud.vision` doit rester silencieux si `GOOGLE_APPLICATION_CREDENTIALS` est absent.
- Les variables d'environnement utiles : `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `GOOGLE_APPLICATION_CREDENTIALS`, `PAYMEE_*`, `KONNECT_*`.

## Fichiers clés
- `core/settings.py`
- `core/urls.py`
- `annonces/models.py`
- `annonces/views.py`
- `annonces/forms.py`
- `annonces/admin.py`
- `annonces/templates/annonces/`

## Style
- Répondre en français.
- Préférer les solutions directement applicables.
- Suggérer des changements compatibles avec le code existant.
