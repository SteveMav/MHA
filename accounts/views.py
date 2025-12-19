from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, LoginForm, UserUpdateForm, ProfileUpdateForm, AbonnementForm
from django.utils import timezone
from datetime import timedelta
import uuid

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile') # Redirect to profile after login
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def profile_view(request):
    user = request.user
    
    # Get current active or last subscription
    current_subscription = user.abonnements.order_by('-date_fin').first()
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user.profile)
            a_form = AbonnementForm() # Empty form if just updating profile
            
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                return redirect('profile')
                
        elif 'pay_subscription' in request.POST:
            u_form = UserUpdateForm(instance=user)
            p_form = ProfileUpdateForm(instance=user.profile)
            a_form = AbonnementForm(request.POST)
            
            if a_form.is_valid():
                abonnement = a_form.save(commit=False)
                abonnement.membre = user
                abonnement.montant = 10.00 # Example fixed amount or based on selection
                abonnement.date_debut = timezone.now().date()
                abonnement.date_fin = timezone.now().date() + timedelta(days=30)
                abonnement.statut = 'en_attente' # Default to pending until confirmed
                # Auto-generate transaction ID
                abonnement.transaction_id = f"MHA-{uuid.uuid4().hex[:8].upper()}"
                abonnement.save()
                return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=user.profile)
        a_form = AbonnementForm()

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'a_form': a_form,
        'subscription': current_subscription
    }
    return render(request, 'accounts/profile.html', context)
