from django.contrib import admin

from .models import Livraison, Produit, Profil, Reservation, Transporteur


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'telephone', 'ville')
    search_fields = ('user__username', 'telephone', 'ville')


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('titre', 'vendeur', 'prix', 'statut', 'category', 'subcategory', 'date_creation')
    list_filter = ('statut', 'date_creation', 'category', 'subcategory')
    search_fields = ('titre', 'description', 'vendeur__username')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('produit', 'get_vendeur', 'get_telephone_vendeur', 'acheteur', 'get_telephone_acheteur', 'date_reservation', 'traite', 'get_statut')
    list_filter = ('traite', 'date_reservation')
    search_fields = ('produit__titre', 'produit__vendeur__username', 'acheteur__username')
    actions = ['marquer_comme_traite']

    def get_vendeur(self, obj):
        return obj.produit.vendeur.username

    def get_telephone_vendeur(self, obj):
        return obj.produit.vendeur.profil.telephone

    def get_telephone_acheteur(self, obj):
        return obj.acheteur.profil.telephone

    def get_statut(self, obj):
        return 'Traité' if obj.traite else 'En attente'

    def marquer_comme_traite(self, request, queryset):
        queryset.update(traite=True)

    marquer_comme_traite.short_description = 'Marquer comme traité'

    get_vendeur.short_description = 'Vendeur'
    get_telephone_vendeur.short_description = 'Téléphone vendeur'
    get_telephone_acheteur.short_description = 'Téléphone acheteur'
    get_statut.short_description = 'Statut'


@admin.register(Transporteur)
class TransporteurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'actif', 'description')
    list_filter = ('actif',)
    search_fields = ('nom',)


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
