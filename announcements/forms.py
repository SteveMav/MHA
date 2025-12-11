from django import forms
from .models import Annonce

class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonce
        fields = ['titre', 'message', 'image', 'cible']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l\'annonce'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contenu de l\'annonce'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'cible': forms.Select(attrs={'class': 'form-select'}),
        }
