from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'client_nom',
            'client_prenom',
            'client_telephone',
            'client_email',
            'mode_retrait',
            'commune_kinshasa',
            'adresse_livraison',
            'mode_paiement',
            'reference_paiement',
            'notes_client',
        ]
        widgets = {
            'client_nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Lobaya'}),
            'client_prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Jean-Luc'}),
            'client_telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +243 810 000 000 (WhatsApp)'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: contact@email.com (facultatif)'}),
            'mode_retrait': forms.Select(attrs={'class': 'form-select', 'id': 'id_mode_retrait'}),
            'commune_kinshasa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Gombe, Ngaliema, Limete, etc.'}),
            'adresse_livraison': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro, Avenue, Référence'}),
            'mode_paiement': forms.Select(attrs={'class': 'form-select', 'id': 'id_mode_paiement'}),
            'reference_paiement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: ID de transaction du SMS Mobile Money'}),
            'notes_client': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Instructions particulières, taille souhaitée si non listée, etc.'}),
        }

    def clean_client_telephone(self):
        tel = self.cleaned_data.get('client_telephone', '').strip()
        if len(tel) < 8:
            raise forms.ValidationError("Veuillez saisir un numéro de téléphone valide pour vous contacter.")
        return tel


class OrderTrackingForm(forms.Form):
    numero_commande = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ex: MHA-A1B2C3'
        }),
        label="Numéro de commande"
    )
    telephone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Numéro utilisé lors de la commande'
        }),
        label="Numéro de téléphone"
    )
