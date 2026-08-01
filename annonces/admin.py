from urllib.parse import quote

from django.contrib import admin
from django.utils.html import format_html

from .models import Livraison, Produit, Profil, Reservation, Transporteur


def _whatsapp_number(tel):
    """Normalise un numéro tunisien vers le format attendu par wa.me
    (indicatif 216, chiffres uniquement, sans 0 initial ni +)."""
    digits = ''.join(ch for ch in (tel or '') if ch.isdigit())
    if digits.startswith('00216'):
        digits = digits[2:]
    if digits.startswith('216'):
        return digits
    if digits.startswith('0'):
        digits = digits[1:]
    return f'216{digits}' if digits else ''


def _whatsapp_link(tel, message):
    numero = _whatsapp_number(tel)
    if not numero:
        return '—'
    url = f'https://wa.me/{numero}?text={quote(message)}'
    return format_html('<a href="{}" target="_blank" rel="noopener">Contacter sur WhatsApp</a>', url)


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'telephone', 'ville')
    search_fields = ('user__username', 'telephone', 'ville')


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('titre', 'vendeur', 'prix', 'etat', 'poids_kg', 'statut', 'category', 'subcategory', 'date_creation')
    list_filter = ('statut', 'etat', 'date_creation', 'category', 'subcategory')
    search_fields = ('titre', 'description', 'vendeur__username')


@admin.register(Transporteur)
class TransporteurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'actif', 'prix_base', 'prix_par_kg', 'delai_estime')
    list_filter = ('actif',)
    search_fields = ('nom',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('produit', 'get_vendeur', 'get_telephone_vendeur', 'whatsapp_vendeur', 'acheteur', 'get_telephone_acheteur', 'whatsapp_acheteur', 'transporteur', 'frais_port', 'date_reservation', 'traite', 'get_statut')
    list_filter = ('traite', 'date_reservation')
    search_fields = ('produit__titre', 'produit__vendeur__username', 'acheteur__username')
    actions = ['marquer_comme_traite']

    def get_vendeur(self, obj):
        return obj.produit.vendeur.username

    def get_telephone_vendeur(self, obj):
        try:
            return obj.produit.vendeur.profil.telephone
        except Profil.DoesNotExist:
            return '—'

    def get_telephone_acheteur(self, obj):
        try:
            return obj.acheteur.profil.telephone
        except Profil.DoesNotExist:
            return '—'

    def whatsapp_vendeur(self, obj):
        message = (
            f'Bonjour, votre annonce "{obj.produit.titre}" a été réservée sur Vangare '
            f'(commande #{obj.id}). Merci de confirmer sa disponibilité pour qu\'on valide la vente.'
        )
        try:
            tel = obj.produit.vendeur.profil.telephone
        except Profil.DoesNotExist:
            tel = ''
        return _whatsapp_link(tel, message)

    def whatsapp_acheteur(self, obj):
        message = (
            f'Bonjour, votre réservation "{obj.produit.titre}" sur Vangare (commande #{obj.id}) '
            f'est en cours de validation. Nous revenons vers vous rapidement.'
        )
        try:
            tel = obj.acheteur.profil.telephone
        except Profil.DoesNotExist:
            tel = ''
        return _whatsapp_link(tel, message)

    def get_statut(self, obj):
        return 'Validée' if obj.traite else 'En attente de validation'

    def marquer_comme_traite(self, request, queryset):
        queryset.update(traite=True)

    marquer_comme_traite.short_description = "Marquer comme validée (contact WhatsApp effectué)"

    get_vendeur.short_description = 'Vendeur'
    get_telephone_vendeur.short_description = 'Téléphone vendeur'
    get_telephone_acheteur.short_description = 'Téléphone acheteur'
    whatsapp_vendeur.short_description = 'WhatsApp vendeur'
    whatsapp_acheteur.short_description = 'WhatsApp acheteur'
    get_statut.short_description = 'Statut'


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'mode_paiement', 'transporteur', 'statut', 'numero_suivi', 'date_creation')
    list_filter = ('statut', 'transporteur', 'mode_paiement')
    search_fields = ('reservation__produit__titre', 'numero_suivi')


from .models import Conditions


@admin.register(Conditions)
class ConditionsAdmin(admin.ModelAdmin):
    list_display = ('titre', 'slug', 'actif', 'date_modification')
    list_filter = ('actif',)
    search_fields = ('titre', 'slug')
    prepopulated_fields = { 'slug': ('titre',) }
