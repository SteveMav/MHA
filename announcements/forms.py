from django import forms
from .models import Annonce


class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonce
        fields = [
            'titre',
            'type_annonce',
            'resume_seo',
            'message',
            'image',
            'date_debut',
            'date_fin',
            'lieu',
            'inscription_url',
            'cible',
        ]
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Ex: Session d'inscription U14 à Gombe"
            }),
            'type_annonce': forms.Select(attrs={'class': 'form-select'}),
            'resume_seo': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 180,
                'placeholder': "Résumé court pour Google et les partages."
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 7,
                'placeholder': "Décrivez l'annonce avec les informations pratiques: public, date, lieu, horaire, inscription."
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'date_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Terrain principal, Gombe, Kinshasa'}),
            'inscription_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'cible': forms.Select(attrs={'class': 'form-select'}),
        }

        labels = {
            'resume_seo': 'Résumé SEO',
            'type_annonce': "Type d'annonce",
            'date_debut': 'Date et heure de début',
            'date_fin': 'Date et heure de fin',
            'inscription_url': "Lien d'inscription",
        }
