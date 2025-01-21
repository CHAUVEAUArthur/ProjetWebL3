import random
import string
from django.shortcuts import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django import forms
from django.utils import timezone
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Create your views here.


@login_required
def mon_compte(request):
    # Exemple de données de réservations
    reservations = [
        {
            "salle": "Salle 1",
            "date": "2023-10-10",
            "heure_debut": "09:00",
            "heure_fin": "10:00",
            "status": "Passée"
        },
        {
            "salle": "Salle 2",
            "date": "2023-11-15",
            "heure_debut": "11:00",
            "heure_fin": "12:00",
            "status": "À venir"
        }
    ]
    return render(request, 'mon_compte.html', {'reservations': reservations})

def accueil(request):
    return render(request, "accueil.html")

class EmailForm(forms.Form):
    email = forms.EmailField()

class CodeForm(forms.Form):
    code_confirmation = forms.CharField(max_length=4)

def generate_confirmation_code():
    return ''.join(random.choices('0123456789', k=4))

def extract_student_number(email):
    return email.split('@')[0]

def connexion(request):
    if request.method == "POST":
        if 'email' in request.POST:
            email = request.POST.get('email')
            code_confirmation = generate_confirmation_code()
            student_number = extract_student_number(email)
            request.session['code_confirmation'] = code_confirmation
            request.session['email'] = email
            request.session['student_number'] = student_number
            request.session['tentatives_restantes'] = 3  # Initialiser le nombre de tentatives
            request.session['bloque_jusqu_a'] = None  # Réinitialiser le blocage

            # Envoyer le code par email
            send_mail(
                'Votre code de confirmation',
                f'Votre code de confirmation est : {code_confirmation}',
                'votre_adresse_email@example.com',  # Remplacez par l'adresse email de l'expéditeur
                [email],
                fail_silently=False,
            )

            return render(request, "connexion.html", {'email_sent': True})
        elif 'code_confirmation' in request.POST:
            code_saisi = request.POST.get('code_confirmation')
            code_envoye = request.session.get('code_confirmation')
            email = request.session.get('email')
            tentatives_restantes = request.session.get('tentatives_restantes', 0)

            if code_saisi == code_envoye:
                # Code correct, connexion réussie
                return redirect('reservation')  # Redirige vers la vue nommée 'reservation'
            else:
                # Code incorrect, décrémenter le nombre de tentatives
                tentatives_restantes -= 1
                request.session['tentatives_restantes'] = tentatives_restantes

                if tentatives_restantes > 0:
                    # Afficher un message d'erreur et permettre une nouvelle tentative
                    return render(request, "connexion.html", {
                        'email_sent': True,
                        'error_message': f"Code de confirmation incorrect. Il vous reste {tentatives_restantes} tentatives."
                    })
                else:
                    # Bloquer l'utilisateur après 3 tentatives incorrectes
                    request.session['bloque_jusqu_a'] = (timezone.now() + timedelta(minutes=1)).isoformat()
                    return render(request, "bloque.html", {
                        'minutes': 1,
                        'seconds': 0,
                        'bloque_jusqu_a': (timezone.now() + timedelta(minutes=1)).isoformat()
                    })
    else:
        return render(request, "connexion.html")

def reservation(request):
    # Génération des heures par tranches de 15 minutes entre 8h30 et 18h30
    debut = datetime.strptime("08:30", "%H:%M")
    fin = datetime.strptime("18:30", "%H:%M")
    heures = []

    while debut <= fin:
        heures.append(debut.strftime("%H:%M"))
        debut += timedelta(minutes=30)

    # Exemple de numéro étudiant à passer au template (remplacez par une donnée réelle)
    numero_etudiant = request.session.get('numero_etudiant', '00000000')  # Récupérer depuis session ou base

    return render(request, "reservation.html", {
        "heures": heures,
        "numero_etudiant": numero_etudiant,
    })

def deconnexion(request):
    logout(request)
    return redirect('accueil')


def salles(request):
    hours = ['08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00']  
    
    if request.method == "POST":
        date = request.POST.get('date')
        heure_debut = request.POST.get('heure_debut')
        heure_fin = request.POST.get('heure_fin')

        # Logique pour récupérer les salles disponibles en fonction de la date et des heures
        # Exemple de données de salles disponibles
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
            "date": date,
            "heure_debut": heure_debut,
            "heure_fin": heure_fin,
            "salles": salles,
            "hours": hours,
        })
    else:
        return render(request, "salles.html", {
            "hours": hours,
        })