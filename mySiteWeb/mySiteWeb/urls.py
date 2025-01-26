"""
URL configuration for monsiteweb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app1 import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accueil/', views.accueil, name='accueil'),
    path('choix-connexion/', views.choix_connexion, name='choix_connexion'),
    path('connexion_etu/', views.connexion_etu, name='connexion_etu'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/reservations/', views.admin_reservations, name='admin_reservations'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('compte/', views.compte, name='compte'),
    path('salles/', views.salles, name='salles'),
    path('confirmation/', views.confirmation, name='confirmation'),
]
