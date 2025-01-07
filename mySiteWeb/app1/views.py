from django.shortcuts import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from datetime import datetime, timedelta
from django.contrib.auth import logout
from django.contrib import messages

# Create your views here.


def accueil(request):
    return render(request, "accueil.html")

def connexion(request):
    return render(request, "connexion.html")

def process_login(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        username = request.POST['username']
        password = request.POST['password']
        
        # Authentification de l'utilisateur
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Connexion de l'utilisateur
            login(request, user)
            return redirect('reservation')  # Rediriger vers la page d'accueil après connexion réussie
        else:
            # Ajout d'un message d'erreur si l'authentification échoue
            messages.error(request, 'Identifiant ou mot de passe incorrect.')
    
    # Rendu du formulaire de connexion en cas d'échec ou de requête GET
    return render(request, 'connexion.html')

def reservation(request):
    # Génération des heures par tranches de 15 minutes entre 8h30 et 19h
    debut = datetime.strptime("08:30", "%H:%M")
    fin = datetime.strptime("18:30", "%H:%M")
    heures = []

    while debut <= fin:
        heures.append(debut.strftime("%H:%M"))
        debut += timedelta(minutes=30)

    # Utiliser l'identifiant de l'utilisateur connecté
    numero_etudiant = request.user.username

    return render(request, "reservation.html", {
        "heures": heures,
        "numero_etudiant": numero_etudiant,
    })


def deconnexion(request):
    logout(request)
    return redirect('accueil')

def salles(request):
    # Informations sur les salles
    salles = [
        {
            "nom": "Salle 1",
            "capacite_min": 2,
            "capacite_max": 4,
            "photo": "path/to/photo1.jpg"  # Remplacez par le chemin réel de la photo
        },
        {
            "nom": "Salle 2",
            "capacite_min": 2,
            "capacite_max": 4,
            "photo": "path/to/photo2.jpg"  # Remplacez par le chemin réel de la photo
        }
    ]

    return render(request, "salles.html", {
        "salles": salles,
    })


