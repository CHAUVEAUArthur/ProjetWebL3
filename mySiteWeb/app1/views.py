from django.shortcuts import HttpResponse
from django.shortcuts import render
from datetime import datetime, timedelta

# Create your views here.


def accueil(request):
    return render(request, "accueil.html")

def connexion(request):
    return render(request, "connexion.html")


def reservation(request):
    # Génération des heures par tranches de 15 minutes entre 8h30 et 19h
    debut = datetime.strptime("08:30", "%H:%M")
    fin = datetime.strptime("19:00", "%H:%M")
    heures = []

    while debut <= fin:
        heures.append(debut.strftime("%H:%M"))
        debut += timedelta(minutes=15)

    # Exemple de numéro étudiant à passer au template (remplacez par une donnée réelle)
    numero_etudiant = request.session.get('numero_etudiant', '00000000')  # Récupérer depuis session ou base

    return render(request, "reservation.html", {
        "heures": heures,
        "numero_etudiant": numero_etudiant,
    })
