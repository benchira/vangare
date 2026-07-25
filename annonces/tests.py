from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Categorie, Livraison, Produit, Reservation, SousCategorie, Transporteur


class CategorieModelTests(TestCase):
    def test_category_and_subcategory_linking(self):
        categorie = Categorie.objects.create(nom='Automobile')
        sous_categorie = SousCategorie.objects.create(categorie=categorie, nom='Pièces automobiles')

        self.assertEqual(sous_categorie.categorie, categorie)
        self.assertEqual(str(sous_categorie), 'Pièces automobiles')

    def test_product_can_store_category_and_subcategory(self):
        vendeur = User.objects.create_user(username='vendeur', password='secret123')
        categorie = Categorie.objects.create(nom='Vêtements')
        sous_categorie = SousCategorie.objects.create(categorie=categorie, nom='Chaussures')

        produit = Produit.objects.create(
            vendeur=vendeur,
            titre='Basket occasion',
            description='Basket en bon état',
            prix='50.000',
            image='dummy.jpg',
            category=categorie,
            subcategory=sous_categorie,
        )

        self.assertEqual(produit.category, categorie)
        self.assertEqual(produit.subcategory, sous_categorie)

    def test_delivery_company_can_be_created_and_linked_to_a_delivery(self):
        vendeur = User.objects.create_user(username='vendeur2', password='secret123')
        acheteur = User.objects.create_user(username='acheteur2', password='secret123')
        categorie = Categorie.objects.create(nom='Électronique')
        produit = Produit.objects.create(
            vendeur=vendeur,
            titre='Téléphone',
            description='Bon état',
            prix='100.000',
            image='dummy.jpg',
            category=categorie,
        )
        reservation = Reservation.objects.create(produit=produit, acheteur=acheteur)
        transporteur = Transporteur.objects.create(nom='FastHaul', actif=True)
        livraison = Livraison.objects.create(reservation=reservation, transporteur=transporteur, adresse='Tunis')

        self.assertEqual(livraison.transporteur, transporteur)
        self.assertEqual(str(transporteur), 'FastHaul')

    def test_reservation_price_includes_shipping_and_commission(self):
        vendeur = User.objects.create_user(username='vendeur3', password='secret123')
        acheteur = User.objects.create_user(username='acheteur3', password='secret123')
        categorie = Categorie.objects.create(nom='Maison')
        produit = Produit.objects.create(
            vendeur=vendeur,
            titre='Table',
            description='Table en bon état',
            prix='80.000',
            image='dummy.jpg',
            category=categorie,
        )

        reservation = Reservation.objects.create(produit=produit, acheteur=acheteur)

        self.assertEqual(reservation.prix_initial, Decimal('80.000'))
        self.assertEqual(reservation.frais_port, Decimal('5.000'))
        self.assertEqual(reservation.commission, Decimal('5.600'))
        self.assertEqual(reservation.prix_total, Decimal('90.600'))
