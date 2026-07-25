from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Categorie, SousCategorie


@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    categories_data = {
        'Automobile': ['Pièces automobiles', 'Accessoires automobile', 'Électronique auto'],
        'Vêtements': ['Hauts', 'Pantalons', 'Chaussures', 'Accessoires'],
        'Déco': ['Meubles', 'Décoration', 'Luminaires'],
    }

    for category_name, subcategories in categories_data.items():
        category, _ = Categorie.objects.get_or_create(nom=category_name)
        for sub_name in subcategories:
            SousCategorie.objects.get_or_create(categorie=category, nom=sub_name)


@receiver(post_migrate)
def create_default_conditions(sender, **kwargs):
    from .models import Conditions

    default_slug = 'conditions-generales'
    if not Conditions.objects.filter(slug=default_slug).exists():
        contenu = '''
<h2>Article 1 — Prix</h2>
<p>Les prix affichés sur le site sont en Dinar tunisien (TND) et incluent toutes taxes applicables sauf indication contraire. Le vendeur déclare le prix de vente au moment de la publication de l'annonce.</p>

<h2>Article 2 — Commande</h2>
<p>La commande s'effectue par la réservation de l'annonce par l'acheteur via le bouton de réservation. La validation de la réservation crée un ticket de réservation et bloque l'annonce (statut «Réservé»).</p>

<h2>Article 3 — Validation</h2>
<p>La réservation est validée automatiquement lors de la confirmation par l'acheteur. Le vendeur et l'acheteur sont informés par le système et peuvent ensuite organiser la livraison et le paiement.</p>

<h2>Article 5 — Paiement</h2>
<p>Le paiement peut être effectué en ligne via Konnect (si activé) ou en espèces à la livraison (cash on delivery). En cas de paiement en ligne, les conditions du prestataire s'appliquent.</p>

<h2>Article 6 — Sécurisation</h2>
<p>Nous mettons en œuvre des mesures raisonnables pour protéger les données des utilisateurs (chiffrement des cookies, bonnes pratiques de mot de passe). Les informations sensibles (clés API) sont stockées en variables d'environnement côté serveur.</p>

<h2>Article 7 — Livraison</h2>
<p>La livraison est organisée par le vendeur ou un transporteur choisi via notre interface. Les frais de port sont à la charge de l'acheteur sauf accord contraire. En cas de litige sur la livraison, les parties sont invitées à contacter le support.</p>
'''
        Conditions.objects.create(titre="Conditions d'utilisation", slug=default_slug, contenu=contenu, actif=True)
