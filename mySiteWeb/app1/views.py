import random
import string
from django.shortcuts import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django import forms
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Reservation, Admin

from django.contrib.auth.models import User
from django import forms


# Create your views here.

class EmailForm(forms.Form):
    email = forms.EmailField()

class CodeForm(forms.Form):
    code_confirmation = forms.CharField(max_length=4)


class AdminLoginForm(forms.Form):
    username = forms.CharField(label='Identifiant', max_length=100)
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)


def accueil(request):
    if request.user.is_authenticated:
        # Définir les quotas
        QUOTA_JOURNALIER = 3  # en heures
        QUOTA_HEBDOMADAIRE = 15  # en heures
        QUOTA_MENSUEL = 75  # en heures

        now = timezone.now()
        start_of_day = datetime.combine(now.date(), datetime.min.time())
        start_of_week = start_of_day - timedelta(days=now.weekday())
        start_of_month = start_of_day.replace(day=1)

        daily_reservations = Reservation.objects.filter(user=request.user, start_time__gte=start_of_day, end_time__lte=now)
        weekly_reservations = Reservation.objects.filter(user=request.user, start_time__gte=start_of_week, end_time__lte=now)
        monthly_reservations = Reservation.objects.filter(user=request.user, start_time__gte=start_of_month, end_time__lte=now)

        daily_hours = sum((res.end_time - res.start_time).total_seconds() / 3600 for res in daily_reservations)
        weekly_hours = sum((res.end_time - res.start_time).total_seconds() / 3600 for res in weekly_reservations)
        monthly_hours = sum((res.end_time - res.start_time).total_seconds() / 3600 for res in monthly_reservations)

        daily_quota_remaining = QUOTA_JOURNALIER - daily_hours
        weekly_quota_remaining = QUOTA_HEBDOMADAIRE - weekly_hours
        monthly_quota_remaining = QUOTA_MENSUEL - monthly_hours

        context = {
            "daily_quota_remaining": daily_quota_remaining,
            "weekly_quota_remaining": weekly_quota_remaining,
            "monthly_quota_remaining": monthly_quota_remaining,
        }
    else:
        context = {}

    return render(request, "accueil.html", context)



def choix_connexion(request):
    return render(request, 'choix_connexion.html')


def generate_confirmation_code():
    return ''.join(random.choices('0123456789', k=4))

def extract_student_number(email):
    return email.split('@')[0]

