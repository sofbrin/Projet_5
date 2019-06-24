from django.shortcuts import render

from django.http import HttpResponse


def index(request):
    return HttpResponse("Vous êtes sur votre page. Tapez 1 pour afficher la liste des substituts, 2 pour rechercher un substitut")
