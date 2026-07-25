from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed the database with marketplace categories and subcategories (LeBonCoin-like)'

    def handle(self, *args, **options):
        from annonces.models import Categorie, SousCategorie

        categories_data = {
            'Immobilier': ['Ventes immobilières', 'Locations', 'Colocations', 'Terrains'],
            'Véhicules': ['Voitures', 'Motos', 'Utilitaires', 'Camping-cars', 'Pièces détachées'],
            'Multimédia': ['Téléphones', 'Informatique', 'Image & Son', 'Consoles', 'Jeux vidéo'],
            'Maison': ['Meubles', 'Electroménager', 'Décoration', 'Bricolage'],
            'Mode': ['Vêtements', 'Chaussures', 'Accessoires'],
            'Bébé': ['Vêtements bébé', 'Poussettes', 'Sièges auto', 'Puériculture'],
            'Animaux': ['Chiens', 'Chats', 'Rongeurs', 'Accessoires animaux'],
            'Loisirs': ['Sports', 'Instruments de musique', 'Billets', 'Collections'],
            'Emploi': ['Offres d\'emploi', 'Demandes d\'emploi', 'Services à la personne'],
            'Services': ['Bricolage', 'Jardinage', 'Cours particuliers', 'Événementiel'],
            'Matériel professionnel': ['Agriculture', 'Restauration', 'BTP', 'Matériel médical'],
            'Art & Antiquités': ['Tableaux', 'Arts de la table', 'Antiquités'],
        }

        created = 0
        for cat_name, subs in categories_data.items():
            category, _ = Categorie.objects.get_or_create(nom=cat_name)
            for sub in subs:
                sc, _ = SousCategorie.objects.get_or_create(categorie=category, nom=sub)
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Seeded {created} categories (with subcategories)'))
