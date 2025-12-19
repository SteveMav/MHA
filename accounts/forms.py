from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile, Abonnement

class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(label="Prénom", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Nom", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    # Profile fields
    date_naissance = forms.DateField(label="Date de naissance", widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    telephone = forms.CharField(label="Numéro WhatsApp", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.username = self.cleaned_data["email"] # Use email as username
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                date_naissance=self.cleaned_data["date_naissance"],
                telephone=self.cleaned_data["telephone"]
            )
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Email", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        # We exclude username from the form display if we don't want them to change it, 
        # or we can make it readonly. For now, let's just use email, first_name, last_name 
        # as per standard profile updates.
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['telephone', 'adresse', 'date_naissance', 'photo', 'ecole_frequente', 'niveau', 'taille', 'poids', 'poste_prefer', 'contact_parent']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'ecole_frequente': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau': forms.TextInput(attrs={'class': 'form-control'}),
            'taille': forms.NumberInput(attrs={'class': 'form-control'}),
            'poids': forms.NumberInput(attrs={'class': 'form-control'}),
            'poste_prefer': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_parent': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AbonnementForm(forms.ModelForm):
    class Meta:
        model = Abonnement
        fields = ['moyen_paiement', 'telephone_paiement']
        widgets = {
            'moyen_paiement': forms.Select(attrs={'class': 'form-select'}),
            'telephone_paiement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +243...'}),
        }
        labels = {
            'moyen_paiement': 'Moyen de paiement',
            'telephone_paiement': 'Numéro pour le paiement'
        }
