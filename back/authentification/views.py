from django.shortcuts import render

# Create your views here.
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

# views.py

from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.groups.filter(name='Administrateurs').exists()

def is_fournisseur(user):
    return user.groups.filter(name='Fournisseurs').exists()

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'Home.html')

@login_required
@user_passes_test(is_fournisseur)
def fournisseur_dashboard(request):
    return render(request, 'Home.html')

def logout_view(request):
    """Déconnecter l'utilisateur et le rediriger vers la page de connexion."""
    logout(request)
    return redirect('login')  # Redirige vers la page de connexion (ou toute autre page)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authentifier l'utilisateur
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Vérification du groupe de l'utilisateur
                if user.groups.filter(name='Administrateurs').exists():
                    return redirect('home')  # Rediriger vers le tableau de bord des administrateurs
                elif user.groups.filter(name='Fournisseurs').exists():
                    return redirect('home')  # Rediriger vers le tableau de bord des fournisseurs
                else:
                    return redirect('home')  # Rediriger vers la page d'accueil ou un autre endroit si nécessaire

            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Erreur de formulaire. Assurez-vous que tous les champs sont valides.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})