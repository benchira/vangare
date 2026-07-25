from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnnonceForm, InscriptionForm
from .models import Categorie, Livraison, Produit, Reservation, SousCategorie, Transporteur, Conditions, PhoneVerification, EmailVerification
from .sms import generate_code, send_sms
from .email import send_verification_email
from .payment import create_konnect_payment
from .delivery import create_aramex_shipment


def catalogue_public(request):
    produits = Produit.objects.filter(statut='disponible').order_by('-date_creation')
    categorie_id = request.GET.get('categorie')
    sous_categorie_id = request.GET.get('sous_categorie')
    query = request.GET.get('q', '').strip()

    if categorie_id:
        produits = produits.filter(category_id=categorie_id)
    if sous_categorie_id:
        produits = produits.filter(subcategory_id=sous_categorie_id)
    if query:
        produits = produits.filter(titre__icontains=query)

    categories = Categorie.objects.all()
    sous_categories = SousCategorie.objects.all()

    return render(request, 'annonces/catalogue.html', {
        'produits': produits,
        'categories': categories,
        'sous_categories': sous_categories,
        'selected_categorie': categorie_id,
        'selected_sous_categorie': sous_categorie_id,
        'query': query,
    })


def inscription_vendeur(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            identifiant = form.cleaned_data.get('identifiant')
            if identifiant == 'telephone':
                telephone = form.cleaned_data.get('telephone')
                # create verification code and send SMS
                code = generate_code(6)
                pv = PhoneVerification.objects.create(telephone=telephone, code=code)
                send_sms(telephone, f"Votre code de vérification: {code}")
                # store cleaned data in session until verification
                request.session['pending_signup'] = {
                    'telephone': telephone,
                    'password': form.cleaned_data.get('password'),
                    'ville': form.cleaned_data.get('ville'),
                }
                return render(request, 'annonces/verify_phone.html', {'telephone': telephone})
            elif identifiant == 'email':
                email = form.cleaned_data.get('email')
                code = generate_code(6)
                ev = EmailVerification.objects.create(email=email, code=code)
                send_verification_email(email, code)
                request.session['pending_signup'] = {
                    'email': email,
                    'password': form.cleaned_data.get('password'),
                    'ville': form.cleaned_data.get('ville'),
                }
                return render(request, 'annonces/verify_email.html', {'email': email})
            else:
                user = form.save()
                login(request, user)
                messages.success(request, 'Votre compte a été créé avec succès.')
                return redirect('accueil')
    else:
        form = InscriptionForm()
    return render(request, 'annonces/inscription.html', {'form': form})


def verify_phone_code(request):
    if request.method == 'POST':
        telephone = request.POST.get('telephone', '').strip()
        code = request.POST.get('code', '').strip()
        pending = request.session.get('pending_signup')
        if not pending or pending.get('telephone') != telephone:
            messages.error(request, 'Aucune inscription en attente pour ce numéro.')
            return redirect('inscription')

        try:
            pv = PhoneVerification.objects.filter(telephone=telephone, verified=False).order_by('-created_at').first()
        except PhoneVerification.DoesNotExist:
            pv = None

        if not pv or pv.code != code:
            messages.error(request, 'Code invalide.')
            return render(request, 'annonces/verify_phone.html', {'telephone': telephone})

        # mark verified and create user
        pv.verified = True
        pv.save(update_fields=['verified'])

        # create user from pending session
        from django.contrib.auth.models import User
        data = pending
        username = telephone
        password = data.get('password')
        ville = data.get('ville', '')
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Un compte existe déjà avec ce numéro.')
            return redirect('connexion')

        user = User.objects.create_user(username=username, password=password)
        from .models import Profil
        Profil.objects.create(user=user, telephone=telephone, ville=ville)
        login(request, user)
        # cleanup
        try:
            del request.session['pending_signup']
        except KeyError:
            pass
        messages.success(request, 'Votre compte a été créé et vérifié par SMS.')
        return redirect('accueil')
    return redirect('inscription')


def verify_email_code(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        code = request.POST.get('code', '').strip()
        pending = request.session.get('pending_signup')
        if not pending or pending.get('email') != email:
            messages.error(request, 'Aucune inscription en attente pour cet email.')
            return redirect('inscription')

        try:
            ev = EmailVerification.objects.filter(email=email, verified=False).order_by('-created_at').first()
        except EmailVerification.DoesNotExist:
            ev = None

        if not ev or ev.code != code:
            messages.error(request, 'Code invalide.')
            return render(request, 'annonces/verify_email.html', {'email': email})

        ev.verified = True
        ev.save(update_fields=['verified'])

        from django.contrib.auth.models import User
        data = pending
        username = email
        password = data.get('password')
        ville = data.get('ville', '')
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Un compte existe déjà avec cet email.')
            return redirect('connexion')

        user = User.objects.create_user(username=username, email=email, password=password)
        from .models import Profil
        Profil.objects.create(user=user, telephone=data.get('telephone',''), ville=ville)
        login(request, user)
        try:
            del request.session['pending_signup']
        except KeyError:
            pass
        messages.success(request, 'Votre compte a été créé et vérifié par email.')
        return redirect('accueil')
    return redirect('inscription')


def connexion_utilisateur(request):
    if request.method == 'POST':
        identifiant = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = None

        if identifiant:
            user = authenticate(request, username=identifiant, password=password)
            if user is None:
                user = authenticate(request, email=identifiant, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Bienvenue ! Vous êtes connecté.')
            return redirect('accueil')

        form = AuthenticationForm(request, data=request.POST)
        form.add_error(None, 'Identifiant ou mot de passe invalide.')
    else:
        form = AuthenticationForm()
    return render(request, 'annonces/connexion.html', {'form': form})


@login_required
def deposer_annonce(request):
    if request.method == 'POST':
        form = AnnonceForm(request.POST, request.FILES)
        if form.is_valid():
            annonce = form.save(commit=False)
            annonce.vendeur = request.user
            annonce.save()
            messages.success(request, 'Votre annonce a été publiée avec succès.')
            return redirect('accueil')
    else:
        form = AnnonceForm()
    return render(request, 'annonces/deposer.html', {'form': form})


@login_required
def reserver_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id, statut='disponible')
    reservation = None
    if request.user != produit.vendeur:
        produit.statut = 'reserve'
        produit.save(update_fields=['statut'])
        reservation = Reservation.objects.create(produit=produit, acheteur=request.user)
        messages.success(request, 'Réservation confirmée. L’annonce a été retirée du catalogue.')
    else:
        messages.info(request, 'Vous ne pouvez pas réserver votre propre annonce.')
    return render(request, 'annonces/confirmation.html', {'produit': produit, 'reservation': reservation})


@login_required
def initier_paiement(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == 'POST':
        provider = request.POST.get('provider', 'cash')
        # Cash on delivery (prioritaire)
        if provider == 'cash':
            if request.user != produit.vendeur:
                produit.statut = 'reserve'
                produit.save(update_fields=['statut'])
                reservation = Reservation.objects.create(produit=produit, acheteur=request.user)
                messages.success(request, 'Réservation confirmée. L’annonce a été retirée du catalogue.')
                return render(request, 'annonces/confirmation.html', {'produit': produit, 'reservation': reservation})
            else:
                messages.info(request, 'Vous ne pouvez pas réserver votre propre annonce.')
        # Konnect as the only online provider for now
        elif provider == 'konnect':
            return_url = request.build_absolute_uri('/').rstrip('/')
            try:
                response = create_konnect_payment(produit.prix, f'order-{produit.id}', f'Paiement pour {produit.titre}', return_url)
                return render(request, 'annonces/paiement.html', {'produit': produit, 'provider': provider, 'response': response})
            except Exception as exc:
                messages.error(request, f'Le paiement n’a pas pu être initié : {exc}')
    return render(request, 'annonces/paiement.html', {'produit': produit, 'provider': 'cash', 'response': None})


@login_required
def creer_livraison(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, acheteur=request.user)
    transporteurs = Transporteur.objects.filter(actif=True).order_by('nom')
    if request.method == 'POST':
        adresse = request.POST.get('adresse', '').strip()
        transporteur_id = request.POST.get('transporteur')
        transporteur = None
        if transporteur_id:
            transporteur = get_object_or_404(Transporteur, id=transporteur_id, actif=True)
        if not adresse:
            messages.error(request, 'Veuillez fournir une adresse de livraison.')
        elif not transporteur:
            messages.error(request, 'Veuillez sélectionner un transporteur actif.')
        else:
            livraison, created = Livraison.objects.get_or_create(
                reservation=reservation,
                defaults={
                    'mode_paiement': 'cash_on_delivery',
                    'transporteur': transporteur,
                    'adresse': adresse,
                }
            )
            if not created:
                livraison.adresse = adresse
                livraison.transporteur = transporteur
                livraison.save(update_fields=['adresse', 'transporteur'])
            try:
                response = create_aramex_shipment(f'order-{reservation.id}', adresse, reservation.acheteur.profil.telephone)
                livraison.numero_suivi = response.get('tracking_number', '')
                livraison.statut = 'en_cours'
                livraison.save(update_fields=['numero_suivi', 'statut'])
                messages.success(request, f'La livraison a été préparée avec {transporteur.nom}.')
            except Exception as exc:
                messages.error(request, f'La livraison n’a pas pu être créée : {exc}')
    return render(request, 'annonces/livraison.html', {'reservation': reservation, 'transporteurs': transporteurs})


def conditions(request):
    from .models import Conditions
    conditions = Conditions.objects.filter(actif=True).order_by('-date_modification').first()
    return render(request, 'annonces/conditions.html', {'conditions': conditions})


def site_snapshot(request):
    produits = Produit.objects.filter(statut='disponible').order_by('-date_creation')[:100]
    categories = Categorie.objects.prefetch_related('sous_categories').all()
    transporteurs = Transporteur.objects.filter(actif=True).order_by('nom')
    conditions = Conditions.objects.filter(actif=True).order_by('-date_modification').first()
    return render(request, 'annonces/snapshot.html', {
        'produits': produits,
        'categories': categories,
        'transporteurs': transporteurs,
        'conditions': conditions,
    })
