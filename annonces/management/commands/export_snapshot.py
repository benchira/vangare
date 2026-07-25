import os
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = 'Export a static snapshot of the public site to dist/snapshot.html'

    def handle(self, *args, **options):
        from annonces.models import Produit, Categorie, Transporteur, Conditions

        produits = Produit.objects.filter(statut='disponible').order_by('-date_creation')[:100]
        categories = Categorie.objects.prefetch_related('sous_categories').all()
        transporteurs = Transporteur.objects.filter(actif=True).order_by('nom')
        conditions = Conditions.objects.filter(actif=True).order_by('-date_modification').first()

        html = render_to_string('annonces/snapshot.html', {
            'produits': produits,
            'categories': categories,
            'transporteurs': transporteurs,
            'conditions': conditions,
        })

        out_dir = os.path.join(os.getcwd(), 'dist')
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'snapshot.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)

        self.stdout.write(self.style.SUCCESS(f'Wrote snapshot to {out_path}'))