def connexion_etu(request):
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
                subject="Votre code de confirmation",
                message=f"Votre code de confirmation est : {code_confirmation}\n\nBibliothèque de l'UFR SEGMI \nBatiment Allais (G), salle 113 \nTel accueil : 01 40 97 78 68",
                from_email='hsnja03@gmail.com',           
                recipient_list=[email],
            )

            return render(request, "connexion_etu.html", {'email_sent': True, 'email': email})
        elif 'code_confirmation' in request.POST:
            code_saisi = request.POST.get('code_confirmation')
            code_envoye = request.session.get('code_confirmation')
            email = request.session.get('email')
            tentatives_restantes = request.session.get('tentatives_restantes', 0)

            if code_saisi == code_envoye:
                # Code correct, connexion réussie
                user, created = User.objects.get_or_create(username=email, defaults={'email': email})
                login(request, user)
                return redirect('salles')  # Redirige vers la vue nommée 'salles'
            else:
                # Code incorrect, décrémenter le nombre de tentatives
                tentatives_restantes -= 1
                request.session['tentatives_restantes'] = tentatives_restantes

                if tentatives_restantes > 0:
                    # Afficher un message d'erreur et permettre une nouvelle tentative
                    return render(request, "connexion_etu.html", {
                        'email_sent': True,
                        'email': email,
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
        return render(request, "connexion_etu.html", {'email_sent': False})

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and isinstance(user, Admin):
                login(request, user)
                return redirect('admin_reservations')
            else:
                messages.error(request, 'Identifiant ou mot de passe incorrect.')
    else:
        form = AdminLoginForm()
    return render(request, 'admin_login.html', {'form': form})

def deconnexion(request):
    logout(request)
    return redirect('accueil')

@login_required
def admin_reservations(request):
    if not isinstance(request.user, Admin):
        return redirect('accueil')
    reservations = Reservation.objects.all().order_by('-start_time')
    return render(request, 'admin_reservations.html', {'reservations': reservations})


@login_required
def salles(request):
    hours = ['08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00']  
    
    # Définir les quotas
    QUOTA_JOURNALIER = 3  # en heures
    QUOTA_HEBDOMADAIRE = 15  # en heures
    QUOTA_MENSUEL = 75  # en heures

    now = timezone.now()
    start_of_day = datetime.combine(now.date(), datetime.min.time())
    start_of_week = start_of_day - timedelta(days=now.weekday())
    start_of_month = start_of_day.replace(day=1)

    daily_reservations = Reservation.objects.filter(user=request.user, start_time__gte=start_of_day, end_time__lte=now)
    weekly_reservations = Reservation.objects.filter(user=request.user, start_time__gte=start_of_week, end_time__lte=now)
    monthly_reservations = Reservation.objects.filter(user=request.user, start_time__gte=start_of_month, end_time__lte=now)

    daily_hours = sum((res.end_time - res.start_time).total_seconds() / 3600 for res in daily_reservations)
    weekly_hours = sum((res.end_time - res.start_time).total_seconds() / 3600 for res in weekly_reservations)
    monthly_hours = sum((res.end_time - res.start_time).total_seconds() / 3600 for res in monthly_reservations)

    daily_quota_remaining = QUOTA_JOURNALIER - daily_hours
    weekly_quota_remaining = QUOTA_HEBDOMADAIRE - weekly_hours
    monthly_quota_remaining = QUOTA_MENSUEL - monthly_hours

    if request.method == "POST":
        try:
            start_time = request.POST.get('startTime')
            end_time = request.POST.get('endTime')
            participants = request.POST.get('participants')
            participant1 = request.POST.get('participant1')
            participant2 = request.POST.get('participant2')
            participant3 = request.POST.get('participant3', '')
            participant4 = request.POST.get('participant4', '')
            terms = request.POST.get('terms') == 'on'
            room = request.POST.get('room')  # Récupérer la salle sélectionnée
            date_str = request.POST.get('date')  # Récupérer la date sélectionnée

            # Convertir les heures en objets datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()  # Utilisez la date sélectionnée
            start_time = timezone.make_aware(datetime.combine(date, datetime.strptime(start_time, '%H:%M').time()))
            end_time = timezone.make_aware(datetime.combine(date, datetime.strptime(end_time, '%H:%M').time()))

            # Calculer la durée de la réservation en heures
            reservation_duration = (end_time - start_time).total_seconds() / 3600

            # Vérifier les quotas
            if daily_hours + reservation_duration > QUOTA_JOURNALIER:
                messages.error(request, f"Vous avez dépassé le quota quotidien de {QUOTA_JOURNALIER} heures.")
            elif weekly_hours + reservation_duration > QUOTA_HEBDOMADAIRE:
                messages.error(request, f"Vous avez dépassé le quota hebdomadaire de {QUOTA_HEBDOMADAIRE} heures.")
            elif monthly_hours + reservation_duration > QUOTA_MENSUEL:
                messages.error(request, f"Vous avez dépassé le quota mensuel de {QUOTA_MENSUEL} heures.")
            else:
                # Vérifier si le créneau est déjà réservé
                if Reservation.objects.filter(room=room, start_time__lt=end_time, end_time__gt=start_time).exists():
                    messages.error(request, "Ce créneau est déjà réservé.")
                else:
                    Reservation.objects.create(
                        user=request.user,
                        start_time=start_time,
                        end_time=end_time,
                        room=room,  # Utiliser la salle sélectionnée
                        participants=participants,
                        participant1=participant1,
                        participant2=participant2,
                        participant3=participant3,
                        participant4=participant4,
                        terms=terms
                    )
                    messages.success(request, "Votre réservation a bien été enregistrée. Vous pouvez consulter vos réservations dans l'onglet Mes Réservations, sinon retournez à l'accueil.")
                    return redirect('confirmation')  # Rediriger vers la même page pour actualiser les quotas
        except Exception as e:
            messages.error(request, f"Une erreur est survenue lors de la réservation. Veuillez réessayer. Erreur: {str(e)}")

    return render(request, "salles.html", {
        "hours": hours,
        "daily_quota_remaining": daily_quota_remaining,
        "weekly_quota_remaining": weekly_quota_remaining,
        "monthly_quota_remaining": monthly_quota_remaining,
    })

@login_required
def compte(request):
    # Définir les quotas
    QUOTA_JOURNALIER = 3  # en heures
    QUOTA_HEBDOMADAIRE = 15  # en heures
    QUOTA_MENSUEL = 75  # en heures

    now = timezone.now()
    start_of_day = datetime.combine(now.date(), datetime.min.time())
    start_of_week = start_of_day - timedelta(days=now.weekday())
    start_of_month = start_of_day.replace(day=1)

    daily_reservations = Reservation.objects.filter(user=request.user, start_time__gte=start_of_day, end_time__lte=now)
    weekly_reservations = Reservation.objects.filter(user=request.user, start_time__gte=start_of_week, end_time__lte=now)
    monthly_reservations = Reservation.objects.filter(user=request.user, start_time__gte=start_of_month, end_time__lte=now)

    daily_hours = sum((res.end_time - res.start_time).total_seconds() / 3600 for res in daily_reservations)
    weekly_hours = sum((res.end_time - res.start_time).total_seconds() / 3600 for res in weekly_reservations)
    monthly_hours = sum((res.end_time - res.start_time).total_seconds() / 3600 for res in monthly_reservations)

    daily_quota_remaining = QUOTA_JOURNALIER - daily_hours
    weekly_quota_remaining = QUOTA_HEBDOMADAIRE - weekly_hours
    monthly_quota_remaining = QUOTA_MENSUEL - monthly_hours

    reservations = Reservation.objects.filter(user=request.user).order_by('-start_time')

    context = {
        "reservations": reservations,
        "daily_quota_remaining": daily_quota_remaining,
        "weekly_quota_remaining": weekly_quota_remaining,
        "monthly_quota_remaining": monthly_quota_remaining,
    }

    return render(request, "compte.html", context)


def confirmation(request):
    return render(request, "confirmation.html")
