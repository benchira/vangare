from django import forms
from django.contrib.auth.models import User

from .models import Categorie, Produit, Profil, SousCategorie


class InscriptionForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    email = forms.EmailField(label="Email", required=False)
    telephone = forms.CharField(max_length=20, label="Téléphone", required=False)
    identifiant = forms.ChoiceField(
        choices=[('telephone', 'Téléphone'), ('email', 'Email')],
        widget=forms.RadioSelect,
        label='Méthode d’identification'
    )
    ville = forms.CharField(max_length=100, label="Ville")

    class Meta:
        model = User
        fields = ['email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        telephone = cleaned_data.get('telephone')
        identifiant = cleaned_data.get('identifiant')

        if identifiant == 'telephone' and not telephone:
            self.add_error('telephone', 'Le téléphone est requis si vous choisissez cette méthode.')
        if identifiant == 'email' and not email:
            self.add_error('email', 'L’email est requis si vous choisissez cette méthode.')

        if email:
            cleaned_data['email'] = email.strip().lower()
        if telephone:
            cleaned_data['telephone'] = telephone.strip()

        return cleaned_data

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone and User.objects.filter(username__iexact=telephone).exists():
            raise forms.ValidationError('Ce numéro de téléphone est déjà utilisé.')
        return telephone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Cet email est déjà utilisé.')
        return email

    def save(self, commit=True):
        identifiant = self.cleaned_data['identifiant']
        email = self.cleaned_data.get('email')
        telephone = self.cleaned_data.get('telephone')
        user = super().save(commit=False)
        user.username = (telephone if identifiant == 'telephone' else email).strip()
        user.email = (email or '').strip().lower()
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        Profil.objects.get_or_create(
            user=user,
            defaults={'telephone': telephone or '', 'ville': self.cleaned_data['ville']}
        )
        return user


class AnnonceForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Categorie.objects.all(), required=False, label='Catégorie')
    subcategory = forms.ModelChoiceField(queryset=SousCategorie.objects.none(), required=False, label='Sous-catégorie')

    class Meta:
        model = Produit
        fields = ['titre', 'description', 'prix', 'image', 'category', 'subcategory']
        labels = {
            'titre': 'Titre',
            'description': 'Description',
            'prix': 'Prix (TND)',
            'image': 'Photo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.data.get('category'):
            self.fields['subcategory'].queryset = SousCategorie.objects.filter(categorie_id=self.data.get('category'))
        elif self.instance.pk and self.instance.category_id:
            self.fields['subcategory'].queryset = SousCategorie.objects.filter(categorie_id=self.instance.category_id)
        else:
            self.fields['subcategory'].queryset = SousCategorie.objects.none()
