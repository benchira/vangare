"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from annonces import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.catalogue_public, name='accueil'),
    path('inscription/', views.inscription_vendeur, name='inscription'),
    path('verify_phone/', views.verify_phone_code, name='verify_phone'),
    path('verify_email/', views.verify_email_code, name='verify_email'),
    path('connexion/', views.connexion_utilisateur, name='connexion'),
    path('deposer/', views.deposer_annonce, name='deposer'),
    path('acheter/<int:produit_id>/', views.reserver_produit, name='reserver_produit'),
    path('paiement/<int:produit_id>/', views.initier_paiement, name='initier_paiement'),
    path('livraison/<int:reservation_id>/', views.creer_livraison, name='creer_livraison'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('conditions/', views.conditions, name='conditions'),
    path('snapshot/', views.site_snapshot, name='snapshot'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
