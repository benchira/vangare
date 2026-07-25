import io
import os
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models

# TODO(commission): la note métier mentionne à la fois "7% côté vendeur" ET
# "0,7 TND de commission par commande" côté acheteur. Le code ci-dessous
# n'applique que le taux vendeur (7%). A confirmer avec Abdel avant mise en
# prod si les deux commissions doivent coexister.
COMMISSION_RATE = Decimal('0.07')

try:
    from google.cloud import vision
except ImportError:  # pragma: no cover - optional dependency for local development
    vision = None


def analyser_image_ia(chemin_absolu):
    if vision is None:
        return ""

    # Skip automatic IA tagging when Google credentials are not configured.
    if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        return ""

    try:
        client = vision.ImageAnnotatorClient()
        with io.open(chemin_absolu, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.label_detection(image=image)
        tags = [label.description for label in response.label_annotations if getattr(label, 'score', 0) > 0.70]
        return ", ".join(tags) if tags else ""
    except Exception:
        # Keep the app working even when Google Vision credentials are missing.
        return ""


class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    telephone = models.CharField(max_length=20)
    ville = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


class SousCategorie(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='sous_categories')
    nom = models.CharField(max_length=100)

    class Meta:
        unique_together = ('categorie', 'nom')

    def __str__(self):
        return self.nom


class Produit(models.Model):
    STATUTS = (('disponible', 'Disponible'), ('reserve', 'Réservé'))

    vendeur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='produits')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=3)
    image = models.ImageField(upload_to='photos_produits/')
    tags_ia = models.CharField(max_length=300, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='disponible')
    date_creation = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='produits')
    subcategory = models.ForeignKey(SousCategorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='produits')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and not self.tags_ia:
            chemin_image = self.image.path
            if os.path.exists(chemin_image):
                self.tags_ia = analyser_image_ia(chemin_image)
                super().save(update_fields=['tags_ia'])

    def __str__(self):
        return self.titre


class Reservation(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='reservations')
    acheteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    date_reservation = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False)
    prix_initial = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    frais_port = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    commission = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    prix_total = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    def save(self, *args, **kwargs):
        # BUGFIX: Decimal ne peut pas être multiplié par un float natif
        # (lève TypeError). Il faut passer par Decimal('...') partout.
        if not self.prix_initial and self.produit_id:
            self.prix_initial = self.produit.prix
        if not self.frais_port:
            # TODO(livraison): valeur provisoire tant que le vrai simulateur
            # de prix par transporteur (cf. spec métier) n'est pas branché
            # ici. Ne pas se fier à ce chiffre pour la mise en prod.
            self.frais_port = self.produit.prix * Decimal('0.0625')
        if not self.commission:
            self.commission = self.produit.prix * COMMISSION_RATE
        self.prix_total = self.prix_initial + self.frais_port + self.commission
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Réservation de {self.produit.titre}"


class Transporteur(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    actif = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Transporteur'
        verbose_name_plural = 'Transporteurs'

    def __str__(self):
        return self.nom


class Livraison(models.Model):
    STATUS_CHOICES = (
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    )

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='livraison')
    mode_paiement = models.CharField(max_length=50, default='cash_on_delivery')
    transporteur = models.ForeignKey(Transporteur, on_delete=models.SET_NULL, null=True, blank=True, related_name='livraisons')
    adresse = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    numero_suivi = models.CharField(max_length=100, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Livraison {self.reservation.id}"


class Conditions(models.Model):
    titre = models.CharField(max_length=200, default='Conditions d\'utilisation')
    slug = models.SlugField(max_length=200, unique=True)
    contenu = models.TextField(help_text='Contenu HTML des conditions')
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Conditions d\'utilisation'
        verbose_name_plural = 'Conditions d\'utilisation'

    def __str__(self):
        return self.titre


class PhoneVerification(models.Model):
    telephone = models.CharField(max_length=30, db_index=True)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Phone verification'
        verbose_name_plural = 'Phone verifications'

    def __str__(self):
        return f"{self.telephone} - {'VERIFIED' if self.verified else 'PENDING'}"


class EmailVerification(models.Model):
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Email verification'
        verbose_name_plural = 'Email verifications'

    def __str__(self):
        return f"{self.email} - {'VERIFIED' if self.verified else 'PENDING'}"
